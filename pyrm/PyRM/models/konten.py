# -*- coding: utf-8 -*-
"""
    Kontenrahmen
    ~~~~~~~~~~~~

    http://de.wikipedia.org/wiki/Kontenrahmen
    DATEV-Standardkontenrahmen 2008: http://www.datev.de/info-db/0907799

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.db import models
from django.conf import settings
from django.contrib import admin

from PyRM.models import MWST

KONTOARTEN = (
    ("A", "Aktivkonto"),
    ("P", "Passivkonto"),
    ("E", "Erlöskonto"),
    ("K", "Kostenkonto"),
    ("S", "Statistikkonto"),
)

class Konto(models.Model):

    datev_nummer = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    kontoart = models.CharField(max_length=1, choices=KONTOARTEN)
    mwst = models.CharField(max_length=1, choices=MWST, null=True, blank=True)

    class Meta:
        app_label = "PyRM"
        verbose_name = "Konto"
        verbose_name_plural = "Konten"

    def __unicode__(self):
        return self.name

#______________________________________________________________________________

class KontoAdmin(admin.ModelAdmin):
    list_display = (
        "datev_nummer", "kontoart", "mwst", "name"
    )
#        list_display_links = ("shortcut",)

admin.site.register(Konto, KontoAdmin)