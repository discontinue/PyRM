# -*- coding: utf-8 -*-
"""
    PyRM - Basis Models
    ~~~~~~~~~~~~~~~~~~~

    Basis Model Klassen.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from PyRM.models import BaseLogModel
from PyRM.middleware import threadlocals
from utils.django_modeladmin import add_missing_fields

#______________________________________________________________________________


class BaseModel(BaseLogModel):
    """
    Grundmodell für fast alle Klassen.
    """
    erstellt_am = models.DateTimeField(default = datetime.now,
        help_text="Zeitpunkt der Erstellung",
    )
    erstellt_von = models.ForeignKey(
        User, blank=True, null=True, #editable=False,
        help_text="Benutzer der diesen Eintrag erstellt hat.",
        related_name="%(class)s_erstellt_von"
    )
    geaendert_am = models.DateTimeField(
        blank=True, null=True,
#        auto_now=True, # Bug?
        help_text="Zeitpunkt der letzten Änderung",
    )
    geaendert_von = models.ForeignKey(
        User, blank=True, null=True, #editable=False,
        help_text="Benutzer der diesen Eintrag zuletzt geändert hat.",
        related_name="%(class)s_geaendert_von"
    )

    notizen = models.TextField(blank=True, null=False)

    def save(self):
        current_user = threadlocals.get_current_user()

        if self.erstellt_von == None:
            # This is a new object
            self.erstellt_von = current_user
        else:
            self.geaendert_von = current_user
            self.geaendert_am = datetime.now()

        id = self.id
        erstellt_von = self.erstellt_von

        super(BaseModel,self).save()

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

BASE_FIELDSET = ('Metadaten', {
#    'classes': ('collapse',),
    'fields': (
        "erstellt_am", "erstellt_von",
        "geaendert_am", "geaendert_von",
        "notizen"
    )
})

#______________________________________________________________________________

class BasisPosten(BaseModel):
    """
    Basis für Aus-/Eingansposten
    """
    anzahl = models.PositiveIntegerField()
    beschreibung = models.TextField()
    einzelpreis = models.DecimalField(max_digits = 6, decimal_places = 2,)

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
    nummer = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Rechnungs Nummer"
    )

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

    konto = models.ForeignKey(
        "Konto", null=True, blank=True,
        related_name="%(class)s_konto_set",
    )
    ggkto = models.ForeignKey(
        "Konto", null=True, blank=True,
        help_text="Gegenkonto",
        related_name="%(class)s_ggkto_set",
    )

    summe = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        help_text="Summe aller einzelnen Posten.",
        null=True, blank=True
    )

    def __unicode__(self):
        return u"Re.Nr.%s" % self.id

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes
        ordering = ['-nummer']


