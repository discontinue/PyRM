# coding: utf-8

"""
    Kontenrahmen
    ~~~~~~~~~~~~

    http://de.wikipedia.org/wiki/Kontenrahmen

    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

from django.contrib import admin
from pyrm.models.konten import Konto


class KontoAdmin(admin.ModelAdmin):
    list_display = ("nummer", "name")
    list_display_links = ("name",)
#    fieldsets = (
#        (None, {
#            'fields': ("datev_nummer", "name", "kontoart", "mwst", "anzahl")
#        }),
#        BASE_FIELDSET
#    )
#    fieldsets = add_missing_fields(Konto, fieldsets)


