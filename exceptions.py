"""
Global exception and warning classes.
"""


class RoutingKEYNotExisted(Exception):
    pass


class ImproperlyConfigured(Exception):
    """Django is somehow improperly configured"""
    pass
