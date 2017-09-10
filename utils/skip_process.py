import functools
from spider.utils import fetch_util


def skip_if_none_response(func):

    @functools.wraps(func)
    def wrapper(self, body, *args, **kwargs):
        if "response" not in body:
            return
        else:
            return func(self, body)
    return wrapper


def skip_if_content_invalid(regex):
    def wrap_func(func):
        @functools.wraps(func)
        def wrapper(self, content, url_body):
            if not regex:
                return func(self, content, url_body)
            # check url and content is valid
            url = url_body["url"]
            if not content:
                return
            if isinstance(regex, list):
                for reg in regex:
                    if fetch_util.Rule.matchurl(**{"url": url, "regx": reg}):
                        return func(self, content, url_body)
                    else:
                        return
            else:
                if fetch_util.Rule.matchurl(**{"url": url, "regx": regex}):
                    return func(self, content, url_body)
        return wrapper
    return wrap_func


