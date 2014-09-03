'''
Created on 2014年9月2日

@author: mu
'''
from spider.save_page import Storage
from HTMLParser import HTMLParser
  
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
        pass
    def parser(self,urldict):
        '''   
            解析成倒排列表
            1.对content去除html标签
            2.用分词器对其进行分词，
            3.统计每个词出现的频率，
        '''
        
        content=_get_rid_of_html()
        
    def save(self,urldict):
        Storage().save(urldict['content'])
        
        urldict['content']
        pass
