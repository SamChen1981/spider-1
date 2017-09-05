# encoding=utf8

from spider.save_page import PageSave


class StorageMiddleWare(object):
    """
        openerMiddleware是用来调用打开一个url所需要的配置
        从用户自定义的opener.py中读取BaseOpener的子类，该类必须实例化，否则报错
    """

    def process_save(self, url_body):
        PageSave().save(url_body)
