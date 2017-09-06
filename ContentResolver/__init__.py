from spider.utils.module_loading import import_by_path
from spider.conf import settings
from spider.exceptions import ImproperlyConfigured


def load_backend(path):
    return import_by_path(path)()


def get_backends():
    backends = []
    for backend_path in settings.PARSER_BACKENDS:
        backends.append(load_backend(backend_path))
    if not backends:
        raise ImproperlyConfigured(
            'No authentication backends have been defined. Does AUTHENTICATION_BACKENDS contain anything?')
    return backends


class ContentParser(object):
    def __init__(self):
        self.backend = None
        for backend in get_backends():
            self.backend = backend
            break

    def is_parser(self, item):
        return self.backend.is_parser(item)

    def parser(self, content):
        return self.backend.parser(content)

    def parser_content(self, content):
        self.backend.parser_content(content)

content_parser = ContentParser()
