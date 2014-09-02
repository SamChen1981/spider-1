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

logger = logging.getLogger('django.request')


class OpenerMiddleware(object):
    """
        openerMiddleware是用来调用打开一个url所需要的配置
        从用户自定义的opener.py中读取BaseOpener的子类，该类必须实例化，否则报错
    """
    
    def process_open(self,urldict):
        
       
        if len(settings.REGLIST)==0:
            raise ImproperlyConfigured("REGLIST MUST SET PROPERLY")
        if not urldict.has_key('openers'):
            raise Exception('OPENER HAS TO BE SETTED !!!!')
        if not urlFilter.matchurl(**{'regx':settings.REGLIST,'url':self.relink}):
            return ''
        fetch=Fetch_WebContent()
        con=fetch.getAllContent(urldict['url'],**urldict)
        urldict.update({'content':con[0]})
        
