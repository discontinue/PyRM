#!/usr/bin/env python
# -*- coding: utf-8 -*-

print "Löscht alle Tabellen und erstell eine frische installation..."
print "Fortfahren? [ENTER]"
#raw_input()

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "PyRM.settings"

from django.core import management

print "Delete all tables..."
management.call_command('reset', "PyRM", verbosity=2, interactive=False)
print "-"*80

print "syncdb..."
management.call_command('syncdb', verbosity=1, interactive=False)
print "-"*80


print "create testuser..."
from django.contrib.auth.models import User
try:
    User.objects.get(username="test")
except User.DoesNotExist:
    print "Username: 'test'"
    print "Password: '12345678'"
    from django.contrib.auth.create_superuser import createsuperuser
    createsuperuser(username="test", email="none@no.com", password="12345678")
else:
    print "Skip, test user still exists."
print "-"*80

print "END"