#coding=utf8

import bsddb as bsddb 

class CrawlerDB:
	
    #BDB操作类的基类
    def __init__(self, db_file):
        self.database_file = db_file
        self.database = bsddb.db.DB(None,0)
    #根据文件名打开一个bdb句柄,具体参数的含义参考BerkeleyDB 文档
    def open_db(self, dbtype, readonly):
        if readonly == True:
            self.BDB.open(self.database_file,dbname=None,mode=0,txn=None)
            return
        if dbtype == 'DB_HASH':
            if cache == True:
                self.BDB.set_cachesize(0,536870912)
            self.BDB.open(self.database_file,dbname=None,dbtype=bsddb.db.DB_HASH,flags=bsddb.db.DB_CREATE,mode=0,txn=None)
        elif dbtype == 'DB_BTREE':
            if cache == True:
                self.BDB.set_cachesize(0,536870912)
            self.BDB.open(self.database_file,dbname=None,dbtype=bsddb.db.DB_BTREE,flags=bsddb.db.DB_CREATE,mode=0,txn=None)
        elif dbtype == 'DB_QUEUE':
            self.BDB.set_re_len(1024)
            self.BDB.open(self.database_file,dbname=None,dbtype=bsddb.db.DB_QUEUE,flags=bsddb.db.DB_CREATE,mode=0,txn=None)
        elif dbtype == 'DB_RECNO':
            self.BDB.open(self.database_file,dbname=None,dbtype=bsddb.db.DB_RECNO,flags=bsddb.db.DB_CREATE,mode=0,txn=None)
        else:
            self.BDB.open(self.database_file,dbname=None,mode=0,txn=None)

    #插入一个key-value 
    def insert(self,key,val=""):
        try:
            self.database.put(key,val)
        except:
            raise
    #根据一个Key找到value
    def select(self,key):
        val = self.database.get(key)
        return val
    #根据key删除value
    def delete(self,key):
        try:
            self.database.delete(key)
        except:
            return False
        return True
    #判断该Key是否已经存在
    def exist(self,key):
        sval = self.database.get(key)
        if sval != None:
            return True
        else:
            return False
    #关闭这个数据库
    def close(self):
        self.database.close()
    #取得游标
    def get_cursor(self):
        return self.database.cursor()
    #同步，将缓存写入磁盘
    def sync(self):
        self.database.sync()

class VistedDB( CrawlerDB ):
    
    def __init__(self,dbfile):
        CrawlerDB.__init__(self, dbfile)
        
        self.database.set_re_len(512)
    def add_urls():
        pass
class QueueDB( CrawlerDB ):
    #队列db,继承基类
    def __init__(self, dbfile):
        CrawlerDB.__init__(self, dbfile)
        self.database.set_re_len( 512 )
        self.database.open( self.database_file, 
                            dbname = None, 
                            dbtype = bsddb.db.DB_QUEUE,
                            flags  = bsddb.db.DB_CREATE,
                            mode   = 0,
                            txn    = None, )
    
    def pop_url(self):
        url = self.database.consume()
        if url == None:
            return url
        url = url[1].strip()
        return url

    def push_urls(self, url_list):
        for url in url_list:
            self.database.append( url )

    #hashDB ，有key-value pair
class WebpageDB( CrawlerDB ):
    
    def __init__(self, dbfile):
        CrawlerDB.__init__(self, dbfile)
        self.database.open(  self.database_file, 
                        dbname=None,
                        dbtype=bsddb.db.DB_HASH,
                        flags=bsddb.db.DB_CREATE,
                        mode=0,
                        txn=None, )

    def html2db(self,url, html):
        self.insert(url, html)

    #HASH DB，只有key ，默认没有value
class DuplCheckDB( CrawlerDB ):
    def __init__(self, dbfile):
        CrawlerDB.__init__(self, dbfile)
        self.database.open(  self.database_file, 
                        dbname=None,
                        dbtype=bsddb.db.DB_HASH,
                        flags=bsddb.db.DB_CREATE,
                        mode=0,
                        txn=None, )

    def filter_dupl_urls(self, url_list):
        unique_urls = []
        for url in url_list:
            if self.database.get(url)==None:
                unique_urls.append(url)
        return unique_urls 
    
    def add_urls(self, url_list):
        for url in url_list:
            self.insert(url, "")
        return True

#import MySQLdb
class MySqlDB:
    
    def __init__(self,phost,puser,ppwd,pdb):
        self.db = MySQLdb.connect(host = phost,user = puser, passwd = ppwd, db = pdb)
        self.cr = self.db.cursor()
    
    def execute(self,SQL):
        self.cr.execute(SQL)
    
    def isDataExist(self,SQL):
        self.cr.execute(SQL)
        numrows = int(self.cr.rowcount)
        if numrows >0:
            return True
        else:
            return False
    def select(self,SQL):
        self.cr.execute(SQL)
        numrow = int(self.cr.rowcount)
        return self.cr.fetchall()


if __name__ == "__main__":
    pass