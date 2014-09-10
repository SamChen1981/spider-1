#encoding=utf8
from spider.middleware.loading import register_middlewares
import sys
class middleware_type(type):
    '''本类就帮助创建middleware时进行自动注册'''
    def __new__(cls,name,bases,attrs):
        new_class=super(middleware_type, cls).__new__(cls,name,bases,attrs)
        
        model_module = sys.modules[new_class.__module__]
        print model_module.__package__
        register_middlewares(model_module.__package__,*(new_class,))


class middleware_base(object):
    __metaclass__=middleware_type
    