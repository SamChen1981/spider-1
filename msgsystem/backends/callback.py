'''
Created on 2014-9-2

@author: Administrator
'''
import json

class startfuture(object):
    def __init__(self,_process):
        self._process=_process
    def callback(self,ch, method, properties, body):
        

        print " [x] Received %r" % (body,)
    #    rule=Acrule(local_dir=local_dir,DOWNLOAD_QUEUE=DOWNLOAD_QUEUE,LOCALPATH_QUEUE=LOCALPATH_QUEUE,downloadtag=downloadtag,saved_field=saved_field,domain=domain,dlregx=dlregx,prregx=prregx,dbregx=dbregx,dbname=dbname,\
    #host=host,user=user,passwd=passwd,filename='huaqiang_com_contact')
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