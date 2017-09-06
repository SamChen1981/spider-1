from HTMLParser import HTMLParser

from spider.utils.fetch_util import Extractor
from spider.utils.log import logger


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def _get_rid_of_html(content):
    return strip_tags(content)


class Inverted_List(object):
    def is_parser(self, urldict):
        return True

    def getlinks(self, content):
        regx = r'<div class="b-slb-item">.*?<h3>.*?<a href="(.*?)">.*?</div>'
        links = Extractor.simpleExtractorAsList(regx, content)
        logger.info("get content title: {0}".format(links))
        return links

    def parser(self, content):
        return self.getlinks(content)

    def parser_content(self, content):
        regx = r'<div class="b-slb-item">.*?<h3>.*?<a href="(.*?)">.*?</div>'
        titles = Extractor.simpleExtractorAsList(regx, content)
        logger.info("get content title: {0}".format(titles))
