
from PyLucid.settings import *

DEBUG = True
#DEBUG = False

#TEMPLATE_DEBUG = False
TEMPLATE_DEBUG = True

INTERNAL_IPS = ("localhost", "127.0.0.1", "192.168.7.3")

# Database connection info.
DATABASE_ENGINE = 'sqlite3'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'PyRM.db3'     # Or path to database file if using sqlite3.

# A tuple of strings designating all applications that are enabled in this
# Django installation. Each string should be a full Python path to a Python
# package that contains a Django application
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    "PyLucid",
    "PyLucid.system.PyLucidPlugins",
    "PyRM"
)

# Don't use the cache
CACHE_BACKEND = "dummy:///"

#______________________________________________________________________________
# PyRM

DEFAULT_ZAHLUNGSZIEL = 7
DEFAULT_MAHNFRIST = 30