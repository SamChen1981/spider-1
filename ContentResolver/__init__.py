# encoding=utf8

from spider.utils.module_loading import import_by_path
from spider.conf import settings
from spider.exceptions import ImproperlyConfigured
from spider.utils import skip_process


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

    def parser(self, content, url_body=None):
        """从当前页面提取到链接"""
        return self.backend.parser(content, url_body)

    @skip_process.skip_if_content_invalid(settings.REG_LIST)
    def parser_content(self, content, url_body=None):
        """从当前页面解析到数据"""
        return self.backend.parser_content(content, url_body)

content_parser = ContentParser()
