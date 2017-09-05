'''
Created on 2014年9月1日

@author: mu
'''
# encoding=utf8
from spider.ContentResolver import content_parser


class ParserMiddleware(object):

    def process_parser(self, url_body):
        c_parser = content_parser()
        c_parser.is_parser(url_body)
        links = c_parser.parser(url_body)
        return links
