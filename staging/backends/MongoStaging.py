# encoding=utf8

from spider.staging.backends import redis_utils

REDIS_SET_NAME = "test:test"


class StagingBackend(object):
    """
        根据用户提供的url的正则表达式 ，判断某一个url是否应该保存
        用户应该提供:
        1.具体的页面存放backend,如没有提供，默认是保存于磁盘上，id 是路径的和时间的 md5
        2.判定的url ,一个list 或者itertable，如果目前的url匹配任意一个，则认为这个url应该保存，如果是[*]
        则保存所有遇到的页面，如果是[!]，不保存任何页面。
    """

    def checkvisited(self, item, **kwargs):
        filepath = redis_utils.redis_db.check_repeate(item, REDIS_SET_NAME)
        return filepath

    def add(self, item, **kwargs):
        redis_utils.redis_db.add(item, REDIS_SET_NAME)
