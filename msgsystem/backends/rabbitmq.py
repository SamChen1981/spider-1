# coding=utf8

import sys
import json
import pika

from multiprocessing import Lock

from spider.conf import settings
from spider.msgsystem.backends.callback import StartFuture
from spider.utils.log import logger
from spider import constant
from spider import exceptions

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))


class TaskQueue(object):
    # 队列的目录
    lock1 = Lock()
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
        self.queue_declare(settings.RABBITMQ_QUEUE)

    def queue_declare(self, queue_name):
        TaskQueue.channel.queue_declare(queue=queue_name, durable=True)

    @classmethod
    def sendtask2Rabbit(cls, message, func=None, exchange_name='',
                        **kwargs):
        if not isinstance(message, list):
            return
        for msg in message:
            if "route_key" not in msg:
                raise exceptions.RoutingKEYNotExisted
            rabbitmsg = ''
            # 传入的值为一个字典类型，有meta信息
            if isinstance(msg, dict):
                msg.update(kwargs)
                rabbitmsg = json.dumps(msg, ensure_ascii=False)
            if isinstance(msg, (str, unicode)):
                # 当没有meta信息的时候
                resultmsgs = {'url': msg}
                if func:
                    resultmsgs.update({"func": func})
                resultmsgs.update(kwargs)
                rabbitmsg = json.dumps(resultmsgs, ensure_ascii=False)
            try:
                TaskQueue.channel.basic_publish(exchange=exchange_name,
                                                routing_key=msg['route_key'],
                                                body=rabbitmsg,
                                                properties=pika.BasicProperties(
                                                    delivery_mode=constant.MESSAGE_PERSISTENCE,
                                                    # make message persistent
                                                ))
            except Exception as e:
                logger.error(e)
                sys.exit()

            print " [x] Sent %r" % (rabbitmsg,)

    @classmethod
    def consumer(cls, _process):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))

            channel = connection.channel()

            print ' [*] Waiting for messages. To exit press CTRL+C'
            t = TaskQueue(channel, **{'flag': settings.flag})

            channel.basic_qos(prefetch_count=1)

            callback = StartFuture(_process).callback
            channel.basic_consume(callback, queue=settings.flag)
        except Exception:
            sys.exit(0)

        channel.start_consuming()

    @classmethod
    def put(cls, message, mqtype=None, func=None,
            exchange_name='',
            **kwargs):
        if not isinstance(message, list):
            return
        TaskQueue.sendtask2Rabbit(message, exchange_name=exchange_name,
                                  **kwargs)
