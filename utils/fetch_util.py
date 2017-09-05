# coding=utf8

import Queue
import re
import traceback

import HTMLParser

import string

queue = Queue.Queue()


class extractor(object):
    '''两个函数两个功能'''

    # 提取key-value类型的数据
    # 提取单一一个value
    # 列表返回
    @classmethod
    def simpleExtractorAsList(cls, regx, content, *args, **kwargs):
        try:
            uniques = []

            regx = re.compile(regx)
            templist = re.findall(regx, content)
            uniques.extend(templist)
            return uniques
        except:
            print " [x] Error occor"
            traceback.print_exc()

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
                except Exception:
                    error = traceback.format_exc()
                    print error

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
        match = re.search(pattern, kwargs['url'])
        if match:
            return True
        return False


def removeSpecialChar(cls, content):
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


def strip_tags(cls, html):
    """
    Python中过滤HTML标签的函数
    >>> str_text=strip_tags("<font color=red>hello</font>")
    >>> print str_text
    hello
    """
    html = html.strip()
    html = html.strip("\n")
    result = []
    parser = HTMLParser()
    parser.handle_data = result.append
    parser.feed(html)
    parser.close()
    return ''.join(result)


def remove_duplicate(rawlinklist):
    links = []
    chked_url = []

    def from_iterable(iterables):
        # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
        for it in iterables:
            yield it

    for rawurl in from_iterable(rawlinklist):
        if isinstance(rawurl, (str, unicode)):
            if rawurl not in chked_url:
                links.extend([{'url': rawurl}])
                chked_url.append(rawurl)
        else:
            if isinstance(rawurl, dict) and 'url' in rawurl:
                if not rawurl['url'] in chked_url:
                    links.extend([rawurl])
                    chked_url.append(rawurl['url'])
    return links
