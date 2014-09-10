#encoding=utf8
'''
Created on 2014年9月6日

@author: mu
'''
from spider.core.handlers.base import BaseHandler
from spider.msgsystem import msgsys
from spider.middleware.loading import get_app,get_apps,get_middleware,get_middlewares
from spider.conf import settings
class CRAWLHandler(BaseHandler):
    def __init__(self,spidername):
        self.spidername=spidername
    def __call__(self):
        
        urldict={}
        
        urldict.update({'app':self.spidername})
        
        self.load_middleware()
        msg=msgsys()
        msg.put(settings.seed)
        callback=self.go_get_it(urldict)
        msg.consumer(callback)
        
        