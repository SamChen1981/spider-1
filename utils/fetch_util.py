# coding=utf8

import re
import HTMLParser
import string
import os

from spider.conf import settings
from spider.utils.log import logger
from spider.staging import staging


class Extractor(object):
    '''两个函数两个功能'''

    # 提取key-value类型的数据
    # 提取单一一个value
    # 列表返回
    @classmethod
    def simpleExtractorAsList(cls, regx, content, *args, **kwargs):
        uniques = []
        try:
            regx = re.compile(regx)
            templist = re.findall(regx, content)
            uniques.extend(templist)
            return uniques
        except Exception as e:
            logger.error(" [x] Error occor")
            logger.exception(e)
        return uniques

    @classmethod
    def getItemAsValue(cls, content, regx, index, *args, **kwargs):
        if not content or not regx:
            return -1
        pattern = re.compile(regx)
        match = re.search(pattern, content)
        # 取得表格HTML内容
        if isinstance(index, tuple):
            values = []

            for ind in index:
                try:

                    values.append(match.group(ind))
                except Exception as e:
                    logger.exception(e)
            return values

        if isinstance(index, (str, int)):
            result = ''
            try:
                result = match.group(index)
            except:
                pass
            return result


# 过滤类，用户需要根据具体情况重写该类，该类也提供一个函数用于检查一个url是否和给定的正则表达式相同
class urlFilter(object):
    def __init__(self, regx):
        self.regx = regx

    @classmethod
    def matchurl(cls, *args, **kwargs):
        if not kwargs['url']:
            return False
        if kwargs['regx'] == '' or not kwargs['regx']:
            return False
        if isinstance(kwargs['regx'], (tuple, list)):
            for r in kwargs['regx']:

                pattern = re.compile(r)
                url = string.strip(kwargs['url'])
                match = re.search(pattern, kwargs['url'])
                if match:
                    return True
        if isinstance(kwargs['regx'], str):
            pattern = re.compile(kwargs['regx'])
            url = string.strip(kwargs['url'])
            match = re.search(pattern, kwargs['url'])
            if match:
                return True

        return False


# 规则类，用户需要在子类中自定义规则，目前提供了一个函数，检查一个url是否和给定的正则表达式相同
class Rule(object):
    @classmethod
    def matchurl(cls, *args, **kwargs):
        if not kwargs['url']:
            return False
        if kwargs['regx'] == '' or not kwargs['regx']:
            return False
        pattern = re.compile(kwargs['regx'])
        url = string.strip(kwargs['url'])
        match = re.search(pattern, url)
        if match:
            return True
        return False


def remove_special_char(content):
    pattern = re.compile(r'.*?(").*?')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'：')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r':')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'-')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r' ')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'\'')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'/')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'\t')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'\n')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'<')
    content = re.sub(pattern, '', content)
    pattern = re.compile(r'>')
    content = re.sub(pattern, '', content)
    return content


def from_iterable(cls, iterables):
    for it in iterables:
        yield it


def strip_tags(html):
    """
    Python中过滤HTML标签的函数
    >>> str_text=strip_tags("<font color=red>hello</font>")
    >>> print str_text
    hello
    """
    html = html.strip()
    html = html.strip("\n")
    result = []
    parser = HTMLParser.HTMLParser()
    parser.handle_data = result.append
    parser.feed(html)
    parser.close()
    return ''.join(result)


def check_visited(rawurl):
    return staging.checkvisited(rawurl)


def process_add_domain_to_link(parurl, domain):
    parurl = str(parurl)
    pattern = re.compile(r'(?:http.+|www.+).+')
    match = re.search(pattern, parurl)
    if not match:
        parurl = os.path.join(domain, parurl)
    return parurl


def process_route_key_to_link(parurl, route_key, domain):
    process_add_domain_to_link(parurl, domain)
    if not isinstance(parurl, dict):
        parurl = {"url": parurl}

    if "route_key" not in parurl:
        parurl["route_key"] = route_key
    return parurl


def tag_info_to_links(route_key, domain, links):
    """给每个待抓取的Link打route_key

    :param route_key:
    :param links: dict 类型
    :return:
    """
    import functools
    links = map(functools.partial(process_route_key_to_link,
                                  route_key=route_key,
                                  domain=domain
                                  ),
                links)
    return links


def refine_links(rawlinklist):
    # 去除重复
    links = list(set(rawlinklist))
    # 访问过的url不再访问
    links = filter(check_visited, links)
    # 给url打标签
    links = tag_info_to_links(settings.RABBITMQ_QUEUE, settings.DOMAIN, links)
    logger.info("refined links: {0}".format(links))
    return links
