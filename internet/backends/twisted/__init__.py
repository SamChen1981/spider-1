import sys

from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.python.util import println
from MoinMoin.conftest import callback



class twisted_client(object):
    def __init__(self,urldict,callback,errback=None):
        self.urldict=urldict
        self.callback=callback
        self.errback=errback
        if self.errback==None:
            self.err
    def request(self):
        url=self.urldict['urldict']
        getPage(url).addCallbacks(
        callback=self.callback,
        errback=self.errback)
        reactor.run()