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

        msg = msgsys()
        for seed in settings.SEEDS:
            msg.put([{"url": seed,
                      "route_key": settings.RABBITMQ_QUEUE}])
        self.load_middleware()
        callback = self.go_get_it
        msg.consumer(callback)
