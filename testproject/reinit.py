#!/usr/bin/env python
# coding: utf-8

import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "testproject.settings"

try:
    import settings
except ImportError, err:
    import traceback
    print traceback.format_exc()
    print "-" * 79
    print "evtl. PyRM virtualenv nicht aktiviert???\n"
    sys.exit()

DATABASE_NAME = settings.DATABASES['default']['NAME']
IS_SQLITE = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'

print
print "WICHTIG:"
print "Es werden alle Daten der aktuellen installation gelöscht!!!"
print
print "Verwendet werden:"
print "setting modul.:", os.environ["DJANGO_SETTINGS_MODULE"]
print "Datenbank.....:", DATABASE_NAME
print
#try:
#    raw_input("weiter mit ENTER, abbruch mit Strg-C...")
#except KeyboardInterrupt:
#    sys.exit(0)

if IS_SQLITE:
    print "Lösche Datei '%s'..." % DATABASE_NAME,
    try:
        os.remove(DATABASE_NAME) # SQLite Datei löschen
    except OSError, err:
        print "Fehler:", err
    else:
        print "OK"


from django.core.management import setup_environ
project_directory = setup_environ(settings)

from django.core import management

assert("pyrm" in settings.INSTALLED_APPS)

if not IS_SQLITE:
    print "Delete all tables..."
    management.call_command('reset', "PyRM", verbosity=2, interactive=False)
    print "-" * 80

print "syncdb..."
management.call_command('syncdb', verbosity=1, interactive=False)
print "-" * 80


USERNAME = "test"
PASSWORD = "12345678"
print "create testuser '%s' with password '%s'..." % (USERNAME, PASSWORD),
from django.contrib.auth.models import User
#defaults = {'password':password, 'email':email}
user, created = User.objects.get_or_create(
    username=USERNAME#, defaults=defaults
)
user.email = ""
user.set_password(PASSWORD)
user.is_staff = True
user.is_superuser = True
user.save()
print "OK"

print "-" * 80

print "END"
