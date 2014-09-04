from mongoengine import *

# Create your models here. 
from spider.conf import settings

connect("ret",alias='default',**settings.MONGODB_CONF)
class webcontent(DynamicDocument):
    meta = {'allow_inheritance': True}
    url=StringField()
    sourcefile=FileField()
    create_date=DateTimeField()
    name=StringField()
    realurl=StringField()
    docid=StringField()
   