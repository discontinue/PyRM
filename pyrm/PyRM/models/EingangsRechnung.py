# -*- coding: utf-8 -*-
"""
    PyRM - EingansRechnung
    ~~~~~~~~~~~~~~~~~~~~~~~

    + EingansPosten
    + EingansRechnung

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
from django.conf import settings
from django.db import models
from django.contrib import admin

from PyRM.models.Rechnung import BasisRechnung, BasisPosten, BasisPostenAdmin
from utils.django_modeladmin import add_missing_fields


class EingangsPosten(BasisPosten):
    """
    Einzelne Positionen auf einer Eingangsrechnung
    """
    class Meta:
        app_label = "PyRM"
        verbose_name = "Eingangsrechnung-Position"
        verbose_name_plural = "Eingangsrechnung-Positionen"

admin.site.register(EingangsPosten, BasisPostenAdmin)


#______________________________________________________________________________


class EingangsRechnung(BasisRechnung):
    """
    Fremde Rechnungen die man selber beazhlen muß.
    i.d.R. für Waren-/Diensleistungseinkauf.
    """
    lieferant = models.ForeignKey("Lieferant", null=True, blank=True)

    class Meta:
        app_label = "PyRM"
        verbose_name = "Eingangsrechnung"
        verbose_name_plural = "Eingangsrechnungen"
        ordering = ['-id']

class PostenInline(admin.TabularInline):
#class PostenInline(admin.StackedInline):
    model = EingangsPosten

class EingangsRechnungAdmin(admin.ModelAdmin):
    inlines = [
        PostenInline,
    ]
    fieldsets = (
        (None, {
            'fields': ("nummer", "lieferant","bestellnummer",)
        }),
        ('Kontenrahmen', {
#            'classes': ('collapse',),
            'fields': ("konto", "ggkto")
        }),
        ('Datum', {
#            'classes': ('collapse',),
            'fields': ("datum", "lieferdatum", "valuta")
        }),
    )
    fieldsets = add_missing_fields(EingangsRechnung, fieldsets)

admin.site.register(EingangsRechnung, EingangsRechnungAdmin)