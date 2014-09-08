#encoding=utf8
"Utilities for loading models and the modules that contain them."
from sqlalchemy.ext.declarative import declarative_base


from spider.core.exceptions import ImproperlyConfigured
from spider.utils.datastructures import SortedDict

from spider.utils._os import upath
from spider.db.model.loading import get_app ,get_apps,_populate,app_cache_ready,load_app
from django.utils import six

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



    def app_cache_ready(self):
        """
        Returns true if the model cache is fully populated.

        Useful for code that wants to cache the results of get_models() for
        themselves once it is safe to do so.
        """
        return self.loaded



    
    
    def get_middlewares(self, app_mod=None,
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
        cache_key = (app_mod,)
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

    def get_middleware(self, app_label, model_name,
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

    def register_middlewares(self, app_label, *models):
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
get_middlewares = cache.get_middlewares
get_middleware = cache.get_middleware
register_middlewares = cache.register_middlewares
load_app = cache.load_app
app_cache_ready = cache.app_cache_ready
