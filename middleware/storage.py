# encoding=utf8

from spider.save_page import PageSave
from spider.utils.log import logger
from spider.utils import skip_process
from spider import constant


class StorageMiddleWare(object):
    """
        openerMiddleware是用来调用打开一个url所需要的配置
        从用户自定义的opener.py中读取BaseOpener的子类，该类必须实例化，否则报错
    """
    @skip_process.skip_if_none_response
    def process_save(self, url_body, **kwargs):
        logger.info("process url : {0} storage".format(url_body.get(
            "url")))
        PageSave().save(url_body[constant.RESPONSE_SIGNATURE], **url_body)
