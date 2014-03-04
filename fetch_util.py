#coding=utf8
import threading
import urllib
import Queue
import re
import MySQLdb as mysql
import traceback
import urllib2
import time
queue=Queue.Queue()
import sys
import string
import os
import signal
from taskqueue import task_queue
from datetime import *
import json
import time
reload(sys)
sys.setdefaultencoding('utf8')
import string
from  multiprocessing import Lock
urlopenlock = Lock()
import random
import thread
from multiprocessing import Process
from multiprocessing import Lock
import commands
from settings import SETTING
import cookielib
import time
import subprocess
import opener
class Gethtml_digikey():
    '''
        在get_html中根据kwargs的func键值调用opener函数，该函数定义在每个抓取任务目录的opener.py模块中 
    '''
    def __init__(self,url,*args,**kwargs):
        self.url = url
        self.i_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"

                          }
        #self.get_iplist()
        #self.creat_temip()
  	self.recur_count=0
    def get_html(self,*args,**kwargs):
        '''
         根据获取的临时ip构造最终url并返回所抓取的html
         如果发生异常则更换ip继续自动请求直到获取成功
         prams为空使用GET请求
        '''
        params={}
        #print self.url
	final_url=self.url
        #final_url = self.url.replace('www.digikey.cn',self.tem_ip)
	#final_url=final_url.replace(' ','')
        print 'in get_html',final_url

        try:
            print 'begin'
            #print "use ip:",self.tem_ip

            #page = urllib2.urlopen(req,timeout=15)#15秒超时
            if kwargs.has_key('func'):
		self.hc,self.info_url=opener.__dict__[kwargs['func']](**kwargs)
                #self.hc,self.info_url=sys.modules['__main__'].__dict__[kwargs['func']](**kwargs)
	    #self.hc = arrow_opener(final_url)
            #self.info_url = page.geturl()
	    #print 'THE REAL URL IS  %s' %self.info_url
            #print len(hc)
            if SETTING.DEBUG:
                print 'end'
            return (self.hc,self.info_url)
        except urllib2.HTTPError, e:
            print "Error Code:", e.code
            print "Error context:",e
        #    self.creat_temip()
	    if self.recur_count>5:
		print ' ****超过最大递归层数****'
	    	sys.exit(1)
	    self.recur_count=self.recur_count+1
            return self.get_html()
        except urllib2.URLError, e:
            print "Error Reason:", e.reason
	    if self.recur_count>5:
		print '****超过最大递归层数****'
	        sys.exit(1)
	    self.recur_count=self.recur_count+1
        #    self.creat_temip()
            return self.get_html()
        except:
            error=traceback.format_exc()
            print error

            print "TimeOut error!"
	    if self.recur_count>5:
	        print ' ****超过最大递归层数****'
	        sys.exit(1)
	    self.recur_count=self.recur_count+1
            #self.creat_temip()
            return self.get_html()


content_glob=''
def saveHTML(*args,**kwargs):
    '''
      保存html.会根据settings.py提供的正则保存
    '''
    realurl=kwargs['realurl']
    url=kwargs['url']
    save_dir=SETTING.save_dir

    content=kwargs['content']
    LOCALPATH_QUEUE=SETTING.LOCALPATH_QUEUE
    for r in SETTING.page_save_reglist:
        if not Rule.matchurl(url=url,regx=r):
    	    continue
	if kwargs['partno']:
	    protype=kwargs['partno']
	else:
	    protype=''
