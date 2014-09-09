
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

def WSGIServer(port,WSGIHandler):
    wsgi_app = tornado.wsgi.WSGIContainer(
        WSGIHandler)
    tornado_app = tornado.web.Application(
        [('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

