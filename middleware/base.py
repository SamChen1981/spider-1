#encoding=utf8
from spider.middleware.loading import register_middlewares
class middleware_base(type):
    '''本类就帮助创建middleware时进行自动注册'''
    def __new__(cls,name,bases,attrs):
        new_class=type.__new__(name,bases,attrs)
        app_label=__file__.rsplit('/',-2)
        model_module = sys.modules[new_class.__module__]
        register_middlewares(model_module.__package__,*(new_class,))