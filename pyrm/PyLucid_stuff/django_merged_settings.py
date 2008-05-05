
from PyLucid.settings import *

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
    "PyRM"
)