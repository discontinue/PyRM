# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


from django.contrib import admin

from reversion.admin import VersionAdmin

from pyrm.models.stammdaten import Person, Firma


class OrtAdmin(VersionAdmin):
    list_display = ("id", "name", "land")
    list_display_links = ("name",)
    list_filter = ("land",)

class PersonInline(admin.TabularInline):
    model = Person

class PersonAdmin(VersionAdmin):
    list_display = ("vorname", "nachname", "strasse", "plz", "ort")
    list_display_links = ("vorname", "nachname")
    list_filter = ("ort",)



class FirmaInline(admin.TabularInline):
    model = Firma

class FirmaAdmin(VersionAdmin):
    list_display = (
        "name1", "plz", "ort", "lastupdatetime", "createtime"
        #"erstellt_von", "erstellt_am", "geaendert_von", "geaendert_am",
    )
    list_display_links = ("name1",)
    list_filter = ("ort",)
#    fieldsets = (
#        (None, {
#            'fields': ("name1", "name2", "notizen")
#        }),
#        ("kontakt", {
#            'fields': ("telefon", "mobile", "fax", "email", "internet")
#        }),
#        ("Adresse", {
#            'fields': ("strasse", "strassen_zusatz", "plz", "ort")
#        }),
#        ("bank", {
#            'fields': ("UStIdNr", "kontonr", "blz", "iban", "bic")
#        }),
#    )
#    fieldsets = add_missing_fields(Firma, fieldsets)


class SkontoAdmin(VersionAdmin):
    pass




class KundeAdmin(VersionAdmin):
#    inlines = (PersonInline,FirmaInline)
    list_display = list_display_links = ("nummer", "person", "firma",)
#    fieldsets = (
#        ("Basis Daten", {
#            'fields': (
#                "nummer", "lieferrantennr", "person", "anzeigen", "firma",
#                "notizen"
#            )
#        }),
#        ("Lieferstop", {
##            'classes': ('collapse',),
#            'fields': ("lieferstop_datum", "lieferstop_grund")
#        }),
#        ("Zeiten", {
##            'classes': ('collapse',),
#            'fields': ("mahnfrist", "zahlungsziel",)
#        }),
#    )
#    fieldsets = add_missing_fields(Kunde, fieldsets)





