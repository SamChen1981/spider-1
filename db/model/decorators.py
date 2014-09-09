from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from spider.db.model.loading import register_models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from spider.conf import settings




      
def transactional(fn):
    """add transactional semantics to a method."""
    
    def transact(self, *args):
  
        session = Session()
        try:
            fn(self, session, *args)
            session.commit()
        except:
            session.rollback()
            raise
    transact.__name__ = fn.__name__
    return transact

def model_register(cls):
    for dbconf in settings.DATABASES:
        if dbconf['alisa']==cls.__name__:
            break
    
    engine = create_engine("mysql://"+dbconf['user']+":"+str(dbconf['passwd'])+"@"+dbconf['host']+"/"+dbconf['db'],\
    encoding='utf8', echo=True) 
    register_models(cls.__name__,*(cls,))
    cls.engine=engine
    cls.Session = scoped_session(sessionmaker(bind=engine)) 
    print "ddddddddddddddddddddd %s" %cls
    return cls