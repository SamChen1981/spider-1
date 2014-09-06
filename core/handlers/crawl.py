'''
Created on 2014年9月6日

@author: mu
'''
from spider.core.handlers.base import BaseHandler
from spider.msgsystem import msgsys
class CRAWLHandler(BaseHandler):
    def __call__(self):
        callback=self.go_get_it()
        msgsys().consumer(callback)
        
        