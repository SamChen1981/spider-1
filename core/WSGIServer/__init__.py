
import os
import sys

from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_HERE)
sys.path.append(os.path.join(_HERE, '..'))
sys.path.append(os.path.join(_HERE, '../contrib'))
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"



import os
import socket
import sys
import traceback


from spider.core.exceptions import ImproperlyConfigured
from spider.core.wsgi import get_wsgi_application
from spider.utils.importlib import import_module




def get_internal_wsgi_application():
    """
    Loads and returns the WSGI application as configured by the user in
    ``settings.WSGI_APPLICATION``. With the default ``startproject`` layout,
    this will be the ``application`` object in ``projectname/wsgi.py``.

    This function, and the ``WSGI_APPLICATION`` setting itself, are only useful
    for Django's internal servers (runserver, runfcgi); external WSGI servers
    should just be configured to point to the correct application object
    directly.

    If settings.WSGI_APPLICATION is not set (is ``None``), we just return
    whatever ``django.core.wsgi.get_wsgi_application`` returns.

    """
    from spider.conf import settings
    app_path = getattr(settings, 'WSGI_APPLICATION')
    if app_path is None:
        return get_wsgi_application()
    module_name, attr = app_path.rsplit('.', 1)
    try:
        mod = import_module(module_name)
    except ImportError as e:
        raise ImproperlyConfigured(
            "WSGI application '%s' could not be loaded; "
            "could not import module '%s': %s" % (app_path, module_name, e))
    try:
        app = getattr(mod, attr)
    except AttributeError as e:
        raise ImproperlyConfigured(
            "WSGI application '%s' could not be loaded; "
            "can't find '%s' in module '%s': %s"
            % (app_path, attr, module_name, e))

    return app




def WSGIServer(port,WSGIHandler):
    wsgi_app = tornado.wsgi.WSGIContainer(
        WSGIHandler)
    tornado_app = tornado.web.Application(
        [('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

