'''
Created on 2014年9月5日

@author: mu
'''
from datetime import datetime
from sqlalchemy import Table, MetaData, Column,ForeignKey, Integer, String, Unicode, DateTime 

class modelbase(type):
    pass
def basemanager(object):
    def create_sql_session():
        pass
class model(object):
    __metaclass__=modelbase
    