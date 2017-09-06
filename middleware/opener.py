# encoding=utf8

from spider.internet import httpreq


class OpenerMiddleware(object):

    def process_open(self, url_body):
        url = url_body["url"]
        if not url:
            return
        response = httpreq.request(url)
        return response
