'''
Created on 2014-9-2

@author: Administrator
'''
import json
import string
class startfuture(object):
    def __init__(self,_process):
        self._process=_process
    def callback(self,ch, method, properties, body):
        print " [x] Received %r" % (body,)
        urlpack=body
        if not urlpack:
            print 'BROKEN'
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        count=10
        try:
            count=json.loads(urlpack)['count']

        except:
            
            urlpack=string.join([urlpack,'}'],'')    
        count=count-1
        packed=json.loads(urlpack)
        url=json.loads(urlpack)['url']
        print str(count) 
        if count:
            self._process(packed)
            ch.basic_ack(delivery_tag = method.delivery_tag)

        else:
            ch.basic_ack(delivery_tag = method.delivery_tag)


        print " [x] Done" 
