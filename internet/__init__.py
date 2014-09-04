
from spider.conf import settings
from spider.core.exceptions import ImproperlyConfigured
from spider.utils.module_loading import import_string
def load_backend(path):
    return import_string(path)()


def get_backends():
    backends = []
    for backend_path in settings.SAVE_PAGE_BACKENDS:
        backends.append(load_backend(backend_path))
    if not backends:
        raise ImproperlyConfigured('No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return backends

class httpreq(object):
    def __init__(self):
        for backend in get_backends():
            self.backend=backend
    def request(self,urldict):
        
        self.backend.request(urldict)
        
        