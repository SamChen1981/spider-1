# encoding=utf8

from spider.internet import httpreq


class OpenerMiddleware(object):

    def process_open(self, url_body):
        """调用internet后端打开一个URL，返回文本"""
        url = url_body["url"]
        if not url:
            return
        response = httpreq.request(url)
        return response
