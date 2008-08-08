# -*- coding: utf-8 -*-
"""
    PyRM - Basis Models
    ~~~~~~~~~~~~~~~~~~~

    Basis Model Klassen für Ein-/AusgangsRechnung

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

from PyRM.models.base_models import BaseModel, BASE_FIELDSET
from PyRM.utils.django_modeladmin import add_missing_fields
from PyRM.models import StSl

class BasisPosten(BaseModel):
    """
    Basis für Aus-/Eingansposten
    """
    anzahl = models.PositiveIntegerField(
#        help_text = u"Rechnungstext für diese Position."
    )
    beschreibung = models.TextField(
        help_text = u"Rechnungstext für diese Position."
    )
    einzelpreis = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        help_text = u"Preis pro Einheit"
    )

    def __unicode__(self):
        return self.beschreibung

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes
        ordering = ['rechnung']

#______________________________________________________________________________

class BasisPostenAdmin(admin.ModelAdmin):
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


#______________________________________________________________________________

class BasisRechnung(BaseModel):
    """
    Basis für Aus-/Eingangsrechungen
    """
    bestellnummer = models.CharField(
        max_length=128, null=True, blank=True,
        help_text="Bestell- bzw. Auftragsnummer"
    )

    datum = models.DateField(null=True, blank=True,
        help_text="Datum der Rechung."
    )
    lieferdatum = models.DateField(null=True, blank=True,
        help_text="Zeitpunkt der Leistungserbringung"
    )
    valuta = models.DateField(null=True, blank=True,
        help_text="Datum der Buchung laut Kontoauszug."
    )


    summe = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        help_text="Summe aller einzelnen Posten.",
        null=True, blank=True
    )

    def __unicode__(self):
        return u"Re.Nr.%s %s %i€" % (self.nummer, self.datum, self.summe)

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes
        ordering = ['-nummer']

