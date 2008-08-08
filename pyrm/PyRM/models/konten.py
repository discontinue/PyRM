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


    Im DATEV-Erfassungssystem werden Buchungs- und Steuerschlüssel an die
    sechste Stelle vor das Gegenkonto gesetzt
    (Vgl. Nr. 7: vor Konto (0)4530 steht der Steuerschlüssel 9 (16% VSt).

    Zu den Erlöskonten 8400  8409 ist der Steuerschlüssel 3 (USt 16 %)
    hinterlegt (<Mandant> <Kontenplan> <Eigenschaften> Steuerschlüssel), zu
    den Erlöskonten 8300  8314 entsprechend der Steuerschlüssel 2 (USt 7 %).

    Zu den WE-Konten 3400  3420 ist der Steuerschlüssel 9 (VSt 16 %)
    hinterlegt (<Mandant> <Kontenplan> <Eigenschaften> Steuerschlüssel), zu den
    WE-Konten 3300  3320 entsprechend der Steuerschlüssel 8 (VSt 7 %).

    Zu den Konten der 4-er Klasse ist kein Steuerschlüssel hinterlegt.
    Der Steuerschlüssel 9 (VSt 16%) bzw. der Steuerschlüssel 8 (VSt 7%) wird
    vor das Gegenkonto gesetzt.

    Es ist möglich die Konten der 4-er Klasse mit Steuerschlüsseln zu versehen.
    Ratsam ist das nicht. In der Regel sind z.B. nicht alle Bürokosten mit
    16% Vorsteuer belastet. Bei unberech-tigten Vorsteuerabzügen kann mit
    keinem Wohlwollen eines Betriebsprüfers gerechnet werden.


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

from modelvcs.messages import add_message

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

# Der Steuerschlüssel steht der datev kontonummer vorran und gibt den
# Prozentwert der MwSt. an.
STEUER_SCHLUESSEL = (
    (3, 19, u"Umsatzsteuer 19%"),
    (5, 16, u"Umsatzsteuer 16%"),
    (7, 16, u"Vorsteuer 16%"),
    (8,  7, u"Vorsteuer 7%"),
    (9, 19, u"Vorsteuer 19%"),
)
#______________________________________________________________________________
class StSlManager(models.Manager):
    def setup(self):
        """
        Alle vorhanden Werte aus STEUER_SCHLUESSEL eintragen
        """
        for data in STEUER_SCHLUESSEL:
            entry = self.model(
                id = data[0],
                steuersatz = data[1],
                beschreibung = data[2],
            )
            add_message(entry, "Neuer Eintrag durch StSlManager.setup()")
            print "neuer Eintrag:", entry#.__dict__
            entry.save()

class StSl(BaseModel):
    """
    Datev-SteuerSchlüssel
    """
    objects = StSlManager()

    id = models.PositiveIntegerField("schluessel", primary_key=True)
    steuersatz = models.PositiveIntegerField()
    beschreibung = models.CharField(max_length=150)

    class Meta:
        app_label = "PyRM"
        verbose_name = verbose_name_plural = u"Steuerschlüssel (StSl)"
        ordering = ("id",)

    def __unicode__(self):
#        return repr(self.__dict__)
        return u"StSl.%s - %s%% (%s)" % (
            self.id, self.steuersatz, self.beschreibung
        )
#______________________________________________________________________________

class StSlAdmin(admin.ModelAdmin):
    list_display = ("id", "steuersatz", "beschreibung")
    list_display_links = ("beschreibung",)
    list_filter = ("steuersatz",)
    fieldsets = (
        (None, {
            'fields': ("id", "steuersatz", "beschreibung")
        }),
        BASE_FIELDSET
    )
    fieldsets = add_missing_fields(StSl, fieldsets)

admin.site.register(StSl, StSlAdmin)

#______________________________________________________________________________

class Konto(BaseModel):
    datev_nummer = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)

    kontoart = models.PositiveIntegerField(
        max_length=1, choices=KONTO_CHOICES, null=True, blank=True
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
#        return repr(self.__dict__)
        return u" - ".join(
            (str(self.datev_nummer), repr(self.name),
            str(self.kontoart), str(self.anzahl))
        )

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