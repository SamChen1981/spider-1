# encoding=utf8
from spider.utils.log import logger


class PostFilterMiddleware(object):
    def process_postfilter(self, url_body):
        logger.debug("post filter url body: {0}".format(url_body))
        return
