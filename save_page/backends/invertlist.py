# encoding=utf8
import logging
import time
import os
import re
import uuid

from datetime import datetime
from spider.utils.log import logger


def saveHTML(content, **kwargs):
    '''
      保存html.会根据settings.py提供的正则保存
    '''
    url = kwargs['url']
    file_ext = ".html"
    # 以/从最右边分割开始，助剂建立目录建立目录
    dirstr = url.rsplit('/', 1)[0]
    # 去掉http://
    pattern = re.compile(r'http://')
    dirstr = re.sub(pattern, '', dirstr)
    # 去掉http://
    pattern = re.compile(r'https://')
    dirstr = re.sub(pattern, '', dirstr)
    # 去掉换行符
    pattern = re.compile(r'\n')
    dirstr = re.sub(pattern, '', dirstr)
    # 再根据dirstr以/划分
    current_date = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
    top_dir = os.path.join(os.getcwd(), dirstr)
    top_dir = os.path.join(top_dir, current_date)
    try:
        if not os.path.exists(top_dir):
            os.makedirs(top_dir)
    except OSError as e:
        if e.errno == os.errno.EEXIST:
            message = "'%s' already exists" % top_dir
            logger.error(message)
        else:
            message = e
            print message
            logging.info(message)
        return -1

    filepath = os.path.join(top_dir, str(uuid.uuid4()) + file_ext)
    write_txt_into_file(content, filepath)
    logger.info('The file is saved into %s' % filepath)


def write_txt_into_file(content, filepath):
    with open(filepath, 'wt') as f:
        f.write(content)


def download_file(content, filepath):
    with open(filepath, 'wb') as f:
        for chunk in content.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


class SavePageBackend(object):
    def saveHTML(self, content, **kwargs):
        saveHTML(content, **kwargs)
