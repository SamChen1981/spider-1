from mongoengine import *

# Create your models here. 
from spider.conf import settings
connect("ret",alias='default',**settings.MONGODB_CONF)
class data(DynamicDocument):
    meta = {'allow_inheritance': True}
    url=StringField()
   