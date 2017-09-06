# encoding=utf8

from spider import constant
from spider.ContentResolver import content_parser
from spider.utils.log import logger


class ParserMiddleware(object):

    def process_filter(self, url_body):
        logger.debug("parser url content: {0}".format(url_body.get(
            constant.RESPONSE_SIGNATURE)))
        logger.info("process url: {0}, filter".format(url_body["url"]))
        return content_parser.parser(
            url_body.get(constant.RESPONSE_SIGNATURE))

    def process_parser(self, url_body):
        """分析url_body中的content

        :param url_body:包含content
        :return: 返回后需要抓取的连接，list类型
        """
        return
