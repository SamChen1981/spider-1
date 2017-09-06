import functools


def skip_if_none_response(func):

    @functools.wraps(func)
    def wrapper(self, body, *args, **kwargs):
        if "response" not in body:
            return
        else:
            return func(self, body)
    return wrapper
