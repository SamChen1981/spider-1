# -*- coding:utf-8 -*-

"""
File Name : 'distinct'.py
Description:
Author: 'chengwei'
Date: '2016/6/2' '11:45'
python: 2.7.10
"""

import hashlib
import os
import codecs
import ConfigParser
import redis

from spider.conf import settings

"""
利用redis的集合不允许添加重复元素来进行去重
"""


class RedisDB(object):

    def __init__(self):
        self.pool, self.redis_db = self.redis_init()

    def redis_init(self, parasecname="Redis"):
        """
        初始化redis
        :param parasecname:
        :return: redis连接池
        """
        cur_script_dir = settings.CONF_DIR
        cfg_path = os.path.join(cur_script_dir, "redis.cfg")

        cfg_reder = ConfigParser.ConfigParser()
        secname = parasecname
        cfg_reder.readfp(codecs.open(cfg_path, "r", "utf_8"))
        redis_host = cfg_reder.get(secname, "server")
        redis_pass = cfg_reder.get(secname, "pass")

        # redis
        pool = redis.ConnectionPool(host=redis_host, port=6379, db=0,
                                    password=redis_pass)
        redis_db = redis.Redis(connection_pool=pool)

        return pool, redis_db

    def add(self, check_str, set_name):
        hash_value = sha1(check_str)
        result = self.redis_db.sadd(set_name, hash_value)
        return result

    def check_repeate(self, check_str, set_name):
        """
        向redis集合中添加元素，重复则返回0，不重复则添加成功，并返回1
        :param redis_db:redis连接
        :param check_str:被添加的字符串
        :param set_name:项目所使用的集合名称，建议如下格式：”projectname:task_remove_repeate“
        :return:
        """
        return self.add(check_str, set_name)

    def redis_close(self):
        """
        释放redis连接池
        :param pool:
        :return:
        """
        self.pool.disconnect()


def sha1(x):
    sha1obj = hashlib.sha1()
    sha1obj.update(x)
    hash_value = sha1obj.hexdigest()
    return hash_value

redis_db = RedisDB()
