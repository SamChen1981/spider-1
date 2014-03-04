#coding=utf8

import time
import sys
from database import *
import json
import os
reload(sys)
sys.setdefaultencoding('utf8')
import threading
from  multiprocessing import Lock
import pika
#channel.queue_declare(queue=flag, durable=True)
import traceback
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#channel=connection.channel()

class task_queue():
    #队列的目录
    db_directory=''
    lock1=Lock()
    #connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel=connection.channel()




    '''
      该类初始化rabbitmq的队列。
     1. __init__初始化队列和文件夹
     2.savevisitedURL保存已经访问过的url
     3.popmsgfromBDB,从bdb中弹出一条记录
     4.checkvisited:检查一条记录是否存在
     5.sendtask2BDB:向队列发送一条消息
    
    '''
    def __init__(self,*args,**kwargs):
	for k,v in kwargs.items():
	    print  v 
	    task_queue.channel.queue_declare(queue=v, durable=True)

        if task_queue.db_directory:
            if os.path.isdir(task_queue.db_directory):  
	        pass 
            else:
                try:

                    os.makedirs(task_queue.db_directory)
                except:
                    error=traceback.format_exc()
                    print error
 
    #保存url,url必须是list,即是只有一个
    @classmethod
    def savevisitedURL(cls,urls,*args,**kwargs):
        try:
            #过滤掉已经保存的url
            vistedURL=DuplCheckDB(os.path.join(task_queue.db_directory,'visited.db'))

            url=vistedURL.filter_dupl_urls(urls)
            #添加未保存的url
            vistedURL.add_urls(url)
            #将缓冲区的内容写入磁盘
            vistedURL.sync()
            vistedURL.close()
            #返回这些未保存的url
            return url
        except:
            return []

    #根据队列弹出一个url
    @classmethod
    def popmsgfromBDB(cls,flag,url=None):
        print 'THE FLAG ISsdf' 
        if flag=='ERROR':
            edb=QueueDB(os.path.join(task_queue.db_directory,'errorqueue.db'))
            purl=edb.pop_url()

            edb.close()

            return purl

        if flag=='NORMAL':
            qdb=QueueDB(os.path.join(task_queue.db_directory,'testqueue.db'))

            purl=qdb.pop_url()
            print 'the url is %s' % purl
            qdb.close()
             
            return purl
        if flag=='DOWNLOAD':
            ddb=WebpageDB(os.path.join(task_queue.db_directory,'downloadqueue.db'))

            purl=ddb.delete(url)
            ddb.close()

            return purl

    #检查单个url是否重复
    @classmethod
    def checkvisited(cls,url,*args,**kwargs):
        vistedURL=DuplCheckDB(os.path.join(task_queue.db_directory,'visited.db'))
	print task_queue.db_directory
	return vistedURL.exist(url)
    #保存进入下载队列,也是hash算法
    @classmethod
    def send2downloadBDB(cls,message,*args,**kwargs):
        ddb=WebpageDB(os.path.join(task_queue.db_directory,'downloadqueue.db'))
        ddb.html2db(message,kwargs['filepath']) 
        ddb.close()
    #保存到待抓取队列或者错误队列，根据参数flag判断
    @classmethod
    def sendtask2Rabbit(cls,message,flag,func=None,exchange_name='',**kwargs):
        msgs=[]
        if not isinstance(message,list):
            return

        #channel=task_queue.connection.channel()

#	task_queue.channel.queue_declare(queue=flag, durable=True)
	count=0
        for msg in message:
            rabbitmsg=''
            #传入的值为一个字典类型，有meta信息
            if isinstance(msg,dict):

                msg.update({'func':func,'flag':flag,'count':10})
		msg.update(kwargs)
                rabbitmsg=json.dumps(msg,ensure_ascii=False)
            if isinstance(msg,(str,unicode)):
                #当没有meta信息的时候
                resultmsgs={'url':msg,'func':func,'flag':flag,'count':10}
		resultmsgs.update(kwargs)
                rabbitmsg=json.dumps(resultmsgs,ensure_ascii=False)

            print 'QUEUE NAME : %s' % flag
	    try:
            	task_queue.channel.basic_publish(exchange=exchange_name,
                          routing_key=flag,
                          body=rabbitmsg,
                          properties=pika.BasicProperties(
                          delivery_mode = 2, # make message persistent
                        ))
            except:
            	error=traceback.format_exc()
                print error
		sys.exit() 

            print " [x] Sent %r" % (rabbitmsg,)

    @classmethod
    def sendtask2BDB(cls,message,flag,mqtype=None,func=None,exchange_name='',**kwargs):
        msgs=[]
	print mqtype
        if not isinstance(message,list):
            return
        if mqtype=='RABBIT':
            task_queue.sendtask2Rabbit(message,flag,exchange_name=exchange_name,**kwargs)
        if mqtype=='BDB':
            task_queue.sendtask2Berkeley(message,flag)
	
    
    @classmethod
    def sendtask2Berkeley(cls,message,flag,func=None,**kwargs):
        msgs=[]
        if not isinstance(message,list):
            return
        for msg in message:
            #传入的值为一个字典类型，有meta信息
            if isinstance(msg,dict):

                msg.update({'func':func,'flag':flag})

                msgs.append(json.dumps(msg,ensure_ascii=False))

            if isinstance(msg,(str,unicode)):
                #当没有meta信息的时候
                resultmsgs={'url':msg,'func':func,'flag':flag}
                msgs.append(json.dumps(resultmsgs,ensure_ascii=False))
        print msgs 

        if flag=='ERROR':
            edb=QueueDB(os.path.join(task_queue.db_directory,'errorqueue.db'))
            edb.push_urls(msgs)
            edb.close()
        if flag=='NORMAL':
            qdb=QueueDB(os.path.join(task_queue.db_directory,'testqueue.db'))

            qdb.push_urls(msgs)
            qdb.close()


