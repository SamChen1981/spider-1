#encoding=utf8

# Default Django settings. Override these with settings in the module
# pointed-to by the DJANGO_SETTINGS_MODULE environment variable.

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.

# Database connection info. If left empty, will default to the dummy backend.
DATABASES = {
                "HOST":"localhost",
                "password":"123456",
                "name":"mysql",
                "PORT":"3306",
                "database":"spider"
             }

# Classes used to implement DB routing behavior.
DATABASE_ROUTERS = []

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
INSTALLED_MODELS= ()
SAVE_PAGE_REGLIST=[]



# List of locations of the template source files, in search order.



