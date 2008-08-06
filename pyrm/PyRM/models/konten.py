# -*- coding: utf-8 -*-
"""
    Kontenrahmen
    ~~~~~~~~~~~~

    http://de.wikipedia.org/wiki/Kontenrahmen
    DATEV-Standardkontenrahmen 2008: http://www.datev.de/info-db/0907799

http://svn.gnucash.org/trac/browser/gnucash/trunk/accounts/de_DE/acctchrt_skr03.gnucash-xea

    http://www.koders.com/?s=SKR03&la=*&li=*

"unternehmer" berlios.de - SKR03 Daten sind 2 Jahre alt!
http://svn.berlios.de/viewcvs/unternehmer/trunk/unstable/sql/
http://svn.berlios.de/wsvn/unternehmer/trunk/unstable/sql/Germany-DATEV-SKR03EU-chart.sql
http://svn.berlios.de/wsvn/unternehmer/trunk/unstable/sql/Germany-DATEV-SKR03EU-gifi.sql



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

from PyRM.models.base_models import BaseModel, BASE_FIELDSET
from utils.django_modeladmin import add_missing_fields

#______________________________________________________________________________

KONTOARTEN = (
    (6, u"INCOME",      u"Einnahmen"),
    (7, u"EXPENSE",     u"Aufwändungen"),
    (1, u"ASSET",       u"Aktivposten"),
    (2, u"RECEIVABLE",  u"offen"),
    (3, u"EQUITY",      u"Eigenkapital"),
    (4, u"LIABILITY",   u"Verbindlichkeit"),
    (5, u"PAYABLE",     u"fällig"),
)
KONTO_CHOICES = [(i[0], i[2]) for i in KONTOARTEN]
GNUCASH_SKR03_MAP = dict([(i[1], i[0]) for i in KONTOARTEN])

MWST = (
    (7, 7),
    (16, 16),
    (19, 19),
)

#______________________________________________________________________________

class Konto(BaseModel):
    datev_nummer = models.PositiveIntegerField()
    name = models.CharField(max_length=150)

    kontoart = models.PositiveIntegerField(
        max_length=1, choices=KONTO_CHOICES
    )
    mwst = models.PositiveIntegerField(
        max_length=1, choices=MWST, null=True, blank=True
    )

    anzahl = models.PositiveIntegerField(
        default=0,
        help_text="Wie oft wurde dieses Konto verwendet (Nur für Sortierung)"
    )

    class Meta:
        app_label = "PyRM"
        verbose_name = "Konto"
        verbose_name_plural = "Konten"
        ordering = ["anzahl", "datev_nummer"]

    def __unicode__(self):
        return u"%(datev_nummer)s - %(name)s - %(anzahl)s" % self.__dict__

#______________________________________________________________________________

class KontoAdmin(admin.ModelAdmin):
    list_display = ("datev_nummer", "kontoart", "mwst", "name", "anzahl")
    list_display_links = ("name",)
    list_filter = ("kontoart", "mwst")
    fieldsets = (
        (None, {
            'fields': ("datev_nummer", "name", "kontoart", "mwst", "anzahl")
        }),
        BASE_FIELDSET
    )
    fieldsets = add_missing_fields(Konto, fieldsets)

admin.site.register(Konto, KontoAdmin)