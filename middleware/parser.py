# encoding=utf8

from spider import constant
from spider.utils.log import logger


class ParserMiddleware(object):

    def process_parser(self, url_body):
        """分析url_body中的content

        :param url_body:
        :return: 返回后需要抓取的连接，list类型
        """

        logger.debug("parser url content: {0}".format(url_body.get(
            constant.RESPONSE_SIGNATURE)))

        return []
