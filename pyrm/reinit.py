#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "PyRM.settings"
#from django.conf import settings
from PyRM import settings

print
print "WICHTIG:"
print "Es werden alle Daten der aktuellen installation gelöscht!!!"
print
print "Verwendet werden:"
print "setting modul.:", os.environ["DJANGO_SETTINGS_MODULE"]
print "Datenbank.....:", settings.DATABASE_NAME
print
#try:
#    raw_input("weiter mit ENTER, abbruch mit Strg-C...")
#except KeyboardInterrupt:
#    sys.exit(0)

print "Lösche Datei '%s'..." % settings.DATABASE_NAME,
try:
    os.remove(settings.DATABASE_NAME) # SQLite Datei löschen
except OSError, err:
    print "Fehler:", err
else:
    print "OK"


from django.core.management import setup_environ
project_directory = setup_environ(settings)

from django.core import management

assert("PyRM" in settings.INSTALLED_APPS)

print "Delete all tables..."
management.call_command('reset', "PyRM", verbosity=2, interactive=False)
print "-"*80

print "syncdb..."
management.call_command('syncdb', verbosity=1, interactive=False)
print "-"*80


print "create testuser...",
USERNAME = "test"
PASSWORD = "12345678"
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

print "-"*80

print "END"