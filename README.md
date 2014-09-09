spider
======

本框架的主要作用是用来方便的配置一个分布式的，高性能的爬虫系统，有一下几个功能

1.功能:

  1.内置一个pylucene作为默认的搜索引擎 
  
  2.添加web搜索功能,支持WSGI的协议(Gevent实现)
  
  3.支持可配置的消息队列，默认是Rabbitmq消息队列 
  
  4.可配置的数据库后端，可以自由选择数据库存储方式，内置orm系统,分别是SQLAlchemy和mongoengine，可以自行配置
  
  5.可配置网络接口后端，默认采用twisted后端


2.基本架构图:

3.使用
 3.1下载后配置环境变量, 例如export $PATH= $PATH:/PATH/TO/SPIDER_DIRECTORY/bin:/PATH/TO/SPIDER_DIRECTORY
 
 3.2 新建一个工程 spider-admin.py startproject test 和新建一个app : spider-admin.py startapp testapp 
 
 3.3 建立一个model,在app目录下的models.py中按照 http://www.ibm.com/developerworks/cn/aix/library/au-sqlalchemy/所示的例子建立model



