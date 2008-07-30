#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Setup PyLucid
    ~~~~~~~~~~~~~

    -Create all PyRM pages.
        WARNING: Delete all existing pages!
    -delete existing PyRM tables
        WARNING: All PyRM data lost!
    -syncdb
    -install PyLucid base plugins
    -install PyRM plugin
"""

import sys, os
from pprint import pprint

os.environ["DJANGO_SETTINGS_MODULE"] = "PyRM_settings"
from django.conf import settings

print
print "WICHTIG:"
print "Es werden alle Daten der aktuellen installation gelöscht!!!"
print
print "Verwendet werden:"
print "setting modul.:", os.environ["DJANGO_SETTINGS_MODULE"]
print "Datenbank.....:", settings.DATABASE_NAME
print
try:
    raw_input("weiter mit ENTER, abbruch mit Strg-C...")
except KeyboardInterrupt:
    sys.exit(0)

print "Lösche Datei '%s'..." % settings.DATABASE_NAME,
try:
    os.remove(settings.DATABASE_NAME) # SQLite Datei löschen
except OSError, err:
    print "Fehler:", err
else:
    print "OK"

from django.core import management

import PyRM_settings

from PyLucid.models import Template, Style, Page, Plugin
from django.contrib.auth.models import User
#from PyLucid.system.detect_page import get_default_page
from PyLucid.system.plugin_manager import install_plugin, auto_install_plugins

sys.path.insert(0, "..") # Add PyLucid root
from tests.utils.FakeRequest import FakePageMsg


def delete_PyRM_tables():
    print "Delete all tables..."
    management.call_command('reset', "PyRM", verbosity=2, interactive=False)
    print "-"*80

def syncdb():
    print "syncdb..."
    management.call_command('syncdb', verbosity=1, interactive=False)
    print "-"*80

#------------------------------------------------------------------------------

class PageCreator(object):
    def __init__(self, user):
        #print Template.objects.all()
        #print Style.objects.all()
        #print User.objects.all()
        
        print "Nutzt User:", user
        
        # Default Einstellungen für alle Seiten
        self.defaults = {
            "template"      : Template.objects.get(name = "small_white"),
            "style"         : Style.objects.get(name = "small_white"),
            "markup"        : 0, # html
            "createby"      : user,
            "lastupdateby"  : user,
        }
        
        self.create_pages()
    
    def create_page(self, data):    
        page_data = self.defaults.copy()
        page_data.update(data)
        pprint(page_data)
        p = Page(**page_data)
        p.save()
        return p

    def create_pages(self):
        print "Delete all pages...",
        Page.objects.all().delete()
        print "OK"
    
        print "Create pages..."
        PyRM_root = self.create_page({
            "name":u"PyRM",
            "title": u"Python Rechnungsmanager",
            "content": "{% lucidTag PyRM_plugin.summary %}",
        })
        self.create_page({
            "name":u"Kunden",
            "content": (
                '<a href="/_admin/PyRM/kunde/">'
                'kunden im django admin panel bearbeiten'
                '</a>\n'
                '{% lucidTag PyRM_plugin.customers %}'
            ),
            "parent": PyRM_root,
        })
        page = self.create_page({
            "name":u"Rechnungen",
            "content":"{% lucidTag PyRM_plugin.bills %}",
            "parent": PyRM_root,
        })
        page = self.create_page({
            "name":u"Rechnung erstellen",
            "content":"{% lucidTag PyRM_plugin.create_bill %}",
            "parent": PyRM_root,
        })
    
        pages = Page.objects.all()
        print pages

#------------------------------------------------------------------------------

def setup_Plugins():
    fake_page_msg  = FakePageMsg()

    # install all internal plugin
    auto_install_plugins(debug=False, page_msg = fake_page_msg, verbosity=0)

    # install PyRM plugin
    install_plugin(
        package_name = "PyLucid.plugins_external",
        plugin_name  = "PyRM_plugin",

        page_msg  = fake_page_msg,
        verbosity = 2,
        user      = a_user,
        active    = True
    )

def create_user(username, password, email, is_staff, is_superuser):
    """
    Create a user and return the instance.
    """
    user = User.objects.create_user(username, email, password)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    return user

if __name__ == "__main__":
    #delete_PyRM_tables()
    syncdb()
    user = create_user(
        username="test",
        password="12345678",
        email="",
        is_staff=True,
        is_superuser=True,
    )
    PageCreator(user)
    setup_Plugins()