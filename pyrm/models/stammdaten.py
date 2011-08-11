# coding: utf-8
"""
    pyrm - Stammdaten
    ~~~~~~~~~~~~~~~~~

    http://de.wikipedia.org/wiki/Stammdaten

     + Ortsangaben für Personen- und Firmen-Adressen.

     + Personen
     + Firmen

     + Kunden
     + Lieferanten

    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.db import models
from django.conf import settings

import reversion # django-reversion

from pyrm.models.base_models import BaseModel
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
#from pyrm.utils.django_modeladmin import add_missing_fields



GESCHLECHTER = (
    ('M', 'männlich'),
    ('W', 'weiblich'),
)

#______________________________________________________________________________


class Ort(models.Model):
    """
    Ort + Land für Personen- und Firmen-Adressen.
    Länder angabe ist als einfacher String hinterlegt.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    land = models.CharField(max_length=128, default=settings.PYRM.DEFAULT_LAND)

    class Meta:
        app_label = "pyrm"
        verbose_name = "Ort"
        verbose_name_plural = "Orte"
        ordering = ("name", "land")
        unique_together = (("name", "land"),)

    def __unicode__(self):
        if self.land == settings.PYRM.DEFAULT_LAND:
            return self.name
        else:
            return "%s (%s)" % (self.name, self.land)

reversion.register(Ort)

#______________________________________________________________________________


