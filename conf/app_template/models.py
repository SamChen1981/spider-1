import os



from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

from spider.db.model.decorators import model_register

from sqlalchemy.ext.declarative import declarative_base
path = "/tmp"

#SQLAlchemy
Base = declarative_base()
@model_register
class BaseModel(Base):
    __tablename__ = 'filesystem'
    
    path = Column(String, primary_key=True)
    name = Column(String)

    def __init__(self, path,name):
        self.path = path
        self.name = name

    def __repr__(self):
        return "<Metadata('%s','%s')>" % (self.path,self.name)
