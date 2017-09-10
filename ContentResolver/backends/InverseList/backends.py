# encoding=utf8

from spider.utils.fetch_util import Extractor
from spider.utils.log import logger


class Inverted_List(object):
    def is_parser(self, urldict):
        return True

    def getlinks(self, content):
        regx = r'<div class="b-slb-item">.*?<h3>.*?<a href="(.*?)">.*?</div>'
        links = Extractor.simpleExtractorAsList(regx, content)
        logger.info("get content links: {0}".format(links))
        return links

    def parser(self, content, url_body=None):
        return self.getlinks(content)

    def parser_content(self, content, url_body=None):

        return {
            "title": self.get_title(content),
            "article": self.get_article(content),
            "author": self.get_author(content)
        }

    def get_title(self, content):
        regx = r'<div class="b-story-header">.*?<h1>([\s\S]*?)<\/h1>'
        titles = Extractor.getItemAsValue(content, regx, 1)
        return titles

    def get_article(self, content):
        regx = r'<div class="b-story-body-x x-r15">.*?<p>([\s\S]*?)<\/p>'
        article = Extractor.getItemAsValue(content, regx, 1)
        return article

    def get_author(self, content):
        regx = r'by<span class="b-story-user-y x-r22">[\s\S].*?<a[\s\S]*?>([' \
               r'\s\S]*?)<\/a>'
        author = Extractor.getItemAsValue(content, regx, 1)
        return author.strip()
