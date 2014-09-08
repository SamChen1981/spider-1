#encoding=utf8
'''
Created on 2014年9月5日

@author: mu
'''
from datetime import datetime
from sqlalchemy import Table, MetaData, Column,ForeignKey, Integer, String, Unicode, DateTime 
from sqlalchemy.ext.declarative import declarative_base
from spider.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from spider.db.model.loading import register_models
import sys
Base = declarative_base()

print dir(Base)
class basemanager(object):
    def __init__(self,engine,Base):
        self.Base=Base
        self.engine=engine
        self.Session = scoped_session(sessionmaker(bind=self.engine))
    @property
    def get_session(self):
        self.Base.metadata.create_all(self.engine)
        
        session=self.Session()
        return session
    
class modelbase(type):
    def __new__(cls,name,bases,attrs):
        
        if not hasattr(attrs,"__tablename__"):
            attrs["__tablename__"]=name
        def __repr__(self):
            return "<User(name='%s', fullname='%s', password='%s')>" % (name,name,name)
        if not hasattr(attrs,"__repr__"):
            attrs["__repr__"]=__repr__
    
        for dbconf in settings.DATABASES:
          
            if dbconf['alisa'] =='test1':
                
                break
        conf_dict={}
        conf_dict.update({'host':dbconf['host'],'user':dbconf['user'],\
                        'passwd':dbconf['passwd'],'db':dbconf['db'],
                        'port':3306})
        
        engine = create_engine("mysql://"+dbconf['user']+":"+str(dbconf['passwd'])+"@"+dbconf['host']+"/"+dbconf['db'],
                                            encoding='utf8', echo=True)        
        #engine = create_engine('mysql',conf_dict, echo=True)
        
        if not hasattr(attrs,"objects"):
            
            attrs["objects"]=basemanager(engine,Base)
        print name
        print bases
        print super(modelbase,cls)
        del attrs['__metaclass__']
        new_class=type.__new__(cls,name,bases,attrs)
        
        model_module = sys.modules[new_class.__module__]
        
        register_models(model_module.__package__, new_class)

    
    

class model(Base):
    __metaclass__=modelbase
    
    def save(self):
        session=self.__class__.objects.get_session()
        session.add(self)
    '''
    def autosave(self,urldict):
        for k,v in urldict.items():
            getattr(self.__class__,k)
    '''