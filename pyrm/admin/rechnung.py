# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.contrib import admin

from reversion.admin import VersionAdmin

from pyrm.models.rechnung import RechnungsPosten, Rechnung


class RechnungsPostenAdmin(VersionAdmin):
    list_display = (
        "anzahl", "beschreibung", "einzelpreis", "rechnung"
    )
    list_display_links = ("beschreibung",)
    list_filter = ("rechnung",)
    list_per_page = 20
    list_select_related = True
    search_fields = ("beschreibung",)

#    fieldsets = (
#        (None, {
#            'fields': ("anzahl", "beschreibung", "einzelpreis", "rechnung")
#        }),
#        BASE_FIELDSET
#    )
#    fieldsets = add_missing_fields(BasisPosten, fieldsets)


class PostenInline(admin.TabularInline):
#class PostenInline(admin.StackedInline):
    model = RechnungsPosten


class RechnungAdmin(VersionAdmin):
    inlines = (PostenInline,)
    list_display = ("nummer", "kunde", "datum", "valuta", "summe")
    list_display_links = ("nummer", "kunde")
    list_filter = ("mahnstufe", "kunde",)
    list_per_page = 20
    list_select_related = True
#    search_fields = ['foreign_key__related_fieldname']
#    fieldsets = (
#        (None, {
#            'fields': (
#                "nummer", "bestellnummer", "kunde", "anschrift", "summe",
#                "mahnstufe"
#            )
#        }),
#        ('Datum', {
##            'classes': ('collapse',),
#            'fields': ("datum", "lieferdatum", "versand", "valuta")
#        }),
#        BASE_FIELDSET,
#    )
#    fieldsets = add_missing_fields(Rechnung, fieldsets)
