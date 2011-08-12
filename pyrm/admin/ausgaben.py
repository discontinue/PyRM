# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

from reversion.admin import VersionAdmin

class AusgabenAdmin(VersionAdmin):
#    inlines = (PostenInline,)
    list_display = ("betrag", "beschreibung", "datum", "valuta", "lastupdatetime")
    list_display_links = ("beschreibung",)
    list_filter = ("lieferant",)
#    list_per_page = 20
#    list_select_related = True
#    search_fields = ['foreign_key__related_fieldname']
