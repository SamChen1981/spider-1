# encoding=utf8

from spider import constant
from spider.ContentResolver import content_parser
from spider.utils.log import logger


class ParserMiddleware(object):

    def process_filter(self, url_body):
        """返回待抓取链接的url列表"""
        content = url_body.get(constant.RESPONSE_SIGNATURE)
        logger.debug("parser url content: {0}".format(content))
        logger.info("process url: {0}, filter raw links".format(url_body[
                                                                   "url"]))
        raw_links = content_parser.parser(content, url_body)
        url_body[constant.RAW_LINKS] = raw_links

    def process_parser(self, url_body):
        """返回从当前页面提取到的数据"""
        logger.info("process url: {0}, parse content".format(url_body["url"]))
        content = url_body.get(constant.RESPONSE_SIGNATURE)
        data = content_parser.parser_content(content, url_body=url_body)
        url_body[constant.REFINED_DATA] = data
