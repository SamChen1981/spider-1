#coding=utf8
import sys
from taskqueue import task_queue
from download import *
from datetime import *
import fetch_util
from fetch_util import *
from urlparse import urljoin
reload(sys)
import json
import threading
from HTMLParser import HTMLParser
from decorator import *
sys.setdefaultencoding('utf8')
import settings
#扩展的过滤器
class filter_url(urlFilter):
    test='ssssssssssssssssssss'
    '''
       过滤器类
    '''
    def __init__(self,*args,**kwargs):
        self.reglist=SETTING.reglist
        self.count=SETTING.count1
        self.local_flag=SETTING.local_flag
        self.LOCALPATH_QUEUE=SETTING.LOCALPATH_QUEUE
        self.dlregx=SETTING.dlregx
        self.save_dir=SETTING.save_dir
        self.is_javascript=SETTING.is_javascript
        self.page_save_reglist=SETTING.page_save_reglist
        try:
            self.exchange_name=SETTING.exchange_name
            self.page_save_reglist=SETTING.page_save_reglist
        except:
            pass
    #打开一个链接


    def openlink(self,reglist,url,parno,**kwargs):
        if not urlFilter.matchurl(**{'regx':reglist,'url':url}):
            return ''
        fetch=Fetch_WebContent()
        return fetch.getAllContent(**kwargs)


    def prefilter_open(self,urlpack):
        if not urlFilter.matchurl(**{'regx':SETTING.reglist,'url':self.relink}):
            return ''
        fetch=Fetch_WebContent()
        con=fetch.getAllContent(self.relink,**urlpack)
        #con=fetch.getAllContent(self.relink,partno=self.partno)
        if isinstance(con,tuple):

            urlpack.update({'content':con[0]})
            urlpack.update({'realurl':con[1]})
            try:
                urlpack.update({'localpath':con[2]})
            except:
                urlpack.update({'localpath':''})
        if urlpack['content']==-1:
            print '未能获取到数据，将退出...'
            return

    def prefilter_0(self,urlpack):
        if isinstance(urlpack,dict):
            self.relink=urlpack['url']
            self.flag=urlpack['flag']
            self.unpacked_url=urlpack
            try:
                self.partno=urlpack['partno']
            except:
                self.partno=''
        elif isinstance(self.urlpack,(str,unicode)):
            self.relink=json.loads(urlpack)['url']
            try:
                self.partno=json.loads(urlpack)['partno']
            except:
                self.partno=''
            self.flag=json.loads(urlpack)['flag']
            self.unpacked_url=json.loads(urlpack)
        #self.content=self.openlink(reglist=self.reglist,url=self.relink,local_flag=self.local_flag,**{'filepath':self.filepath,'is_javascript':self.is_javascript,'dlregx':self.dlregx,'save_dir':self.save_dir,'LOCALPATH_QUEUE':self.LOCALPATH_QUEUE,'page_save_reglist':self.page_save_reglist})

        #if self.content:
        #    task_queue.sendtask2BDB([filepath],self.LOCALPATH_QUEUE,exchange_name='',mqtype='RABBIT',**{'count':10})

    #启动过滤链
    @url_decorator
    def processChain(self,urlpack):
        '''
        本函数负责一次启动prefilter_*,filter_*,postfilter_*函数
        prefilter_*(urlpack)
        filter_*(urlpack)
        postfilter_*(urlpack,link)
        urlpack为字典，可以在函数中修改，urlpack只有一个实例，任何影响这个实例的操作都会对最终的parurl字典产生影响。
        '''
        dictlinks=[]
        rawlinklist=[]
        links=[]
        for attr in dir(self):
            if attr.startswith('prefilter_'):
                if callable(getattr(self,attr)):
                    getattr(self,attr)(urlpack)

        for attr in dir(self):
            if attr.startswith('filter_'):

                rawlinklist.extend(getattr(self,attr)(urlpack))
        if self.local_flag==1:
            I2=rawlinklist
        else:
            I2=[]
        for rawurl in db.from_iterable(rawlinklist):
            if isinstance(rawurl,(str,unicode)):
                if not rawurl in I2:

                    links.extend([{'url':rawurl,'parent_url':self.relink}])
                    I2.append(rawurl)
            else:
                if isinstance(rawurl,dict) and rawurl.has_key('url'):
                    if not rawurl['url'] in I2:
                        if not rawurl.has_key('parent_url'):
                            rawurl.update({'parent_url':self.relink})
                        links.extend([rawurl])
                        I2.append(rawurl['url'])

        for attr in dir(self):
            if attr.startswith('postfilter_'):
                getattr(self,attr)(urlpack,links)
                #if len(links)>0:
                #    break
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
                            message=urljoin(SETTING.domain,message)
            #message=urllib.quote(message)

                        if not task_queue.checkvisited(message):
                            parurl['url']=message
                            urllist.append(message)
                            uniquelinks.append(parurl)
        if len(uniquelinks)>0:
            if SETTING.SPEC_FLAG and isinstance(SETTING.SPEC_FLAG,(unicode,str)):
                task_queue.sendtask2BDB(uniquelinks,SETTING.SPEC_FLAG,mqtype='RABBIT',exchange_name=self.exchange_name)
            else:
                task_queue.sendtask2BDB(uniquelinks,SETTING.flag,mqtype='RABBIT',exchange_name=self.exchange_name)


        task_queue.savevisitedURL(urllist)
        if SETTING.DEBUG:
            print 'THE NEWLY ADDED URL IS %s ' % len(uniquelinks)
            print 'add queue %s' % self.flag
        # if isinstance(parurl,str):
            #     rawlinks=[]
            #     #判断是否为绝对地址
            #     pattern=re.compile(r'(?:http.+|www.+).+')
            #     match=re.search(pattern,message)
            #     if not match:
            #         message=urljoin(self.domain,message)
            #         rawlinks.append(message)
            #     uniquelinks=task_queue.savevisitedURL(rawlinks)

            #    task_queue.sendtask2BDB(uniquelinks,self.flag)


        return

