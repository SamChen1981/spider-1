# encoding=utf8
from spider.conf import settings

from fetch_util import *
from spider.utils.fetch_util import urlFilter
from spider.internet import httpreq


class OpenerMiddleware(object):

    def process_open(self, url_body):
        url = url_body["url"]
        httpreq().request(url)
