# encoding=utf8
from spider.conf import settings
from spider.exceptions import ImproperlyConfigured

from spider.utils.module_loading import import_by_path


def load_backend(path):
    return import_by_path(path)()


def get_backends():
    backends = []
    for backend_path in settings.SAVE_PAGE_BACKENDS:
        backends.append(load_backend(backend_path))
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return backends


class PageSave(object):
    def __init__(self):
        for backend in get_backends():
            self.backend = backend

    def save(self, content, **kwargs):
        if content:
            self.backend.saveHTML(content, **kwargs)
