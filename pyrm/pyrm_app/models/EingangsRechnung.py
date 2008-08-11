# -*- coding: utf-8 -*-
"""
    pyrm_app - EingansRechnung
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

from django.db import models
from django.contrib import admin

from pyrm_app.models import StSl
from pyrm_app.models.base_models import BASE_FIELDSET
from pyrm_app.models.base_rechnung import BasisRechnung, BasisPosten, \
                                                                BasisPostenAdmin
from pyrm_app.utils.django_modeladmin import add_missing_fields


class EingangsPosten(BasisPosten):
    """
    Einzelne Positionen auf einer Eingangsrechnung
    """
    rechnung = models.ForeignKey(
        "EingangsRechnung", #related_name="positionen"
    )

    konto = models.ForeignKey(
        "Konto", null=True, blank=True,
        related_name = "%(class)s_konto",
    )
    stsl = models.ForeignKey(StSl,
        blank=True, null=True,
        help_text = u"Der Datev-SteuerSchlüssel (StSl)"
    )
    ggkto = models.ForeignKey(
        "Konto", null=True, blank=True,
        related_name = "%(class)s_gkonto",
        help_text="Gegenkonto",
    )

    class Meta:
        app_label = "pyrm_app"
        verbose_name = "Eingangsrechnung-Position"
        verbose_name_plural = "Eingangsrechnung-Positionen"

#        ('Kontenrahmen', {
##            'classes': ('collapse',),
#            'fields': ("konto", "ggkto")
#        }),

admin.site.register(EingangsPosten, BasisPostenAdmin)


#______________________________________________________________________________


class EingangsRechnung(BasisRechnung):
    """
    Fremde Rechnungen die man selber beazhlen muß.
    i.d.R. für Waren-/Diensleistungseinkauf.
    """
    nummer = models.CharField(max_length= 50,
        null=True, blank=True,
        help_text="Rechnungs Nummer (optional)"
    )

    lieferant = models.ForeignKey("Lieferant", null=True, blank=True)

    class Meta:
        app_label = "pyrm_app"
        verbose_name = "Eingangsrechnung"
        verbose_name_plural = "Eingangsrechnungen"


class PostenInline(admin.TabularInline):
#class PostenInline(admin.StackedInline):
    model = EingangsPosten


class EingangsRechnungAdmin(admin.ModelAdmin):
#    inlines = (PostenInline,)
    list_display = ("nummer", "lieferant", "datum", "valuta", "summe")
    list_display_links = ("nummer", "lieferant")
    list_filter = ("lieferant", )
    list_per_page = 20
    list_select_related = True
#    search_fields = ['foreign_key__related_fieldname']
    fieldsets = (
        (None, {
            'fields': ("nummer", "lieferant","bestellnummer",)
        }),
        ('Datum', {
#            'classes': ('collapse',),
            'fields': ("datum", "lieferdatum", "valuta")
        }),
        BASE_FIELDSET,
    )
    fieldsets = add_missing_fields(EingangsRechnung, fieldsets)

admin.site.register(EingangsRechnung, EingangsRechnungAdmin)