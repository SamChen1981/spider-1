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
from spider.save_page import Storage
logger = logging.getLogger('django.request')


class StorageMiddleWare(object):
    """
        openerMiddleware是用来调用打开一个url所需要的配置
        从用户自定义的opener.py中读取BaseOpener的子类，该类必须实例化，否则报错
    """
    def process_save(self,urldict):
        docid=Storage().save(urldict['content'])
        urldict.update({'docid':docid})
       
        
        