class rule1(Rule):
    count=0
    def __init__(self,*args,**kwargs):
        #self.link=kwargs['link']
        #初始化下载匹配模式
        self.dlregx=kwargs['dlregx']
        #初始化数据库匹配模式
        self.dbregx=kwargs['dbregx']
        #初始化解析匹配模式
        self.prregx=kwargs['prregx']
        #初始化表
        #数据库名
        self.dbname=kwargs['dbname']
        #初始化主机
        self.host=kwargs['host']
        #初始化用户
        self.user=kwargs['user']
        #初始化密码
        self.passwd=kwargs['passwd']
        #初始化保存的文件名
        self.filename=kwargs['filename']
        self.saved_field=kwargs['saved_field']
        #下载队列
        try:
            self.DOWNLOAD_QUEUE=kwargs['DOWNLOAD_QUEUE']
        except:
            pass
        #初始化下载标志,0表示和不下载，1表示下载
        self.downloadtag=kwargs['downloadtag']
#保存抓取的记录到数据库
    def save_db(self,table,*args,**kwargs):
        if kwargs['result'].has_key('dbinfopack'):
            if isinstance(kwargs['result']['dbinfopack'],dict):
                dbinfopack=kwargs['result']['dbinfopack']
                dbname=dbinfopack.get('dbname','')
                table=dbinfopack.get('table','')
                host=dbinfopack.get('host','')
                passwd=dbinfopack.get('passwd','')
                user=dbinfopack.get('user','')
                del kwargs['result']['dbinfopack']
            else:
                dbname=self.dbname
                table=table
                host=self.host
                user=self.user
                passwd=self.passwd
        else:
            dbname=self.dbname
            table=table
            host=self.host
            user=self.user
            passwd=self.passwd
        if not table and table=='':
            return
        for r in self.dbregx:
            if SETTING.DEBUG:
                print '正在执行数据库操作...'
            #if not Rule.matchurl(url=link,regx=r):
            #    continue
            #db.init_conn(DB=self.dbname,host=self.host,user=self.user,passwd=self.passwd)
            #测试字段是否存在
            for k,v in kwargs['result'].items():
                res=db.checkexist('SHOW COLUMNS FROM `'+table+'` WHERE field =\''+k+'\'',**{'field':(k,),'host':host,'user':user,'passwd':passwd,'db':dbname})
                if not res:
                    #altersql='alter table '+table+' add '+k+' varchar('+str(len(v)*2)+')'
                    altersql='alter table %s add `%s` varchar(%s)' %(table,k.encode('utf8'),len(v)*3)

                    print '字段不存在，正在创建中... %s' %altersql  
                    db.execute_sql_without_ret([altersql,[]],1,**{'host':host,'passwd':passwd,'db':dbname,'user':user})

            sql=db.insert_kwargs(table,**kwargs['result'])
            if not isinstance(sql,(list,tuple)):
                raise Exception('GENERATOR SQL FAIL!!!!')
            #sql=db.gen_insert(table,kwargs['result'])
            if args and isinstance(args,tuple):
                update=db.gen_on_duplicate(*args,**{'joiner':','})
                sql[0]=' '.join([sql[0],update])
            if SETTING.DEBUG:
                print 'SQL: %s' %sql
            opresult=db.execute_sql(sql,1,**{'host':host,'passwd':passwd,'db':dbname,'user':user})
            return opresult
    @classmethod
    def extractor_digit(cls,content):
        pattern=re.compile(r'[\s\S]*?([0-9]+)[\s\S]*?')
        value=extractor.getItemAsValue(content,pattern,1)
        value=cls.strip_tags(value)
        return value
    @classmethod
    def extractor_char(cls,content):
        pattern=re.compile(r'[\s\S]*?(\w+)[\s\S]*?')
        value=extractor.getItemAsValue(content,pattern,1)
        value=cls.strip_tags(value)
        return value

    @classmethod
    def extractor_char_digit(cls,content):
        pattern=re.compile(r'[\s\S]*?([a-zA-Z0-9]+)[\s\S]*?')
        value=extractor.getItemAsValue(content,pattern,1)
        value=cls.strip_tags(value)
        return value
    @classmethod
    def removeSpecialChar(cls,content):
        pattern=re.compile(r'.*?(").*?')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'：')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r':')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'-')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r' ')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'\'')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'/')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'\t')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'\n')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'<')
        content=re.sub(pattern,'',content)
        pattern=re.compile(r'>')
        content=re.sub(pattern,'',content)
        return content


    @classmethod
    def strip_tags(cls,html):
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


    def construct_generator(self,*args,**kwargs):
        return ( (key,kwargs[key]) for key in kwargs.keys() )


