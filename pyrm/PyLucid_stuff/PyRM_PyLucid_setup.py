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


from django.core import management

import PyRM_settings

from PyLucid.models import Template, Style, Page, Plugin
from django.contrib.auth.models import User
#from PyLucid.system.detect_page import get_default_page
from PyLucid.system.plugin_manager import install_plugin, auto_install_plugins

sys.path.insert(0, "..") # Add PyLucid root
from tests.utils.FakeRequest import FakePageMsg


#print Template.objects.all()
#print Style.objects.all()
#print User.objects.all()
try:
    a_user = User.objects.get(is_superuser=True)[0]
except:
    a_user = User.objects.all()[0]

print "Nutzt User:", a_user


# Default Einstellungen für alle Seiten
PAGE_DEFAULTS = {
    "template"      : Template.objects.get(name = "small_white"),
    "style"         : Style.objects.get(name = "small_white"),
    "markup"        : 0, # html
    "createby"      : a_user,
    "lastupdateby"  : a_user,
}

def create_page(data):
    page_data = PAGE_DEFAULTS.copy()
    page_data.update(data)
    pprint(page_data)
    p = Page(**page_data)
    p.save()
    return p


def delete_PyRM_tables():
    print "Delete all tables..."
    management.call_command('reset', "PyRM", verbosity=2, interactive=False)
    print "-"*80

def syncdb():
    print "syncdb..."
    management.call_command('syncdb', verbosity=1, interactive=False)
    print "-"*80


def create_pages():
    print "Delete all pages...",
    Page.objects.all().delete()
    print "OK"

    print "Create pages..."
    index_page = create_page({
        "name":u"PyRM Login",
        "title": u"Python Rechnungsmanager - Login",
        "content": "{{ login_link }}",
    })
    PyRM_root = create_page({
        "name":u"PyRM",
        "title": u"Python Rechnungsmanager",
        "content": "{% lucidTag sub_menu %}",
        "parent": index_page,
    })
    create_page({
        "name":u"Übersicht",
        "content":"{% lucidTag PyRM_plugin.summary %}",
        "parent": PyRM_root,
    })
    create_page({
        "name":u"Kunden",
        "content":"{% lucidTag PyRM_plugin.customers %}",
        "parent": PyRM_root,
    })
    page = create_page({
        "name":u"Rechnungen",
        "content":"{% lucidTag PyRM_plugin.bills %}",
        "parent": PyRM_root,
    })
    page = create_page({
        "name":u"Rechnung erstellen",
        "content":"{% lucidTag PyRM_plugin.create_bill %}",
        "parent": PyRM_root,
    })


    pages = Page.objects.all()
    print pages

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


if __name__ == "__main__":
    delete_PyRM_tables()
    syncdb()
    create_pages()
    setup_Plugins()