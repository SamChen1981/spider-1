#encoding=utf8
"Utilities for loading models and the modules that contain them."
from sqlalchemy.ext.declarative import declarative_base


from spider.core.exceptions import ImproperlyConfigured
from spider.utils.datastructures import SortedDict
from spider.utils.importlib import import_module
from spider.utils.module_loading import module_has_submodule
from spider.utils._os import upath
from spider.utils import six
from spider.conf import settings
import imp
import sys
import os

__all__ = ('get_apps', 'get_app', 'get_models', 'get_model', 'register_models',
        'load_app', 'app_cache_ready')


class AppCache(object):
    """
    A cache that stores installed applications and their models. Used to
    provide reverse-relations and for app introspection (e.g. admin).
    """
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state = dict(
        # Keys of app_store are the model modules for each application.
        app_store=SortedDict(),

        # Mapping of installed app_labels to model modules for that app.
        app_labels={},

        # Mapping of app_labels to a dictionary of model names to model code.
        # May contain apps that are not installed.
        app_models=SortedDict(),

        # Mapping of app_labels to errors raised when trying to import the app.
        app_errors={},

        # -- Everything below here is only used when populating the cache --
        loaded=False,
        handled={},
        postponed=[],
        nesting_level=0,
        _get_models_cache={},
    )

    def __init__(self):
        self.__dict__ = self.__shared_state

    def _populate(self):
        """
        Fill in all the cache information. This method is threadsafe, in the
        sense that every caller will see the same state upon return, and if the
        cache is already initialised, it does no work.
        """
        if self.loaded:
            return
        # Note that we want to use the import lock here - the app loading is
        # in many cases initiated implicitly by importing, and thus it is
        # possible to end up in deadlock when one thread initiates loading
        # without holding the importer lock and another thread then tries to
        # import something which also launches the app loading. For details of
        # this situation see #18251.
        imp.acquire_lock()
        try:
            if self.loaded:
                return
            
            for app_name in settings.INSTALLED_APPS:
                if app_name in self.handled:
                    continue
                self.load_app(app_name, True)
            if not self.nesting_level:
                for app_name in self.postponed:
                    self.load_app(app_name)
                self.loaded = True
        finally:
            imp.release_lock()

    def _label_for(self, app_mod):
        """
        Return app_label for given models module.
        app的名字
        """
        return app_mod.__name__.split('.')[-2]

    def load_app(self, app_name, can_postpone=False):
        """
        Loads the app with the provided fully qualified name, and returns the
        model module.
        """
        self.handled[app_name] = None
        self.nesting_level += 1
        app_module = import_module(app_name)
        try:
            models = import_module('.models', app_name)
            middlewares = import_module('.middlewares', app_name)
        except ImportError:
            self.nesting_level -= 1
            # If the app doesn't have a models module, we can just ignore the
            # ImportError and return no models for it.
            if not module_has_submodule(app_module, 'models') or not module_has_submodule(app_module, 'middlewares') :
                return None
            # But if the app does have a models module, we need to figure out
            # whether to suppress or propagate the error. If can_postpone is
            # True then it may be that the package is still being imported by
            # Python and the models module isn't available yet. So we add the
            # app to the postponed list and we'll try it again after all the
            # recursion has finished (in populate). If can_postpone is False
            # then it's time to raise the ImportError.
            else:
                if can_postpone:
                    self.postponed.append(app_name)
                    return None
                else:
                    raise

        self.nesting_level -= 1
        if models not in self.app_store:
            self.app_store[models] = len(self.app_store)
            self.app_labels[self._label_for(models)] = models
        return models

    def app_cache_ready(self):
        """
        Returns true if the model cache is fully populated.

        Useful for code that wants to cache the results of get_models() for
        themselves once it is safe to do so.
        """
        return self.loaded

    def get_apps(self):
        "Returns a list of all installed modules that contain models."
        self._populate()

        # Ensure the returned list is always in the same order (with new apps
        # added at the end). This avoids unstable ordering on the admin app
        # list page, for example.
        apps = [(v, k) for k, v in self.app_store.items()]
        apps.sort()
        return [elt[1] for elt in apps]

    def get_app(self, app_label, emptyOK=False):
        """
        Returns the module containing the models for the given app_label. If
        the app has no models in it and 'emptyOK' is True, returns None.
        """
        self._populate()
        imp.acquire_lock()
        
        try:
            for app_name in settings.INSTALLED_APPS:
                if app_label == app_name.split('.')[-1]:
                    mod = self.load_app(app_name, False)
                    if mod is None:
                        if emptyOK:
                            return None
                        raise ImproperlyConfigured("App with label %s is missing a models.py module." % app_label)
                    else:
                        return mod
            raise ImproperlyConfigured("App with label %s could not be found" % app_label)
        finally:
            imp.release_lock()

    def get_app_errors(self):
        "Returns the map of known problems with the INSTALLED_APPS."
        self._populate()
        return self.app_errors
    
    
    def get_models(self, app_mod=None,
                   include_auto_created=False, include_deferred=False,
                   only_installed=True, include_swapped=False):
        """
        Given a module containing models, returns a list of the models.
        Otherwise returns a list of all installed models.

        By default, auto-created models (i.e., m2m models without an
        explicit intermediate table) are not included. However, if you
        specify include_auto_created=True, they will be.

        By default, models created to satisfy deferred attribute
        queries are *not* included in the list of models. However, if
        you specify include_deferred, they will be.

        By default, models that aren't part of installed apps will *not*
        be included in the list of models. However, if you specify
        only_installed=False, they will be.

        By default, models that have been swapped out will *not* be
        included in the list of models. However, if you specify
        include_swapped, they will be.
        """
        """
            app_mod is models.py
        """
        cache_key = (app_mod, include_auto_created, include_deferred, only_installed, include_swapped)
        try:
            return self._get_models_cache[cache_key]
        except KeyError:
            pass
        self._populate()
        if app_mod:
            if app_mod in self.app_store:
                app_list = [self.app_models.get(self._label_for(app_mod),SortedDict())]
            else:
                app_list = []
        else:
            #获取全部已安装的应用(app)的的的所有的model,不是models.py ,是所有app里面的models.py里面的
            #内容
            #通过app的名字查找到在该app 包下面所有的model
            if only_installed:
                app_list = [self.app_models.get(app_label, SortedDict())
                            for app_label in six.iterkeys(self.app_labels)]
            else:
                #"only_install未指定"
                app_list = six.itervalues(self.app_models)
        model_list = []
        for app in app_list:
            #app_list: [appname:{"model名1"：model模块1,'model名2':'model模块2'...}]
            #获取每个app下面所有的models字典{"model名"：model模块}形式
            model_list.extend(
                #取得所有模块
                model for model in app.values()
                #没有那么多限制条件你妈逼的

            )
        self._get_models_cache[cache_key] = model_list
        return model_list

    def get_model(self, app_label, model_name,
                  seed_cache=True, only_installed=True):
        """
        Returns the model matching the given app_label and case-insensitive
        model_name.

        Returns None if no model is found.
        """
        if seed_cache:
            self._populate()
        if only_installed and app_label not in self.app_labels:
            return None
        return self.app_models.get(app_label, SortedDict()).get(model_name.lower())

    def register_models(self, app_label, *models):
        """
        Register a set of models as belonging to an app.
        """
        for model in models:
            Base = declarative_base()
            if issubclass(model,Base):

                # Store as 'name: model' pair in a dictionary
                # in the app_models dictionary
                model_name = model._meta.object_name.lower()
                model_dict = self.app_models.setdefault(app_label, SortedDict())
                if model_name in model_dict:
                    # The same model may be imported via different paths (e.g.
                    # appname.models and project.appname.models). We use the source
                    # filename as a means to detect identity.
                    fname1 = os.path.abspath(upath(sys.modules[model.__module__].__file__))
                    fname2 = os.path.abspath(upath(sys.modules[model_dict[model_name].__module__].__file__))
                    # Since the filename extension could be .py the first time and
                    # .pyc or .pyo the second time, ignore the extension when
                    # comparing.
                    if os.path.splitext(fname1)[0] == os.path.splitext(fname2)[0]:
                        continue
                model_dict[model_name] = model
                self._get_models_cache.clear()

cache = AppCache()

# These methods were always module level, so are kept that way for backwards
# compatibility.
get_apps = cache.get_apps
get_app = cache.get_app
get_app_errors = cache.get_app_errors
get_models = cache.get_models
get_model = cache.get_model
register_models = cache.register_models
load_app = cache.load_app
app_cache_ready = cache.app_cache_ready
