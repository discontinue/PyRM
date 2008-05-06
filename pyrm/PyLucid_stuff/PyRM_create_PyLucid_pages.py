#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create all PyRM pages.

WARNING: Delete all existing pages!!!
"""

import os
from pprint import pprint

os.environ["DJANGO_SETTINGS_MODULE"] = "PyRM_settings"

import PyRM_settings

from PyLucid.models import Page, Plugin
from PyLucid.system.detect_page import get_default_page


class PageMaker(object):
    def __init__(self, default_page):
        default_data = default_page.__dict__
        for key in ("id", "lastupdatetime", "createtime", "parent_id",):
            del(default_data[key])
        default_data["markup"] = 2 # TinyTextile
        self.default_data = default_data

    def create_page(self, data):
        page_data = self.default_data.copy()
        page_data.update(data)
        pprint(page_data)
        p = Page(**page_data)
        p.save()
        return p

pages = Page.objects.all()
print pages

# Get default page data
default_page = get_default_page(request=None)
p = PageMaker(default_page)

print "Delete all pages...",
Page.objects.all().delete()
print "OK"

print "Create pages..."
index_page = p.create_page({
    "name":u"PyRM",
    "title": u"Python Rechnungsmanager",
    "content": (
        u"Zuerst must du das 'PyRM_plugin' installieren & aktivieren:\n\n"
        "sub menu / miscellaneous / Plugin administration\n\n"
        "h2. PyRM\n\n"
        "{% lucidTag sub_menu %}"
    ),
})
p.create_page({
    "name":u"Übersicht",
    "content":"{% lucidTag PyRM_plugin.summary %}",
    "parent": index_page,
})
p.create_page({
    "name":u"Kunden",
    "content":"{% lucidTag PyRM_plugin.customers %}",
    "parent": index_page,
})
page = p.create_page({
    "name":u"Rechnungen",
    "content":"{% lucidTag PyRM_plugin.bills %}",
    "parent": index_page,
})
page = p.create_page({
    "name":u"erstellen",
    "content":"{% lucidTag PyRM_plugin.create_bill %}",
    "parent": page,
})


pages = Page.objects.all()
print pages