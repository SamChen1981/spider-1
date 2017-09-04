# encoding=utf8
from __future__ import unicode_literals

import os

from spider.conf import settings

from spider.utils.importlib import import_module
from spider import exceptions
from spider.staging import staging
from spider.msgsystem import msgsys

import re


def next_page(links):
    '''这个函数的功能是将下一级的链接加入到队列中去 ，并且，把这些链接标记成已访问，
    此函数会在settings.MSGSYS_BACKEND和settings.STAGING_BACKEND中找到消息队列的后端
          和暂存区的后端，默认的消息队列后端和暂存区后端分别是rabbitmq和mongodb
    '''
    uniquelinks = []
    urllist = []
    for parurl in links:
        if isinstance(parurl, dict):
            for k, message in parurl.items():
                # 依次取出所有元素判断该url是否被访问过
                if k == 'url':
                    # 判断是否为绝对地址
                    message = str(message)
                    pattern = re.compile(r'(?:http.+|www.+).+')
                    match = re.search(pattern, message)
                    if not match:
                        message = os.path.join(settings.DOMAIN, message)
                    # message=urllib.quote(message)

                    if not staging.checkvisited(message):
                        parurl['url'] = message
                        urllist.append(message)
                        uniquelinks.append(parurl)
    msgsys().put(uniquelinks)
    for link in urllist:
        staging.add(link)


class BaseHandler(object):
    # Changes that are always applied to a response (in this order).

    def __init__(self):
        self._filter_middleware = []
        self._template_response_middleware = []
        self._response_middleware = []
        self._exception_middleware = []
        self._postfilter_middleware = []
        self.url_preopenermiddleware = []
        self.url_openermiddleware = []
        self.url_parserermiddleware = []
        self.url_savemiddleware = []

    def load_middleware(self):

        for middleware_path in settings.MIDDLEWARE_CLASSES:
            try:
                mw_module, mw_classname = middleware_path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured(
                    '%s isn\'t a middleware module' % middleware_path)
            try:
                mod = import_module(mw_module)
            except ImportError as e:
                raise exceptions.ImproperlyConfigured(
                    'Error importing middleware %s: "%s"' % (mw_module, e))
            try:
                mw_class = getattr(mod, mw_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured(
                    'Middleware module "%s" does not define a "%s" class' % (
                        mw_module, mw_classname))
            try:
                mw_instance = mw_class()
            except exceptions.MiddlewareNotUsed:
                continue

            if hasattr(mw_instance, 'process_filter'):
                self._filter_middleware.append(mw_instance.process_filter)
            if hasattr(mw_instance, 'process_postfilter'):
                self._postfilter_middleware.append(
                    mw_instance.process_postfilter)
            if hasattr(mw_instance, 'process_preopen'):
                self.url_preopenermiddleware.append(
                    mw_instance.process_preopen)
            if hasattr(mw_instance, 'process_open'):
                self.url_openermiddleware.append(mw_instance.process_open)
            if hasattr(mw_instance, 'process_parser'):
                self.url_parserermiddleware.append(
                    mw_instance.process_parser)
            if hasattr(mw_instance, 'process_save'):
                self.url_savemiddleware.append(mw_instance.process_save)

    def go_get_it(self, **kwargs):
        for middleware_method in self.url_preopenermiddleware:
            middleware_method(kwargs)
        for middleware_method in self.url_openermiddleware:
            con = middleware_method(kwargs)
            if isinstance(con, tuple) and len(con) == 3:
                break
        # filter返回一个当前url下一级的所有链接,可以是list 也可以是dict
        # 这里可以根据每个网站的不同自定义抓取的方式，若_filter_middleware为None，将报
        # NotImplement异常,这个过滤链后端必须实现的方法有is_filter(),filter()，分别是
        # 1.判断是否要在当前的网页解析下一级的链接,is_filter
        # 2.filter 分析这个网页，找到所有下一级的链接
        if len(self._filter_middleware) == 0:
            raise NotImplementedError()
        rawlinks = []
        for middleware_method in self._filter_middleware:
            rawlinks = middleware_method(urldict)
        # postfilter的基本功能:
        # 1.对相同链接进行去重
        # 2.其他自定义的操作
        for middleware_method in self._postfilter_middleware:
            middleware_method(urldict, rawlinks)
        # 将上面的rawlinks，就是下一级要抓取的链接加入到队列中和暂存区
        next_page(rawlinks)