#解析页面链,该链根据提供的正则匹配过滤后的url,如果匹配，则进行操作
    def preparse_0(self,parurl):
        try:
            l=parurl['realurl']
        except:
            return parurl
        for r in SETTING.page_save_reglist:
            if not Rule.matchurl(url=l,regx=r):
                continue
            parurl.update({'localpath':self.localpath})
            try:
                self.update=parurl['updatefield']
            except:
                self.update=SETTING.updatefield
    def parse_1(self,parurl):
        if not isinstance(self.prregx,(tuple,list)):
            return {}
        if not isinstance(parurl,dict):
            return {}
        if not parurl.has_key('url'):
            return {}

        l=parurl['realurl']
        if SETTING.DEBUG:
            print 'PARSED URL IS %s' % l
        for r in self.prregx:
            if not Rule.matchurl(url=l,regx=r):
                continue
            result={}

            for attr in dir(self):
                if attr.startswith('get_'):
                    subresult=getattr(self,attr)(parurl)
                    if isinstance(subresult,dict):
                        result.update(subresult)
                    else:
                        result.update({attr[4:]:subresult})
            parurl.update(result)
            break
        return parurl


    #下载这个url,这个url
    #可以在子类中重写改函数，因为在大多数情况下不推荐在抓取的过程中下载该文件，建议把该url放入一个消息队列，
    #本系统有一个专门的多线程下载工具可以读取消息队列
    def parse_2(self,parurl):
        if not isinstance(self.dlregx,(tuple,list)):
            return {}
        if not parurl.has_key('url'):
            return {}
        l=parurl['url']
        for r in self.dlregx:
            if not Rule.matchurl(url=l,regx=r):
                continue
            downloadinfo=[]
            for attr in dir(self):
                if attr.startswith('download_'):
                    subresult=[]

                    if callable(getattr(self,attr)):
                        subresult.extend(getattr(self,attr)(parurl))
                    if isinstance(subresult,list) and len(subresult)>0:
                        downloadinfo.extend(subresult)
                    msgs=''
                    for s in subresult:
                        if isinstance(s,dict):
                            msgs+=json.dumps(s,ensure_ascii=False)
                            parurl.update({'DOWNLOAD_PACK':msgs})
                for info in downloadinfo:
                    if len(downloadinfo)==0:
                        break
                    if not isinstance(info,dict):
                        break
                    gen=self.construct_generator(**info)
                if self.downloadtag==0:
                    try:
                        rl=gen.next()
                        rl1=gen.next()
                    except:
                        pass
                    if isinstance(rl,tuple) and isinstance(rl1,tuple):
                        parurl.update({rl[0]:rl[1],rl1[0]:rl1[1]})
                        try:
                            remotelink=rl[1]
                            #locallink=rl1[1]
                            #task_queue.send2downloadBDB(remotelink,filepath=locallink)
                            task_queue.sendtask2BDB([{rl[0]:rl[1],rl1[0]:rl1[1]}],self.DOWNLOAD_QUEUE,exchange_name='',mqtype='RABBIT',**{'count':10})
                            print 'SAVE download link :%s' % remotelink
                        except:
                            pass
                elif self.downloadtag==1:
                    try:
                        rl=gen.next()
                        rl1=gen.next()
                    except:
                        pass
                    if isinstance(rl,tuple):
                        parurl.update({rl[0]:rl[1],rl1[0]:rl1[1]})
                    # info=gen.next()
                        remotelink=rl[1]
                        locallink=rl1[1]
                        paxel(str(remotelink),locallink, blocks=4, proxies={})
                print " [x] download url has been processed :%r" % (l)
                break
            rule1.count=rule1.count+1
        return parurl


    def processChain(self,linkinfo):
        '''
        本函数一次启动preparse_*(parurl),parse(parurl),postparse(parurl)
         parurl为字典，可以在函数中修改，parurl只有一个实例，任何影响这个实例的操作都会对最终的parurl字典产生影响。

        '''
        link=''
        table=''
        if not isinstance(linkinfo,(str,unicode,dict)):
            return 0
        if isinstance(linkinfo,(str,unicode,)):
            linkinfo=json.loads(linkinfo)
        if not linkinfo.has_key('url'):
            return -2
        link=linkinfo['url']
        try:
            self.content=linkinfo['content']
            if self.content==-1:
                print '未能获取到HTML数据，将退出...'
                return
        except:
            return
        self.realurl=linkinfo['realurl']
        self.localpath=linkinfo['localpath']
        #启动预处理
        for attr in dir(self):
            if attr.startswith('preparse_'):#启动预处理
                if callable(getattr(self,attr)):
                    res=getattr(self,attr)(linkinfo)
                    if res==-1:
                        return
        #启动解析页面程序
        result={}
        for attr in dir(self):
            if attr.startswith('parse_'):
                subresult={}
                if callable(getattr(self,attr)):
                    subresult=getattr(self,attr)(linkinfo)
                if isinstance(subresult,dict):
                    linkinfo.update(subresult)
        #启动解析后处理
        for attr in dir(self):
            if attr.startswith('postparse_') and urlFilter.matchurl(**{'regx':SETTING.prregx,'url':link}):
                if callable(getattr(self,attr)):
                    subresult=getattr(self,attr)(linkinfo)
                if isinstance(subresult,dict):
                    linkinfo.update(subresult)
    def savemodel(self,link,table=None,*args,**kwargs):
        '''
        在这里执行数据库操作，kwargs包含要保存的字段和字段值。程序会自动建立字段和字段值。
        '''	
        if SETTING.DEBUG:
            print 'THE DBINFO IS %s' %kwargs
            print 'TABLE IS %s' %table

        if not table:
            table=SETTING.dbtable
        for attr in dir(self):
            savemethod=''
            if attr.startswith('save_'):
                savemethod=attr
            if isinstance(savemethod,str) and savemethod.startswith('save_'):
                if args and isinstance(args,tuple) and len(args)>0:
                    return getattr(self,savemethod)(table,*args,**{'result':kwargs})
                else:
                    return getattr(self,savemethod)(table,**{'result':kwargs})
        return -1

