'''
Created on 2014年9月1日

@author: mu
'''
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
from spider.utils.fetch_util import db
logger = logging.getLogger('django.request')
import os
def _get_rid_of_dups(relink,rawlinklist):
    links=[]
    I2=[]
    for rawurl in db.from_iterable(rawlinklist):
        if isinstance(rawurl,(str,unicode)):
            if not rawurl in I2:

                links.extend([{'url':rawurl,'parent_url':relink}])
                I2.append(rawurl)
        else:
            if isinstance(rawurl,dict) and rawurl.has_key('url'):
                if not rawurl['url'] in I2:
                    if not rawurl.has_key('parent_url'):
                        rawurl.update({'parent_url':relink})
                    links.extend([rawurl])
                    I2.append(rawurl['url'])
    return links

def _(links):
    uniquelinks=[]
    urllist=[]
    for parurl in links:
        if isinstance(parurl,dict):
            for k,message in parurl.items():
                #依次取出所有元素判断该url是否被访问过
                if k=='url':
        #判断是否为绝对地址
                    message=str(message)
                    pattern=re.compile(r'(?:http.+|www.+).+')
                    match=re.search(pattern,message)
                    if not match:
                        message=os.path.join(settings.domain,message)
        #message=urllib.quote(message)
                    
                    if not task_queue.checkvisited(message):
                        parurl['url']=message
                        urllist.append(message)
                        uniquelinks.append(parurl)

class PostFilterMiddleware(object):
    """
        openerMiddleware是用来调用打开一个url所需要的配置
        从用户自定义的opener.py中读取BaseOpener的子类，该类必须实例化，否则报错
    """
    def process_postfilter(self,urldict,rawlinks):
        
       
        linksdict=_get_rid_of_dups(rawlinks)
        _(linksdict)