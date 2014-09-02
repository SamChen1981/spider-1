from spider.utils.module_loading import import_string
from spider.conf import settings
from spider.core.exceptions import ImproperlyConfigured
def load_backend(path):
    return import_string(path)()


def get_backends():
    backends = []
    for backend_path in settings.SAVE_PAGE_BACKENDS:
        backends.append(load_backend(backend_path))
    if not backends:
        raise ImproperlyConfigured('No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return backends

class Storage(object):
    def __init__(self):
        for backend in get_backends():
            self.backend=backend
    def save(self,content):
            
        filepath=self.backend.saveHTML(**{'content':content})
        return filepath
        