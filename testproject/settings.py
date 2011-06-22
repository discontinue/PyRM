# coding: utf-8

import os
import sys

_cwd = os.getcwd()
sys.path.insert(0, _cwd)
print "Current work dir:", _cwd

try:
    #from django_tools.utils import info_print;info_print.redirect_stdout()
    import django
    import django_tools
    import pyrm
except Exception, e:
    import traceback
    sys.stderr.write(traceback.format_exc())
    raise

BASE_PATH = os.path.abspath(os.path.dirname(pyrm.__file__))
#print BASE_PATH


from pyrm import app_settings as PYRM


#______________________________________________________________________________
# DJANGO STUFF

DEBUG = True


if DEBUG:
    from django.contrib.messages import constants as message_constants
    MESSAGE_LEVEL = message_constants.DEBUG


# A boolean that turns on/off template debug mode. If this is True, the fancy
# error page will display a detailed report for any TemplateSyntaxError.
# Note that Django only displays fancy error pages if DEBUG is True!
TEMPLATE_DEBUG = DEBUG

if TEMPLATE_DEBUG:
    # Display invalid (e.g. misspelled, unused) template variables
    # http://www.djangoproject.com/documentation/templates_python/#how-invalid-variables-are-handled
    # http://www.djangoproject.com/documentation/settings/#template-string-if-invalid
    TEMPLATE_STRING_IF_INVALID = "XXX INVALID TEMPLATE STRING '%s' XXX"

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#______________________________________________________________________________
# DATABASE SETUP

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# A boolean that specifies if data will be localized by default or not.
# If this is set to True, e.g. Django will display numbers and dates using the format of the current locale.
USE_L10N = True


# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(BASE_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

ADMIN_URL_PREFIX = "admin"

LOGIN_URL = "/%s/login/" % ADMIN_URL_PREFIX # TODO: Redirect after django login seems not to work

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    #'dbtemplates.loader.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_PATH, "templates"),
    os.path.expanduser("~/pyrm_env/src/django-reversion/src/reversion/templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "pyrm.context_processors.pyrm",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',

    # From http://code.google.com/p/django-tools/
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',

    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

ROOT_URLCONF = 'pyrm.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',

    'reversion', # https://github.com/etianen/django-reversion

    "pyrm",
)


# We must set a defaul DB settings here, otherwise managment commands doesn't work.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'pyrm_database.db3',
    }
}


#_______________________________________________________________________________

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-DE'

DATE_FORMAT = "%d.%m.%Y"

#_______________________________________________________________________________


try:
    import local_settings as _local_settings
    from local_settings import *
except ImportError, err:
    if str(err) == "No module named local_settings":
        msg = (
            "You should create a local_settings.py file in '%s' !"
            " (Original error was: %s)\n"
        ) % (_cwd, err)
        sys.stderr.write(msg)
        #from django.core.exceptions import ImproperlyConfigured
        #raise ImproperlyConfigured(msg)
    else:
        raise
else:
    print "Use %r, ok." % _local_settings.__file__
    del(_local_settings)
