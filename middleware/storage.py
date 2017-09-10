# encoding=utf8

from spider.save_page import PageSave
from spider.utils.log import logger
from spider.utils import skip_process
from spider import constant


class StorageMiddleWare(object):
    @skip_process.skip_if_none_response
    def process_save(self, url_body, **kwargs):
        """调用页面保存后端存储网页到存储设备上"""
        logger.info("process url : {0} storage".format(url_body.get(
            "url")))
        PageSave().save(url_body[constant.RESPONSE_SIGNATURE], **url_body)
