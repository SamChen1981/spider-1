#coding=utf-8
import MySQLdb
import datetime

'''
$Id: dbsource.py 2670 2010-06-13 08:34:44Z lidong $

'''

#DB_HOST = 'localhost'
#DB_HOST = '192.168.0.8'
#DB_HOST = '192.168.100.50'
#DB_HOST = 'kongming'
#luxun 192.168.1.177
#DB_HOST = 'luxun'
#DB_HOST = 'liubei'
try:
    from dbsource_settings import DB_HOST_SETTING
    DB_HOST = DB_HOST_SETTING
    print 'in dbsource.py line 20 DB_HOST:',DB_HOST
except:
    raise ValueError,'find not dbsource_settings.py, please check ...'
DB_USER = 'lidongdev'
DB_PASS = 'asdasd'

'''
# 数据源
src_con = MySQLdb.connect(host=DB_HOST, port=3306,
                      user=DB_USER, passwd=DB_PASS, db=DB_SOURCE ,use_unicode=1, charset='utf8')
src_cur = src_con.cursor( )

'''

LOG_FILE = '/db/import2icgoo/log/dberrlog'
debug_log = [True,False][1]
if debug_log:
    print 'in dbsource.py line 31 debug_log is True and will print information'

def log(*args,**kwargs):
    """
    这个log 函数有两个可选参数，
    filename=日志文件名，如果不提供这个参数，
    则需要有一个全局的 LOG_FILE 变量
    timestamp=1 ,如果有这个参数，日志会在每行末尾增加时间戳
    默认是没有时间戳的。
    """

    import string
    filename = kwargs.pop('filename',None) or LOG_FILE    
    try:#防止权限读写异常  edit by daimingming on 2013年 08月 30日 星期五 11:58:18 CST
        f = open(filename,'aw')
        msg = ""
        for a in args:
            if isinstance(a,(list,tuple,dict)):
                msg += repr(a)
            else:
                msg+= a
        if kwargs.pop('timestamp',None):
            msg += " %s " %datetime.datetime.now()
        str = "%s \n" %msg
        try:
            f.write("%s \n" %msg)
        except:
            f.write('log meet an error ,may be an unicode encode error \n') 
        f.close()
    except Exception,e:
        if debug_log: print 'in dbsource.py line 61 exception:',str(e)
        pass


class DbConn(object):
    def __init__(self,db_name, db_read='', db_write_list=[], host=DB_HOST,port=3306,user=DB_USER,passwd=DB_PASS):
        con = MySQLdb.connect(host=host, port=3306,
                      user=user, passwd=passwd, db=db_name ,use_unicode=1, charset='utf8')
        if not db_read:
            self.cur_read = con.cursor()
        else:
            con_read = MySQLdb.connect(host=host, port=3306,
                      user=user, passwd=passwd, db=db_read ,use_unicode=1, charset='utf8')
            self.cur_read = con_read.cursor()

        self.cur_write_list = []
        if not db_write_list:
            self.cur_write_list.append(con.cursor())
        else:
            for db_write in db_write_list:
                con_write = MySQLdb.connect(host=host, port=3306,
                      user=user, passwd=passwd, db=db_write ,use_unicode=1, charset='utf8')
                self.cur_write_list.append(con_write.cursor())

    def fetch_one(self,sql,params=[]):
        '''只取回一条记录'''
        if not isinstance(params, (list,tuple)):
            params = [params]
        r = self.cur_read.execute(sql,params)
        if r:
            return self.cur_read.fetchone()
        return None

    def fetch_all(self,sql,params=[]):
        '''取回所有记录'''
        if not isinstance(params, (list,tuple)):
            params = [params]
        r = self.cur_read.execute(sql,params)
        if r:
            return self.cur_read.fetchall()
        return None

    def update_kwargs(self, tablename ,id=None, **kwargs):
        """ Update table ,set key = value where id = id 
            table 必须有 id 字段，更新操作的时候也必须提供id 这个参数 
            id 参数可以出现在 kwargs 中
        """
        id = id or kwargs.pop('id',None)
        if not id:
            log('no id argument can not update to %s' %table)
            return 0

        set_str = ''
        para = []
        for key,value in kwargs.iteritems():
            set_str += ",%s = %s" %(key,'%s')
            if isinstance(value, unicode):
                try:
                    utfVal = value.encode("utf-8")
                except Exception, e:
                    utfVal = ''
                    print "table %s have a unicode error %s" %(tablename,e)
            elif isinstance(value,(int,float)):
                utfVal = value
            elif value is None:
                utfVal = ""
            else:
                utfVal = kwargs[key]
            para += [utfVal]
            
        set_str = set_str[1:]
        sqlstr = """update %s set %s where id=%s""" %(tablename, set_str, id)
        try:
            #print "%s  -- %s" %(sqlstr, para)
            for cur in self.cur_write_list:
                cur.execute(sqlstr,para)
            #self.con.commit()
            return id
        except Exception, e:
            log(sqlstr, "%s" %e)
            print "error in dbsource.py update: %s" %e
            return 0


    def insert_kwargs(self, table, **kwargs):
        """ Insert Resoult Records into database
            把一个字典数据当成表中的每个字段插入到表 tablename  
        """
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
            try:    
                sqlstr = """insert into %s (%s) values (%s)""" %(table, sqlitems[1:], sqlvalues[1:])
                for cur in self.cur_write_list:
                    cur.execute(sqlstr,para)
                #self.con.commit()
            except Exception,ex:
                log(sqlstr, str(ex))
            self.cur_write_list[0].execute('select LAST_INSERT_ID()')
            row = self.cur_write_list[0].fetchone()
            if row:
                return row[0]
            else:
                return None
        except Exception, e:
            log("module dbsource.py insert_kwargs() error: %s %s %s" %(Exception,e,kwargs))
            return None
  
    def get_id (self,sql,params=[]):
        '''返回一个 id 数字或者 None'''
        ck = self.cur_read.execute(sql, params )
        if ck:#存在
            ckr = self.cur_read.fetchone()
            return ckr[0]
        return None 

    def execute(self,sql,params = []):
        if not isinstance(params, (list,tuple)):
            params = [params]
        return self.cur_read.execute(sql,params)

    def insert(self,sql,params):
        '''返回刚刚插入的id '''
        self.execute(sql,params)
        newid = self.fetch_one('select LAST_INSERT_ID()')
        return newid[0]

    def delete(self, sql, params=[]):
        if not isinstance(params, (list,tuple)):
            params = [params]
        for cur in self.cur_write_list:
            cur.execute(sql,params)
        return 

if __name__ == '__main__':
    pass
