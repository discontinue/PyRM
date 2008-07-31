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



class EingangsPosten(models.Model):
    """
    Einzelne Positionen auf einer Eingangsrechnung
    """
    id = models.AutoField(primary_key=True)

    beschreibung = models.TextField()
    einkaufspreis = models.FloatField()

    eingangsrechnung = models.ForeignKey(
        "EingangsRechnung",
        #related_name="eingangs_posten",
    )
    class Meta:
        app_label = "PyRM"
        verbose_name = "Eingangsrechnung-Position"
        verbose_name_plural = "Eingangsrechnung-Positionen"

class EingangsPostenAdmin(admin.ModelAdmin):
    pass

admin.site.register(EingangsPosten, EingangsPostenAdmin)


#______________________________________________________________________________


class EingangsRechnung(models.Model):
    """
    Fremde Rechnungen die man selber beazhlen muß.
    i.d.R. für Waren-/Diensleistungseinkauf.
    """
    id = models.AutoField(primary_key=True,)

    rechnungsnummer = models.CharField(
         max_length=128, null=True, blank=True,
         help_text="Rechnungsnummer",
    )

    class Meta:
        app_label = "PyRM"
        verbose_name = "Eingangsrechnung"
        verbose_name_plural = "Eingangsrechnungen"
        ordering = ['-id']

class EingangsRechnungAdmin(admin.ModelAdmin):
    pass

admin.site.register(EingangsRechnung, EingangsRechnungAdmin)