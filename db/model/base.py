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
class modelbase(type):
    def __new__(cls,name,bases,attrs):
        Base = declarative_base()
        if not hasattr(attrs,"__tablename__"):
            attrs["__tablename__"]=name
        def __repr__(self):
            return "<User(name='%s', fullname='%s', password='%s')>" % (name,name,name)
        if not hasattr(attrs,"__repr__"):
            attrs["__repr__"]=__repr__
        if not Base in bases:
            bases.append(Base)
        name=settings.DATABASE['name']
        host=settings.DATABASE['host']
        username=settings.DATABASE['username']
        port=settings.DATABASE['port']
        psw=settings.DATABASE['password']
        database=settings.DATABASE['database']
        conf_str=name+"://"+host+":"+username+"@"+host+":"+port+"/"+database
        engine = create_engine(conf_str, echo=True)
        
        if not hasattr(attrs,"objects"):
            attrs["objects"]=basemanager(engine,Base)
        return Base.__class__.__new__(name.bases,attrs)
        
def basemanager(object):
    def __init__(self,engine,Base):
        self.Base=Base
        self.engine=engine
        self.Session = scoped_session(sessionmaker(bind=self.engine))
    @property
    def get_session(self):
        self.Base.metadata.create_all(self.engine)
        
        session=self.Session()
        return session
    
    
    

class model(object):
    __metaclass__=modelbase
    def save(self):
        session=self.__class__.objects.get_session()
        session.add(self)