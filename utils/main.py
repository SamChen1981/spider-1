#encoding=utf8
from gevent import gevent
class rabbitmq_fetch(object):
    def consumer(self):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    
            channel=connection.channel()
    
            print 'Thread : %s' % SETTING.processName
            print ' [*] Waiting for messages. To exit press CTRL+C'
            t=task_queue(channel,**{'flag':SETTING.flag})
    
        
            channel.basic_qos(prefetch_count=1)
            
            channel.basic_consume(self.callback,queue=SETTING.flag)
        except:
            sys.exit(0)
    
        channel.start_consuming()
    
    #rabbitmq��Ϣ����
    def callback(self,ch, method, properties, body):
        rule=Acrule(local_dir=SETTING.local_dir,DOWNLOAD_QUEUE=SETTING.DOWNLOAD_QUEUE,LOCALPATH_QUEUE=SETTING.LOCALPATH_QUEUE,downloadtag=SETTING.downloadtag,saved_field=SETTING.saved_field,domain=SETTING.domain,dlregx=SETTING.dlregx,prregx=SETTING.prregx,dbregx=SETTING.dbregx,dbname=SETTING.dbname,\
                    host=SETTING.host,user=SETTING.user,passwd=SETTING.passwd,filename='huaqiang_com_contact')


        print " [x] Received %r" % (body,)
    #    rule=Acrule(local_dir=local_dir,DOWNLOAD_QUEUE=DOWNLOAD_QUEUE,LOCALPATH_QUEUE=LOCALPATH_QUEUE,downloadtag=downloadtag,saved_field=saved_field,domain=domain,dlregx=dlregx,prregx=prregx,dbregx=dbregx,dbname=dbname,\
    #host=host,user=user,passwd=passwd,filename='huaqiang_com_contact')
    #

    #
        urlpack=body


        if not urlpack:
            print 'BROKEN'

            ch.basic_ack(delivery_tag = method.delivery_tag)


            return
        count=10
        try:
            count=json.loads(urlpack)['count']

        except:
            print 'urlpack���ִ���\n'
            urlpack=string.join([urlpack,'}'],'')    
        count=count-1

        packed=json.loads(urlpack)
        url=json.loads(urlpack)['url']
        print str(count) 
        if count:
            filterc=realfilter(page_save_reglist=SETTING.page_save_reglist,is_javascript=SETTING.is_javascript,save_dir=SETTING.save_dir,LOCALPATH_QUEUE=SETTING.LOCALPATH_QUEUE,dbtable=SETTING.dbtable,local_flag=SETTING.local_flag,count=10,exchange_name=SETTING.exchange_name,urlpack=packed,domain='',reglist=SETTING.reglist,dlregx=SETTING.dlregx)

            filterc.processChain(packed)
            rule.processChain(packed)
            ch.basic_ack(delivery_tag = method.delivery_tag)


            ''' 
		error=traceback.format_exc()
		print error
		del packed['flag']
		addtime=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d:%H:%M:%S')
		currentpid=os.getpid()
		os.kill(currentpid,signal.SIGTERM)
	    '''

                #task_queue.sendtask2BDB([url],SETTING.ERROR_QUEUE,exchange_name=SETTING.exchange_name,mqtype='RABBIT',**packed)
                #ch.basic_nack(method.delivery_tag,0,False)	
        else:
            ch.basic_ack(delivery_tag = method.delivery_tag)


        print " [x] Done" 
        
def run_forever():
    rf=rabbitmq_fetch()
    rf.consumer()
def serve_forever():
    gevent.signal(signal.SIGQUIT,gevent.shutdown)
    thread = gevent.spawn(run_forever)
    thread.join()    