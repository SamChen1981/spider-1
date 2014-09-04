from __future__ import unicode_literals

import logging
import sys
import types
import os

from django import http
from django.conf import settings
from django.core import exceptions
from django.core import urlresolvers
from django.core import signals
from django.utils.encoding import force_text
from django.utils.importlib import import_module
from django.utils import six
from django.views import debug
from spider.utils.module_loading import import_string
from spider.core.exceptions import ImproperlyConfigured
from spider.staging import staging
from spider.msgsystem import msgsys

logger = logging.getLogger('django.request')
import re
def _(links):
    '''
           这个函数的功能是将下一级的链接加入到队列中去 ，并且，把这些链接标记成已访问，
          此函数会在settings.MSGSYS_BACKEND和settings.STAGING_BACKEND中找到消息队列的后端
          和暂存区的后端，默认的消息队列后端和暂存区后端分别是rabbitmq和mongodb
    '''
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
                    
                    if not staging.checkvisited(message):
                        parurl['url']=message
                        urllist.append(message)
                        uniquelinks.append(parurl)
                            
           
                
    msgsys.put(uniquelinks)
                
    for link in urllist:
        staging.add(link)
            
class BaseHandler(object):
    # Changes that are always applied to a response (in this order).
    response_fixes = [
        http.fix_location_header,
        http.conditional_content_removal,
    ]

    def __init__(self):
        self._request_middleware =_opener_middleware=self._view_middleware = self._template_response_middleware = self._response_middleware = self._exception_middleware = None

    def load_middleware(self):
        """
        Populate middleware lists from settings.MIDDLEWARE_CLASSES.

        Must be called after the environment is fixed (see __call__ in subclasses).
        """
        self._view_middleware = []
        self._template_response_middleware = []
        self._response_middleware = []
        self._exception_middleware = []
        self._postfilter_middleware=[]
        request_middleware = []
        for middleware_path in settings.MIDDLEWARE_CLASSES:
            try:
                mw_module, mw_classname = middleware_path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured('%s isn\'t a middleware module' % middleware_path)
            try:
                mod = import_module(mw_module)
            except ImportError as e:
                raise exceptions.ImproperlyConfigured('Error importing middleware %s: "%s"' % (mw_module, e))
            try:
                mw_class = getattr(mod, mw_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured('Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname))
            try:
                mw_instance = mw_class()
            except exceptions.MiddlewareNotUsed:
                continue

          
            if hasattr(mw_instance, 'process_filter'):
                self._filter_middleware.append(mw_instance.process_view)
            if hasattr(mw_instance, 'process_postfilter'):
                self._postfilter_middleware.append(mw_instance.process_view)
            if hasattr(mw_instance, 'process_preopen'):
                self.url_preopenermiddleware.append(mw_instance.process_preopen)      
            if hasattr(mw_instance, 'process_open'):
                self.url_openermiddleware.append(mw_instance.process_open)   
            if hasattr(mw_instance, 'process_parser'):
                self.url_parserermiddleware.append(mw_instance.process_parse)   
            if hasattr(mw_instance, 'process_save'):
                self.url_savemiddleware.append(mw_instance.process_save)   
                            
        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._request_middleware = request_middleware
    def go_get_it(self,urldict):
        #Apply opener middleware
        
        urldict.update({'openers':self.url_openermiddleware})
        for middleware_method in self.url_preopenermiddleware:
            middleware_method(urldict)
        for middleware_method in self.url_openermiddleware:
            
            con=middleware_method(urldict)
            if isinstance(con, tuple) and len(con)==3:
                break

        #filter返回一个当前url下一级的所有链接,可以是list 也可以是dict
        #这里可以根据每个网站的不同自定义抓取的方式，若_filter_middleware为None，将报
        #NotImplement异常,这个过滤链后端必须实现的方法有is_filter(),filter()，分别是
        #1.判断是否要在当前的网页解析下一级的链接,is_filter
        #2.filter 分析这个网页，找到所有下一级的链接
        for middleware_method in self._filter_middleware:
            rawlinks=middleware_method(urldict)
        #postfilter的基本功能:
        #1.对相同链接进行去重
        #2.其他自定义的操作
        
        
        for middleware_method in self._postfilter_middleware:
            middleware_method(rawlinks)
        
        #将上面的rawlinks，就是下一级要抓取的链接加入到队列中和暂存区
        _(rawlinks)
        #调用解析后端对当前的链接信息进行分析，这个操作是预分析，只是将当前页面的
        #需要的内容做一个截取，包括对当前网页内容的解析，返回一个包含已经当前页面已经有的
        #信息的字典
        #解析后端需要实现的方法有isparse(),parse(),save(),分别是
        #1.判断当前页面是否需要解析,返回True or False，传入当前的link和content
        #2.解析当前网页，返回一个字典
        #3.存储信息，将parse()中返回的字典传入save中，用户可以自定义一个存储后端
        
        #默认的操作是进行分词处理，并建立倒排索引
        #规则是<docid,[(word1,TF),(word2,TF)...]>
        for middleware_method in self._parse_middleware:
            middleware_method(rawlinks)
        
        #保存页面的middleware,遍历所有保存页面的后端，
        for middleware_method in self.url_savemiddleware:
            middleware_method(urldict)    
        
        
            
    def get_response(self, request):
        "Returns an HttpResponse object for the given HttpRequest"
        try:
            # Setup default url resolver for this thread, this code is outside
            # the try/except so we don't get a spurious "unbound local
            # variable" exception in the event an exception is raised before
            # resolver is set
            urlconf = settings.ROOT_URLCONF
            urlresolvers.set_urlconf(urlconf)
            resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
            try:
                response = None
                # Apply request middleware
                for middleware_method in self._request_middleware:
                    response = middleware_method(request)
                    if response:
                        break

                if response is None:
                    if hasattr(request, 'urlconf'):
                        # Reset url resolver with a custom urlconf.
                        urlconf = request.urlconf
                        urlresolvers.set_urlconf(urlconf)
                        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

                    resolver_match = resolver.resolve(request.path_info)
                    callback, callback_args, callback_kwargs = resolver_match
                    request.resolver_match = resolver_match

                    # Apply view middleware
                    for middleware_method in self._view_middleware:
                        response = middleware_method(request, callback, callback_args, callback_kwargs)
                        if response:
                            break

                if response is None:
                    try:
                        response = callback(request, *callback_args, **callback_kwargs)
                    except Exception as e:
                        # If the view raised an exception, run it through exception
                        # middleware, and if the exception middleware returns a
                        # response, use that. Otherwise, reraise the exception.
                        for middleware_method in self._exception_middleware:
                            response = middleware_method(request, e)
                            if response:
                                break
                        if response is None:
                            raise

                # Complain if the view returned None (a common error).
                if response is None:
                    if isinstance(callback, types.FunctionType):    # FBV
                        view_name = callback.__name__
                    else:                                           # CBV
                        view_name = callback.__class__.__name__ + '.__call__'
                    raise ValueError("The view %s.%s didn't return an HttpResponse object." % (callback.__module__, view_name))

                # If the response supports deferred rendering, apply template
                # response middleware and the render the response
                if hasattr(response, 'render') and callable(response.render):
                    for middleware_method in self._template_response_middleware:
                        response = middleware_method(request, response)
                    response = response.render()

            except http.Http404 as e:
                logger.warning('Not Found: %s', request.path,
                            extra={
                                'status_code': 404,
                                'request': request
                            })
                if settings.DEBUG:
                    response = debug.technical_404_response(request, e)
                else:
                    try:
                        callback, param_dict = resolver.resolve404()
                        response = callback(request, **param_dict)
                    except:
                        signals.got_request_exception.send(sender=self.__class__, request=request)
                        response = self.handle_uncaught_exception(request, resolver, sys.exc_info())
            except exceptions.PermissionDenied:
                logger.warning(
                    'Forbidden (Permission denied): %s', request.path,
                    extra={
                        'status_code': 403,
                        'request': request
                    })
                try:
                    callback, param_dict = resolver.resolve403()
                    response = callback(request, **param_dict)
                except:
                    signals.got_request_exception.send(
                            sender=self.__class__, request=request)
                    response = self.handle_uncaught_exception(request,
                            resolver, sys.exc_info())
            except SystemExit:
                # Allow sys.exit() to actually exit. See tickets #1023 and #4701
                raise
            except: # Handle everything else, including SuspiciousOperation, etc.
                # Get the exception info now, in case another exception is thrown later.
                signals.got_request_exception.send(sender=self.__class__, request=request)
                response = self.handle_uncaught_exception(request, resolver, sys.exc_info())
        finally:
            # Reset URLconf for this thread on the way out for complete
            # isolation of request.urlconf
            urlresolvers.set_urlconf(None)

        try:
            # Apply response middleware, regardless of the response
            for middleware_method in self._response_middleware:
                response = middleware_method(request, response)
            response = self.apply_response_fixes(request, response)
        except: # Any exception should be gathered and handled
            signals.got_request_exception.send(sender=self.__class__, request=request)
            response = self.handle_uncaught_exception(request, resolver, sys.exc_info())

        return response

    def handle_uncaught_exception(self, request, resolver, exc_info):
        """
        Processing for any otherwise uncaught exceptions (those that will
        generate HTTP 500 responses). Can be overridden by subclasses who want
        customised 500 handling.

        Be *very* careful when overriding this because the error could be
        caused by anything, so assuming something like the database is always
        available would be an error.
        """
        if settings.DEBUG_PROPAGATE_EXCEPTIONS:
            raise

        logger.error('Internal Server Error: %s', request.path,
            exc_info=exc_info,
            extra={
                'status_code': 500,
                'request': request
            }
        )

        if settings.DEBUG:
            return debug.technical_500_response(request, *exc_info)

        # If Http500 handler is not installed, re-raise last exception
        if resolver.urlconf_module is None:
            six.reraise(*exc_info)
        # Return an HttpResponse that displays a friendly error message.
        callback, param_dict = resolver.resolve500()
        return callback(request, **param_dict)

    def apply_response_fixes(self, request, response):
        """
        Applies each of the functions in self.response_fixes to the request and
        response, modifying the response in the process. Returns the new
        response.
        """
        for func in self.response_fixes:
            response = func(request, response)
        return response


def get_path_info(environ):
    """
    Returns the HTTP request's PATH_INFO as a unicode string.
    """
    path_info = environ.get('PATH_INFO', str('/'))
    # Under Python 3, strings in environ are decoded with ISO-8859-1;
    # re-encode to recover the original bytestring provided by the webserver.
    if six.PY3:
        path_info = path_info.encode('iso-8859-1')
    # It'd be better to implement URI-to-IRI decoding, see #19508.
    return path_info.decode('utf-8')


def get_script_name(environ):
    """
    Returns the equivalent of the HTTP request's SCRIPT_NAME environment
    variable. If Apache mod_rewrite has been used, returns what would have been
    the script name prior to any rewriting (so it's the script name as seen
    from the client's perspective), unless the FORCE_SCRIPT_NAME setting is
    set (to anything).
    """
    if settings.FORCE_SCRIPT_NAME is not None:
        return force_text(settings.FORCE_SCRIPT_NAME)

    # If Apache's mod_rewrite had a whack at the URL, Apache set either
    # SCRIPT_URL or REDIRECT_URL to the full resource URL before applying any
    # rewrites. Unfortunately not every Web server (lighttpd!) passes this
    # information through all the time, so FORCE_SCRIPT_NAME, above, is still
    # needed.
    script_url = environ.get('SCRIPT_URL', environ.get('REDIRECT_URL', str('')))
    if script_url:
        script_name = script_url[:-len(environ.get('PATH_INFO', str('')))]
    else:
        script_name = environ.get('SCRIPT_NAME', str(''))
    # Under Python 3, strings in environ are decoded with ISO-8859-1;
    # re-encode to recover the original bytestring provided by the webserver.
    if six.PY3:
        script_name = script_name.encode('iso-8859-1')
    # It'd be better to implement URI-to-IRI decoding, see #19508.
    return script_name.decode('utf-8')
