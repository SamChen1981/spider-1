#encoding=utf8
import hashlib
import logging
import re

from spider.conf import settings
from django import http
from django.core.mail import mail_managers
from spider.utils.http import urlquote
from spider.utils import six
from django.core import urlresolvers
from fetch_util import *
from spider.core.exceptions import ImproperlyConfigured
from spider.utils.fetch_util import  urlFilter, Fetch_WebContent  
import os
from gc import garbage
logger = logging.getLogger(__name__)
from datetime import datetime
import time
import traceback
from spider.staging.mongomodels import data

'''
    默认的中间值存储方式是mongodb,
'''
def add(item):
    try:
        d=data(url=item)
        d.save()
    except:
        pass
def checkvisited(item):
    try:
        data.objects.get(url=item)
        return True
    except:
        return False
class StagingBackend(object):
    """
        根据用户提供的url的正则表达式 ，判断某一个url是否应该保存
        用户应该提供:
        1.具体的页面存放backend,如没有提供，默认是保存于磁盘上，id 是路径的和时间的 md5
        2.判定的url ,一个list 或者itertable，如果目前的url匹配任意一个，则认为这个url应该保存，如果是[*]
        则保存所有遇到的页面，如果是[!]，不保存任何页面。
    """
    def checkvisited(self,item,**kwargs):
        
       
        if len(settings.PAGE_SAVE_REGLIST)==0:
            raise ImproperlyConfigured("REGLIST MUST SET PROPERLY")

        filepath=checkvisited(item)
        return filepath
    def add(self,item,**kwargs):
        