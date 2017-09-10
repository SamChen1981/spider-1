# encoding=utf8
from __future__ import unicode_literals

import importlib
import requests

from spider.conf import settings

from spider import constant
from spider import exceptions
from spider.msgsystem import msgsys
from spider.utils import fetch_util
from spider.utils.log import logger


def next_page(links):
    msgsys.put(links)


class BaseHandler(object):
    # Changes that are always applied to a response (in this order).

    def __init__(self):
        self._filter_middleware = []
        self._postfilter_middleware = []
        self.url_preopenermiddleware = []
        self.url_openermiddleware = []
        self.url_parserermiddleware = []
        self.url_savemiddleware = []

    def load_middleware(self):

        for middleware_path in settings.MIDDLEWARE_CLASSES:
            logger.debug("middleware_path: {0}".format(middleware_path))
            try:
                mw_module, mw_classname = middleware_path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured(
                    '%s isn\'t a middleware module' % middleware_path)
            try:
                mod = importlib.import_module(mw_module)
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
            except exceptions.MiddlewareNotUsed as e:
                logger.error(e)
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

    def go_get_it(self, url_body):
        try:
            for middleware_method in self.url_preopenermiddleware:
                middleware_method(url_body)
            for middleware_method in self.url_openermiddleware:
                content = middleware_method(url_body)
                url_body[constant.RESPONSE_SIGNATURE] = content
                logger.debug(url_body[constant.RESPONSE_SIGNATURE])
            # filter返回一个当前url下一级的所有链接,可以是list 也可以是dict
            # 这里可以根据每个网站的不同自定义抓取的方式，若_filter_middleware为None，将报
            # NotImplement异常,这个过滤链后端必须实现的方法有is_filter(),filter()，分别是
            # 1.判断是否要在当前的网页解析下一级的链接,is_filter
            # 2.filter 分析这个网页，找到所有下一级的链接
            for middleware_method in self._filter_middleware:
                middleware_method(url_body)
            for middleware_method in self.url_parserermiddleware:
                middleware_method(url_body)
            for middleware_method in self._postfilter_middleware:
                middleware_method(url_body)
            for middleware_method in self.url_savemiddleware:
                middleware_method(url_body)
            # 将上面的rawlinks，就是下一级要抓取的链接加入到队列中和暂存区
            if constant.RAW_LINKS in url_body:
                refined_links = fetch_util.refine_links(
                    url_body[constant.RAW_LINKS])
                next_page(refined_links)
        except requests.exceptions.InvalidSchema as e:
            logger.error(e)