#去除特殊字元
        pattern=re.compile(r'/')
        protype=re.sub(pattern,'',protype)
 	pattern=re.compile(r'\n')
        protype=re.sub(pattern,'',protype)
	try:
            subdirectory=protype[0]
	except:
	    subdirectory=''
	top_sub=string.split(realurl,'/')[2]
        subdirectory=string.join((top_sub,subdirectory),'/')
        directory=os.path.join(save_dir,subdirectory)
        if os.path.isdir(directory):
            pass
        else:
            os.makedirs(directory)
        filepath=os.path.join(directory,protype+'_'+datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d:%H:%M:%S')+'.html')
  	print 'THE SAVE LOCATION IS %s' %filepath
    	try:

            g=open(filepath,'a+')
            print >> g,'------------------------------------------------------'
            print >> g, content
            print >> g,'------------------------------------------------------'
            g.close()
            print 'CURRENT PAGE SAVE SUCCESSFULLY'
	    #task_queue.sendtask2BDB([filepath],LOCALPATH_QUEUE,exchange_name='',mqtype='RABBIT',**{'count':10})

            return filepath
        except:
            error=traceback.format_exc()
            print error

            return -1
    return ''
class Fetch_WebContent():
    #下载函数
    def getAllContent(self,*args,**kwargs):
        #header={'User-Agent':'Mozilla/5.0'}
        #proxy_handler=urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
        #opener=urllib2.build_opener(proxy_handler)
        if not os.path.isdir(kwargs['url']) and SETTING.local_flag==1:
	    try:
       	        iptxt = file(kwargs['url'],'r')
                content = iptxt.read()
	    except:
	 	return -1
	    iptxt.close()
	    return (content,kwargs['url'])
        elif SETTING.local_flag==0:
            if kwargs.has_key('url'):
    	        geth=Gethtml_digikey(kwargs['url'],**{'digikey':'digikey_ip.txt'})
      	        content=geth.get_html(**kwargs)

                content_glob=content[0]
                realurl=content[1]
                try:
		    localpath=saveHTML(**{'url':kwargs['url'],'realurl':realurl,'content':content_glob,'partno':'hqew'})
                except:
		    error=traceback.format_exc()
                    print error


                    localpath=''
    	        return (content_glob,realurl,localpath)
        else:
            return -1

class getHTML():
    @classmethod
    def getURLFromDisk(cls,basedir,db_directory,table=None,*args,**kwargs):

        task_queue.db_directory=db_directory
        tq=task_queue()
        task_queue.savevisitedURL([basedir])

        task_queue.sendtask2BDB([basedir],"NORMAL")
        while(1):
            url=''
            item=''
            try:
                tmp=task_queue.popmsgfromBDB("NORMAL")
                if not tmp:
                    break
                item=json.loads(tmp)

                if not item.has_key('url'):
                    continue
                url=item['url']
                print url

            except:
                error=traceback.format_exc()
                print error

                break
            if os.path.isdir(url):
                uniques=[]
                for subitem in db.from_iterable(os.listdir(url)):
                    if subitem.startswith('.') or os.path.splitext(subitem)[-1]=='.db':
                        continue
                    subitem=os.path.join(url,subitem)
                    checkresult=task_queue.checkvisited(str(subitem))
                    if not checkresult:
                        result={}
                        result.update({'url':subitem})
                        print '%s ADDED TO THE QUEUE' % subitem
                        task_queue.savevisitedURL([str(subitem)])
                        uniques.append(result)
                task_queue.sendtask2BDB(uniques,'NORMAL')



            elif os.path.isfile(url):
                if not os.path.splitext(url)[1]=='.html' or os.path.basename(url).startswith('.') or os.path.splitext(url)[-1]=='.db':
                    continue
                if table:
                    item.update({'table':table})
                yield item
        yield None

#数据库接口/操作，包含:
#1.字段生成函数;
#2.数据库操作函数

class db(object):
    con=None
    def __init__(self,*args,**kwargs):
        pass
    #生成where语句
    @classmethod
    def Dict2Str(cls,dictin,joiner=','):
        if not dictin:
            return
        tmplist=[]
        for k,v in dictin.items():
            # if v is list, so, generate
            # "k in (v)"
            if isinstance(v,(list,tuple)):
                tmp = str(k)+' in ('+ ','.join(map(lambda x:'\"'+str(x)+'\"',v)) +') '
            else:
                tmp=str(k)+'='+'\"'+str(v)+'\"'
            tmplist.append(' '+tmp+' ')
        return joiner.join(tmplist)
    @classmethod
    def from_iterable(cls,iterables):
    # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
        for it in iterables:
            yield it

    #生成插入语句
    @classmethod
    def insert_kwargs(cls,table,**kwargs):
        try:
            sqlitems = ""
            sqlvalues= ""
            para = []
            for key,value in kwargs.iteritems():
                sqlitems += ",%s" %key
                sqlvalues += ",%s"
                if isinstance(value,unicode):
                    try:
                        utfVal = value.encode("utf8")
                    except Exception, e:
                        utfVal = ""
                        print "table %s have a unicode error %s" %(table,e)
                elif isinstance(value,(int,float)):
                    utfVal = value
                elif not value:
                    utfVal = ""
                else:
                    utfVal = value
                para += [utfVal]
            sqlstr = """insert into %s (%s) values (%s)""" %(table, sqlitems[1:], sqlvalues[1:])
            return [sqlstr,para]
        #self.con.commit()
        except Exception, e:
            return None
    @classmethod
    def gen_insert(cls,table,insdict):
        if not isinstance(insdict,dict):
            return -1
        sql = 'insert into %s '% table
        ksql = []
        vsql = []
        for k,v in insdict.items():
            ksql.append(str(k))
            vsql.append('\"'+str(v)+'\"')
        sql+='('+','.join(ksql)+')'
        sql+=' values ('+','.join(vsql)+')'
        return sql
    #生成更新语句
    @classmethod
    def gen_update(cls,table,some_dicts,file_id_dict):
        #条件字典中值为tuple的在sql语句中为key1 in (value1,value2,...) , 条件字典中值不为tuple的为 key2=value
        if not isinstance(some_dicts,dict) or not isinstance(file_id_dict,dict):
            return -1
        sql=''
        sql += ' update %s ' % table
        sql += ' set %s' % db.Dict2Str(some_dicts)
        sql += ' where %s' % db.Dict2Str(file_id_dict,'and')
        return sql
    #生成重复数据更新字段语句
    @classmethod
    def gen_on_duplicate(cls,*args,**kwargs):
        if not kwargs.has_key('joiner') or not kwargs['joiner']:
            return -1

        templist=[]
        if not isinstance(args,tuple):
            return -1
        sql = 'ON DUPLICATE KEY UPDATE '
        for k in args:
            templist.append(k+'=VALUES('+k+')')
        sql=sql+kwargs['joiner'].join(templist)
        return sql
    #检查是否有重复
    def checkcatlinkexist(self,*args,**kwargs):
        con = mysql.connect(host='192.168.0.6', user='chenkun', passwd='ck1234', db='chenkun_alibaba',use_unicode=1,charset='utf8')
        if kwargs['con'] is None:
            return None
        try:
            if con is not None:
                with con:
                    cur=con.cursor()
                    cur.execute("SELECT "+kwargs['col']+" FROM "+kwargs['table']+" WHERE EXISTS (SELECT *FROM "+kwargs['table']+"  WHERE "+kwargs['checkcol']+"='%s') LIMIT 1")
                    #cur.execute("SELECT 1 FROM linkTable WHERE catlink = "+catlink+" LIMIT 1",(catlink,catname,str(time.strftime("%Y%m%d-%H%M%S"))))
                    r = cur.fetchone()
                    if not r is None:
                        print 'Record Exists'
                        return True
                    else:
                        return False
                    #con.commit()
        except:
            traceback.print_exc()

            return None
    #检查更新
    @classmethod
    def gen_select(cls,table,keys,*args,**kwargs):
        col=''
        if isinstance(keys, (tuple,list)):

            col=','.join(map(lambda x:str(x),keys))

        sql = 'select %s ' % col
        sql += ' from %s ' % table
        if kwargs.has_key('conditions') and isinstance(kwargs['conditions'],dict):

            sql += ' where %s '%cls.Dict2Str(kwargs['conditions'],'and')
            #print sql
        return sql

    #初始化一个新的数据链接
    @classmethod
    def init_conn(cls,host,user,passwd,DB=None):
        HOST = host
        DB = 'chenkun_alibaba' if DB is None else DB
        USER = user
        PASSWD = passwd
        conn = mysql.connect(host=HOST,port=3306,user=USER,passwd=PASSWD,\
        db=DB,use_unicode=1,charset='utf8')
        cls.con=conn
        return conn
    @classmethod
    def execute_sql_without_ret(cls,sql,flag=1,**kwargs):
        db.con = db.init_conn(host=kwargs['host'], user=kwargs['user'], passwd=kwargs['passwd'], DB=kwargs['db'])
        try:

            if db.con is not None:
                with db.con:
                    if sql:

                        cur=db.con.cursor(mysql.cursors.DictCursor)
                        cur.execute(sql[0],sql[1])
                        #db.con.commit()

                        if flag==1:
                            print 'ALTER Operation Compelete Successful ******%s' %sql

                        return 1
                return -1
            else:
                return -1
        except mysql.Error,e:
            print 'Database  Fail'
            error=traceback.format_exc()
            print error
            sys.exit(1)
            return -1


    #执行插入或更新sql语句
    @classmethod
    def execute_sql(cls,sql,flag=1,**kwargs):
        db.con = db.init_conn(host=kwargs['host'], user=kwargs['user'], passwd=kwargs['passwd'], DB=kwargs['db'])
        try:

            if db.con is not None:
                with db.con:
                    if sql:

                        cur=db.con.cursor(mysql.cursors.DictCursor)
                        cur.execute(sql[0],sql[1])
                        #db.con.commit()

                        r = cur.execute('select LAST_INSERT_ID()')
                        if r:
                            newid=cur.fetchone()['LAST_INSERT_ID()']
                        else:
                            newid=-1
                        if flag==1:
                            print 'INSERT Operation Compelete Successful ******%s' %sql
                        elif flag==2:
                            print 'UPDATE Operation Compelete Successful ******%s' %sql


                        return newid
                return -1
            else:
                return -1
        except mysql.Error,e:
            print 'Database  Fail'
            error=traceback.format_exc()
            print error
            sys.exit(1)
            return -1

    #生成检查语句
    @classmethod
    def gen_checkexist(cls,*args,**kwargs):
        subsql1=cls.gen_select(kwargs['table'],kwargs['key'])
        subsql2=cls.gen_select(kwargs['table'],kwargs['key'],**{'conditions':kwargs['condition']})
        sql= "%s WHERE EXISTS (%s) LIMIT 1" % (subsql1,subsql2)
        return sql
    #检查是否重复
    @classmethod
    def checkexist(cls,sql,*args,**kwargs):
        db.con = db.init_conn(host=kwargs['host'], user=kwargs['user'], passwd=kwargs['passwd'], DB=kwargs['db'])
        if db.con is None:
            return None
        try:
            if db.con is not None:
                with db.con:
                    cur=db.con.cursor()
                    cur.execute(sql)
                    #cur.execute("SELECT 1 FROM linkTable WHERE catlink = "+catlink+" LIMIT 1",(catlink,catname,str(time.strftime("%Y%m%d-%H%M%S"))))
                    r = cur.fetchone()
                    if not r is None:
                        print 'Record Exists'
                        return True
                    else:
                        return False
                    #con.commit()
        except:
            traceback.print_exc()

            return None
    #执行查询语句
    @classmethod
    def execute_select_sql(cls,sql,flag,**kwargs):
        db.con = db.init_conn(host=kwargs['host'], user=kwargs['user'], passwd=kwargs['passwd'], DB=kwargs['db'])
        try:
            if db.con is not None:
                with db.con:
                    if sql:
                        cur=db.con.cursor(mysql.cursors.DictCursor)
                        cur.execute(sql)
                        #db.con.commit()
                        numrows = int(cur.rowcount)
                        for i in range(numrows):
                            row = cur.fetchone()
                            if row:
                                if kwargs.has_key('field') and kwargs['field'] and isinstance(kwargs['field'],(tuple,list)):
                                    yield (row[field] for field in kwargs['field'])


                if flag==0:
                    print "Error Saved"
                else:
                    print 'Operation Compelete Successful'
        except mysql.Error,e:
            print 'Database  Fail'
            error=traceback.format_exc()
            print error
            sys.exit(1)
class extractor(object):
    '''两个函数两个功能'''
    #提取key-value类型的数据
    #提取单一一个value
    #列表返回
    @classmethod
    def simpleExtractorAsList(cls,regx,content,*args,**kwargs):
	try:
	    uniques=[]

	    regx=re.compile(regx)
            templist=re.findall(regx,content)
	    uniques.extend(templist)
	    return uniques
	except:
	    print " [x] Error occor"
            traceback.print_exc()

	return uniques

    @classmethod
    def getItemAsValue(cls,content,regx,index,*args,**kwargs):
        if not content or not regx:
            return -1
        pattern=re.compile(regx)
        match=re.search(pattern,content)
        #取得表格HTML内容
        if isinstance(index,tuple):
            values=[]

            for ind in index:
                try:

                    values.append(match.group(ind))
                except:
		    error=traceback.format_exc()
	            print error

            return values

        if isinstance(index,(str,int)):
            result=''
            try:

                result=match.group(index)
            except:
                pass
            return result
    #提取单一一个值作为一个列表返回
    @classmethod
    def getItemsAsList(cls,content,regx,*args,**kwargs):
        if not content or not regx:
            return []
        templist=[]
        pattern=re.compile(regx)
        templist.extend(re.findall(pattern,content))
        return templist

#过滤类，用户需要根据具体情况重写该类，该类也提供一个函数用于检查一个url是否和给定的正则表达式相同
class urlFilter(object):
    def __init__(self,regx):
        self.regx=regx
    def filterurl(self,*args):
        pattern=re.compile(self.regx)
        url=string.strip(url)
        match=re.search(pattern,url)
        if match:
            return True
        return False

    @classmethod
    def matchurl(cls,*args,**kwargs):
        if not kwargs['url']:
            return False
        if kwargs['regx']=='' or not kwargs['regx']:
            return False
        if isinstance(kwargs['regx'],(tuple,list)):
            for r in kwargs['regx']:

                pattern=re.compile(r)
                url=string.strip(kwargs['url'])
                match=re.search(pattern,kwargs['url'])
                if match:
                    return True
        if isinstance(kwargs['regx'],str):
            pattern=re.compile(kwargs['regx'])
            url=string.strip(kwargs['url'])
            match=re.search(pattern,kwargs['url'])
            if match:
                return True

        return False
#规则类，用户需要在子类中自定义规则，目前提供了一个函数，检查一个url是否和给定的正则表达式相同
class Rule(object):
    @classmethod
    def matchurl(cls,*args,**kwargs):
        if not kwargs['url']:
            return False
        if kwargs['regx']=='' or not kwargs['regx']:
            return False
        pattern=re.compile(kwargs['regx'])
        url=string.strip(kwargs['url'])
        match=re.search(pattern,kwargs['url'])
        if match:
            return True
        return False

#线程实体类，用户可以根据需要扩展这个类
class xvideoThread(threading.Thread):
    worker_count=0
    def __init__(self):
        threading.Thread.__init__(self)
        self.id=xvideoThread.worker_count
        xvideoThread.worker_count+=1
        self.start()
    def run(self):
        try:
            for attr in dir(self):
                if attr.startswith('target_'):
                    getattr(self,attr)()

        except:

                error=traceback.format_exc()
                print error
                print 'error happen when get the job from Queue'
#数据库池，感觉在本程序中用处不大 ，但其实是很有用处的，特别在抓取速率动态控制，线程状态控制方面很有用处，
#这个连接池模块有待改进
class ThreadPool:
    def __init__(self,number_worker,timeout,targetobject):

        self.workerqueue=Queue.Queue()
        self.timeout=timeout
        self.number_worker=number_worker
        self._recruitThreads(number_worker)
        self.targetobject=targetobject
    def _recruitThreads(self,number_worker):
        for attr in dir(self):
                if attr.startswith('create_'):
                    getattr(self,attr)()

        i=0
        for i in range(number_worker):
            xvideo=self.targetobject()
            self.workerqueue.put(xvideo)
    def wait_for_complete(self):
        #while len(self.workers):
        #    worker=self.workers.pop()
        #    if worker.isAlive() and not self.workqueue.empty():
        #        self.workers.append(worker)

        while self.workerqueue.qsize() > 0:

            try:
                taskthread=self.workerqueue.get()

                if not taskthread.isAlive():
                    print 'Thread-%s done its job' % taskthread.id

                else:
                    self.workerqueue.put(taskthread)
            except:
                print 'Well It\'s seem that the thread Queue is empty'

            time.sleep(1)
        print 'All job has done!!!!'


