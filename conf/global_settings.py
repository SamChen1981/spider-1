# encoding=utf8
# Default Django settings. Override these with settings in the module
# pointed-to by the DJANGO_SETTINGS_MODULE environment variable.

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.

# Database connection info. If left empty, will default to the dummy backend.
DATABASES = []

# Classes used to implement DB routing behavior.
DATABASE_ROUTERS = []
SECRET_KEY = ''
# The email backend to use. For possible shortcuts see django.core.mail.
# The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending email.
EMAIL_HOST = 'localhost'

# Port for sending email.
EMAIL_PORT = 25

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# List of strings representing installed apps.
INSTALLED_APPS = ()
SAVE_PAGE_REGLIST = []
# 存储内容后端,用来筛选需要存储的字段
SAVE_PAGE_BACKENDS = ["spider.save_page.backends.invertlist.SavePageBackend"]
# 暂存区后端
STAGING_BACKENDS = ["spider.staging.backends.MongoStaging.StagingBackend"]
# 页面解析后端
PARSER_BACKENDS = [
    "spider.ContentResolver.backends.InverseList.backends.Inverted_List"]
# 消息队列系统后端
RABBITMQ_BACKENDS = ["spider.msgsystem.backends.rabbitmq"]
# 访问页面的网络接口后端，默认是twisted提供的客户端
INTERNET_BACKENDS = ["spider.internet.backends.twisted.twisted_client"]

# 处理中间件
MIDDLEWARE_CLASSES = ["spider.core.middleware.opener.OpenerMiddleware",
                      "spider.core.middleware.parser.ParserMiddleware",
                      "spider.core.middleware.postfilters.PostFilterMiddleware",
                      "spider.core.middleware.storage.StorageMiddleWare"]

# List of locations of the template source files, in search order.

LOGGING_CONFIG = 'spider.utils.log.dictConfig'
# Custom logging configuration.
LOGGING = {}
