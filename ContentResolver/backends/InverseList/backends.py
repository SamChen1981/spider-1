'''
Created on 2014年9月2日

@author: mu
'''
from spider.save_page import PageSave
from HTMLParser import HTMLParser
import StringIO  
from spider.ContentResolver.backends.InverseList.pylucene_test import luceneIndexer


from datetime import datetime
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
  
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def _get_rid_of_html(content):
    '''
        去除html标签
    '''
    return strip_tags(content)
class Inverted_List(object):
    def is_parser(self,urldict):
        return True
    def parser(self,urldict):
        '''   
            解析成倒排列表
            用pylucene对每个content建立索引
            索引索引默认存放于磁盘上，路径由settings指定
        '''
        
        content=_get_rid_of_html()
        output=StringIO.StringIO(content)
        docid=luceneIndexer([output])
        urldict.update({'indexid':docid})

