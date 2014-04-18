spider
======

抓取程序用到的主文件
===================
概述:
=========
1用到的工具簡介：
	1.1Rabbitmq用於構建一個分佈式的集群。有關rabbitmq構建集群的內容請參看：
	https://www.rabbitmq.com/clustering.html
	2.1BerkeleyDB用於存儲中間結果
	3.1Requests:https://github.com/kennethreitz/requests, 這個工具用來模擬複雜的訪問，例如對GWT框架構建的服務的訪問。
	4.1python-Mysqldb用于python和mysql的数据库连接，支持多數據庫。在settings.py中新建一個DATABASES的項，
	例如：DATABASES={
		'default'：{
				'HOST':127.0.0.1,
				'PORT':3306.
				'USER':'root',
				'PSW':'127.0.0.1',
		}
	}
	5.1支持MongoDB或者BerkerleyDB作為最終數據結果的存儲，
	6.1一個抓取實例:https://github.com/moojun/huaqiang。

2.主要算法:
    該抓取系統採用廣度優先算法來爬取网站数据，并借鉴了Heritrix爬虫中的过滤链和解析链的架构设计，对Django
    中的MiddleWare架构熟悉的能比较好理解这个架构, 对于不同的网站只需要重写不同的过滤链和解析链即可。