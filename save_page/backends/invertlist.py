# encoding=utf8
import logging
import time
import os
import StringIO
import re

from datetime import datetime

logger = logging.getLogger(__name__)


def saveHTML(*args, **kwargs):
    '''
      保存html.会根据settings.py提供的正则保存
    '''
    realurl = kwargs['realurl']
    url = kwargs['url']

    content = kwargs['content']

    # 以/从最右边分割开始，助剂建立目录建立目录
    dirstr = url.rsplit('/', 1)[0]
    # 去掉http://
    pattern = re.compile(r'http://')
    # 去掉换行符

    dirstr = re.sub(pattern, '', dirstr)
    pattern = re.compile(r'\n')
    dirstr = re.sub(pattern, '', dirstr)
    # 再根据dirstr以/划分
    dircomponent = dirstr.split('/')
    top_dir = os.path.join(os.getcwd(), dirstr)
    try:
        if not os.path.exists(top_dir):
            os.makedirs(top_dir)
    except OSError as e:
        if e.errno == os.errno.EEXIST:
            message = "'%s' already exists" % top_dir
            print message
            logging.info(message)  # will not print anything
        else:
            message = e
            print message
            logging.info(message)
        return -1
    filepath = os.path.join(top_dir,
                            datetime.fromtimestamp(time.time()).strftime(
                                '%Y-%m-%d:%H:%M:%S') + '.html')
    print 'THE SAVE LOCATION IS %s' % filepath
    output = StringIO.StringIO()
    output.write(content)


class SavePageBackend(object):
    """
        根据用户提供的url的正则表达式 ，判断某一个url是否应该保存
        用户应该提供:
        1.具体的页面存放backend,如没有提供，默认是保存于磁盘上，id 是路径的和时间的 md5
        2.判定的url ,一个list 或者itertable，如果目前的url匹配任意一个，则认为这个url应该保存，如果是[*]
        则保存所有遇到的页面，如果是[!]，不保存任何页面。
    """

    def saveHTML(self, content, **kwargs):
        saveHTML(**kwargs)
