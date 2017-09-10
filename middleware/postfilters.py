# encoding=utf8
from spider.utils.log import logger
from spider import constant
from spider.db import db_storage


class PostFilterMiddleware(object):
    def process_postfilter(self, url_body):
        """调用db存储后端，存储解析到的数据"""
        logger.debug("post filter url body: {0}".format(url_body))
        if not isinstance(url_body, dict):
            return
        if constant.REFINED_DATA in url_body:
            db_storage.save(url_body[constant.REFINED_DATA])
        return
