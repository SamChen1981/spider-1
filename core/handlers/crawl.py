# encoding=utf8
'''
Created on 2014年9月6日

@author: mu
'''
from spider.core.handlers.base import BaseHandler
from spider.msgsystem import msgsys
from spider.conf import settings


class CRAWLHandler(BaseHandler):
    def __init__(self, spidername):
        super(CRAWLHandler, self).__init__()
        self.spidername = spidername

    def __call__(self):

        self.load_middleware()
        msg = msgsys()
        msg.put(settings.seed)
        callback = self.go_get_it()
        msg.consumer(callback)