class FirmaPersonBaseModel(BaseModel):
    """
    Basis Klasse für Personen und Firmen mit allen gemeinsamen Felder.
    
    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
    """
    internet = models.URLField(verify_exists=False, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    telefon = models.CharField(max_length=32, blank=True, null=True)
    fax = models.CharField(max_length=32, blank=True, null=True)
    mobile = models.CharField(max_length=32, blank=True, null=True)

    strasse = models.CharField(max_length=128, blank=True, null=True)
    strassen_zusatz = models.CharField(max_length=128, blank=True, null=True)
    plz = models.PositiveIntegerField(blank=True, null=True)
    ort = models.ForeignKey(Ort, blank=True, null=True)

    #__________________________________________________________________________
    # Konto daten

    kontonr = models.CharField(
        max_length=128, # FIXME
        blank=True, null=True,
        help_text="Bank Kontonummer",
    )

    # Bankleitzahl
    # http://de.wikipedia.org/wiki/Bankleitzahl
    # zwei Dreierblöcken und einem Zweierblock
    # bsp.: "123 456 78"
    blz = models.CharField(
        max_length=10,
        blank=True, null=True,
        help_text="Bankleitzahl (8 Zahlen + zwei Leerzeichen)",
    )

    # IBAN
    # http://de.wikipedia.org/wiki/International_Bank_Account_Number
    # Unterschiedliche Länge!
    iban = models.CharField(
        max_length=38, #
        blank=True, null=True,
        help_text=(
            "International Bank Account Number"
            " (max. 31 Ziffern + 7 Leerzeichen)"
        ),
    )

    # SWIFT-BIC
    # http://de.wikipedia.org/wiki/SWIFT
    bic = models.CharField(
        max_length=11, # max. 11 Ziffern
        blank=True, null=True,
        help_text=(
            "BIC bzw. Bank Identifier Code"
            " (auch SWIFT-Adresse, keine Leerzeichen)"
        ),
    )
    class Meta:
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

#______________________________________________________________________________

class Firma(FirmaPersonBaseModel):
    name1 = models.CharField(max_length=80, help_text="Name der Firma1")
    name2 = models.CharField(
        max_length=80, null=True, blank=True, help_text="Name der Firma2"
    )

    # http://de.wikipedia.org/wiki/Umsatzsteuer-Identifikationsnummer
    # Niederlande, Schweden haben 12 Ziffern
    UStIdNr = models.CharField(
        max_length=12, null=True, blank=True,
        help_text="Umsatzsteuer-Identifikationsnummer (ohne Leerzeichen)"
    )

    #__________________________________________________________________________

    class Meta:
        app_label = "pyrm"
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"
        ordering = ['-lastupdatetime']

    def __unicode__(self):
        return self.name1


reversion.register(Firma)

#______________________________________________________________________________

class Person(FirmaPersonBaseModel):
    vorname = models.CharField(max_length=30, blank=True, null=True)
    nachname = models.CharField(max_length=30)

    geschlecht = models.CharField(
        blank=True, null=True, max_length=1, choices=GESCHLECHTER
    )

    geburtstag = models.DateField(blank=True, null=True)

    #__________________________________________________________________________

    class Meta:
        app_label = "pyrm"
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        unique_together = (("vorname", "nachname"),)

    def __unicode__(self):
        if self.vorname:
            return " ".join((self.vorname, self.nachname))
        else:
            return self.nachname

reversion.register(Person)


#______________________________________________________________________________

class Skonto(BaseModel):
    """
    Prozentualer Preisnachlass auf den Rechnungsbetrag bei Zahlung innerhalb
    des Zahlungsziels.
    """
    zahlungsziel = models.PositiveIntegerField(
        help_text="Zahlungseingangsdauer in Tagen"
    )
    skonto = models.FloatField(
        help_text="Prozentualer Preisnachlass"
    )
    netto = models.BooleanField(
        default=False,
        help_text=(
            "Skonto auf Netto-Umsatz (ohne Umsatzsteuer)"
            " oder auf Brutto-Umsatz?"
        )
    )
    def __unicode__(self):
        return u"%s Tag(e) - %s Prozent" % (self.zahlungsziel, self.skonto)

    class Meta:
        app_label = "pyrm"
        verbose_name = "Skonto"
        verbose_name_plural = "Skonto Einträge"
        ordering = ("zahlungsziel", "skonto")


reversion.register(Skonto)

#______________________________________________________________________________

class KundeLieferantBase(BaseModel):
    """
    Basis Klasse für Kunde und Lieferant
    """
    person = models.ForeignKey(
        Person, null=True, blank=True,
        related_name="%(class)s_person"
    )
    firma = models.ForeignKey(
        Firma, null=True, blank=True,
        related_name="%(class)s_firma"
    )

    lieferranten_nr = models.TextField(blank=True, null=True)

    seid = models.DateField(auto_now_add=True, null=True, blank=True)

    lieferstop_datum = models.DateField(blank=True, null=True)
    lieferstop_grund = models.TextField(blank=True, null=True)

    zahlungsziel = models.PositiveIntegerField(
        default=settings.PYRM.DEFAULT_ZAHLUNGSZIEL,
        help_text="max. Zahlungseingangsdauer in Tagen"
    )
    skonto = models.ManyToManyField(Skonto, verbose_name="Skonto liste",
        blank=True, null=True,
        help_text="FIXME"
    )

    def clean_fields(self, exclude):
        super(KundeLieferantBase, self).clean_fields(exclude)

        if "person" not in exclude and "firma" not in exclude:
            if self.person is None and self.firma is None:
                msg = ("Person und Firma können nicht beide leer sein!",)
                raise ValidationError({
                    "person": msg, "firma": msg
                })

    class Meta:
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

#______________________________________________________________________________


class Kunde(KundeLieferantBase):
    """
    Firmen- und Privat-Kunden für Rechnungen.
    """
    nummer = models.IntegerField(
        primary_key=True,
        help_text="Kundennummer Nummer"
    )
    anzeigen = models.BooleanField(
        help_text="Name der Person mit anzeigen, wenn es eine Firma ist?"
    )

    lieferrantennr = models.CharField(
        max_length=128, blank=True, null=True,
        help_text=(
            "Lieferrantennummer bei dieser Firma, falls vorhanden."
            " Wird auf jeder Rechnung aufgeführt"
        )
    )

    anzahl_rechnungen = models.PositiveSmallIntegerField(
        default=2,
        help_text=(
            "Wieviel Rechnungen sollen gedruckt werden?"
            " (z.B. 2x: eine zum Verschicken, eine für die Buchhaltung"
        )
    )
    anzahl_rechnungskopie = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Wieviel Rechnungens-Kopien sollen gedruckt werden?"
        )
    )

    mahnfrist = models.PositiveIntegerField(
        default=settings.PYRM.DEFAULT_MAHNFRIST,
        help_text="Frist in Tagen."
    )

    def range_rechnung(self):
        # http://stackoverflow.com/questions/1107737/numeric-for-loop-in-django-templates
        return xrange(self.anzahl_rechnungen)
    def range_kopie(self):
        return xrange(self.anzahl_rechnungskopie)

    def __unicode__(self):
        if self.firma:
            if self.anzeigen:
                return u"%s - %s" % (self.firma, self.person)
            else:
                return u"%s" % self.firma
        else:
            return u"%s" % self.person

    class Meta:
        app_label = "pyrm"
        ordering = ('-lastupdatetime',)
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"



reversion.register(Kunde)


#______________________________________________________________________________

class Lieferant(KundeLieferantBase):
    """
    Lieferanten für die Eingansrechnungen
    """
#    nummer = models.IntegerField(
    nummer = models.AutoField(
        primary_key=True,
        help_text="Lieferranten Nummer"
    )
    kundennummer = models.CharField(
        max_length=128, null=True, blank=True,
        help_text="Kundennummer bei diesem Lieferrant.",
    )

    def __unicode__(self):
        items = (str(self.nummer), unicode(self.firma), self.person)
        return u" - ".join([i for i in items if i])

    class Meta:
        app_label = "pyrm"
        verbose_name = "Lieferant"
        verbose_name_plural = "Lieferanten"
        ordering = ("firma", "person")


reversion.register(Lieferant)
