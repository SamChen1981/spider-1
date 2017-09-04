# coding=utf8

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
import string
# channel.queue_declare(queue=flag, durable=True)
import traceback
import Queue
from spider.conf import settings
from spider.msgsystem.callback import StartFuture

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
# channel=connection.channel()
simple_queue = Queue.Queue(0)


class task_queue():
    # 队列的目录
    db_directory = ''
    lock1 = Lock()
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    '''
      该类初始化rabbitmq的队列。
     1. __init__初始化队列和文件夹
     2.savevisitedURL保存已经访问过的url
     3.popmsgfromBDB,从bdb中弹出一条记录
     4.checkvisited:检查一条记录是否存在
     5.sendtask2BDB:向队列发送一条消息

    '''

    def __init__(self, *args, **kwargs):

        for k, v in kwargs.items():
            print  v
            task_queue.channel.queue_declare(queue=v, durable=True)

            if task_queue.db_directory:
                if os.path.isdir(task_queue.db_directory):
                    pass
                else:
                    try:

                        os.makedirs(task_queue.db_directory)
                    except:
                        error = traceback.format_exc()
                        print error

                        # 保存到待抓取队列或者错误队列，根据参数flag判断

    @classmethod
    def sendtask2Rabbit(cls, message, flag, func=None, exchange_name='',
                        **kwargs):
        msgs = []
        if not isinstance(message, list):
            return
        count = 0
        for msg in message:
            rabbitmsg = ''
            # 传入的值为一个字典类型，有meta信息
            if isinstance(msg, dict):
                msg.update({'func': func, 'flag': flag, 'count': 10})
                msg.update(kwargs)
                rabbitmsg = json.dumps(msg, ensure_ascii=False)
            if isinstance(msg, (str, unicode)):
                # 当没有meta信息的时候
                resultmsgs = {'url': msg, 'func': func, 'flag': flag,
                              'count': 10}
                resultmsgs.update(kwargs)
                rabbitmsg = json.dumps(resultmsgs, ensure_ascii=False)

            print 'QUEUE NAME : %s' % flag
            try:
                task_queue.channel.basic_publish(exchange=exchange_name,
                                                 routing_key=flag,
                                                 body=rabbitmsg,
                                                 properties=pika.BasicProperties(
                                                     delivery_mode=2,
                                                     # make message persistent
                                                 ))
            except:
                error = traceback.format_exc()
                print error
                sys.exit()

            print " [x] Sent %r" % (rabbitmsg,)

    @classmethod
    def consumer(cls, _process):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))

            channel = connection.channel()

            print ' [*] Waiting for messages. To exit press CTRL+C'
            t = task_queue(channel, **{'flag': settings.flag})

            channel.basic_qos(prefetch_count=1)

            callback = StartFuture(_process).callback
            channel.basic_consume(callback, queue=settings.flag)
        except Exception:
            sys.exit(0)

        channel.start_consuming()

    @classmethod
    def put(cls, message, flag, mqtype=None, func=None, exchange_name='',
            **kwargs):
        msgs = []
        print mqtype
        if not isinstance(message, list):
            return

        task_queue.sendtask2Rabbit(message, flag, exchange_name=exchange_name,
                                   **kwargs)
