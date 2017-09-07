# encoding=utf8
import os

DATABASES = []
SEEDS = ['https://www.literotica.com/c/lesbian-sex-stories']
RABBITMQ_QUEUE = "test"
SAVE_PAGE_REGLIST = []
# 存储内容后端,用来筛选需要存储的字段
SAVE_PAGE_BACKENDS = ["spider.save_page.backends.invertlist.SavePageBackend"]
# 暂存区后端
STAGING_BACKENDS = ["spider.staging.backends.MongoStaging.StagingBackend"]
# 页面解析后端
PARSER_BACKENDS = [
    "spider.ContentResolver.backends.InverseList.backends.Inverted_List"]
# 消息队列系统后端
RABBITMQ_BACKENDS = ["spider.msgsystem.backends.rabbitmq.TaskQueue"]
# 访问页面的网络接口后端，默认是twisted提供的客户端
INTERNET_BACKENDS = ["spider.internet.backends.twisted.HttpClient"]

# 处理中间件
MIDDLEWARE_CLASSES = ["spider.middleware.opener.OpenerMiddleware",
                      "spider.middleware.parser.ParserMiddleware",
                      "spider.middleware.postfilters.PostFilterMiddleware",
                      "spider.middleware.storage.StorageMiddleWare"]

# List of locations of the template source files, in search order.

LOGGING_CONFIG = 'spider.utils.log.dictConfig'
# Custom logging configuration.
LOGGING = {}
CONF_DIR = os.path.split(os.path.realpath(__file__))[0]
