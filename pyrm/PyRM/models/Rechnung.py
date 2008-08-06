# -*- coding: utf-8 -*-
"""
    PyRM - Rechnung
    ~~~~~~~~~~~~~~~

    Basis für Aus-/Eingangsrechungen

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

class BasisRechnung(models.Model):
    """
    Basis für Aus-/Eingangsrechungen
    """
    id = models.AutoField(primary_key=True)

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

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes