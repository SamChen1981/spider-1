# encoding=utf8

from spider.utils.module_loading import import_by_path
from spider.conf import settings
from spider.exceptions import ImproperlyConfigured


def load_backend(path):
    return import_by_path(path)()


def get_backends():
    backends = []
    for backend_path in settings.STAGING_BACKENDS:
        backends.append(load_backend(backend_path))
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return backends


class Staging(object):
    def __init__(self):
        self.backend = None
        for backend in get_backends():
            self.backend = backend
            break

    def checkvisited(self, url):
        # 检查这个url是否已经访问过
        return self.backend.checkvisited(url)

    def add(self, url):
        return self.backend.add(url)

staging = Staging()
