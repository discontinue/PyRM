# -*- coding: utf-8 -*-
"""
    PyRM - Stammdaten
    ~~~~~~~~~~~~~~~~~

    http://de.wikipedia.org/wiki/Stammdaten

     + Ortsangaben für Personen- und Firmen-Adressen.

     + Personen
     + Firmen

     + Kunden
     + Lieferanten


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

#______________________________________________________________________________

GESCHLECHTER = (
    ('F', '[Firma]'),
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
    land = models.CharField(max_length=128, default=settings.DEFAULT_LAND)

    class Meta:
        verbose_name = "Ort"
        verbose_name_plural = "Orte"
        ordering = ("name", "land")

    def __unicode__(self):
        return self.name

#______________________________________________________________________________


class OrtAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "land")
    list_display_links = ("name",)
    list_filter = ("land",)

admin.site.register(Ort, OrtAdmin)

#______________________________________________________________________________

class FirmaPersonBaseModel(models.Model):
    """
    Basis Klasse für Personen und Firmen mit allen gemeinsamen Felder.
    """
    email = models.EmailField(blank=True)
    telefon = models.PhoneNumberField(blank=True, null=True)
    mobile = models.PhoneNumberField(blank=True, null=True)

    strasse = models.CharField(max_length=128, blank=True, null=True)
    strassen_zusatz = models.CharField(max_length=128, blank=True, null=True)
    plz = models.PositiveIntegerField(blank=True, null=True)
    ort = models.ForeignKey(Ort, blank=True, null=True)

    notizen = models.TextField(blank=True, null=True)

    #__________________________________________________________________________
    # Konto daten

    kontonr = models.CharField(

        max_length=128, # FIXME
        blank=True, null=True,
        help_text = "Bank Kontonummer",
    )

    # Bankleitzahl
    # http://de.wikipedia.org/wiki/Bankleitzahl
    # zwei Dreierblöcken und einem Zweierblock
    # bsp.: "123 456 78"
    blz = models.CharField(
        max_length=10,
        blank=True, null=True,
        help_text = "Bankleitzahl (8 Zahlen + zwei Leerzeichen)",
    )

    # IBAN
    # http://de.wikipedia.org/wiki/International_Bank_Account_Number
    # Unterschiedliche Länge!
    iban = models.CharField(
        max_length=38, #
        blank=True, null=True,
        help_text = (
            "International Bank Account Number"
            " (max. 31 Ziffern + 7 Leerzeichen)"
        ),
    )

    # SWIFT-BIC
    # http://de.wikipedia.org/wiki/SWIFT
    bic = models.CharField(
        max_length=11, # max. 11 Ziffern
        blank=True, null=True,
        help_text = (
            "BIC bzw. Bank Identifier Code"
            " (auch SWIFT-Adresse, keine Leerzeichen)"
        ),
    )
    class Meta:
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

#______________________________________________________________________________

class Firma(FirmaPersonBaseModel):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=30, help_text="Name der Firma (kurz)")
    volle_bezeichnung = models.CharField(
         help_text="Volle Firmenbezeichnung",
         max_length=128, null=True, blank=True
    )

    # http://de.wikipedia.org/wiki/Umsatzsteuer-Identifikationsnummer
    # Niederlande, Schweden haben 12 Ziffern
    UStIdNr = models.CharField(max_length=12,
        help_text="Umsatzsteuer-Identifikationsnummer (ohne Leerzeichen)"
    )

    #__________________________________________________________________________

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    def __unicode__(self):
        return self.name


class FirmaAdmin(admin.ModelAdmin):
    pass

admin.site.register(Firma, FirmaAdmin)

#______________________________________________________________________________

class Person(FirmaPersonBaseModel):
    id = models.AutoField(primary_key=True)

    vorname = models.CharField(max_length=30)
    nachname = models.CharField(max_length=30)
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHTER)

    #__________________________________________________________________________

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        unique_together = (("vorname", "nachname"),)

    def __unicode__(self):
        return " ".join((self.vorname, self.nachname))


class PersonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Person, PersonAdmin)


#______________________________________________________________________________

class Skonto(models.Model):
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
        verbose_name = "Skonto"
        verbose_name_plural = "Skonto Einträge"
        ordering = ("zahlungsziel", "skonto")

class SkontoAdmin(admin.ModelAdmin):
    pass

admin.site.register(Skonto, SkontoAdmin)


#______________________________________________________________________________


class Kunde(models.Model):
    """
    Firmen- und Privat-Kunden für Ausgangsrechnungen.
    """
    id = models.AutoField(primary_key=True,
        help_text="ID - Kundennummer"
    )
    person = models.ForeignKey(Person, null=True, blank=True)
    anzeigen = models.BooleanField(
        help_text="Name der Person mit anzeigen, wenn es eine Firma ist?"
    )
    firma = models.ForeignKey(Firma, null=True, blank=True)

    lieferrantennr = models.CharField(max_length=128,
        help_text=(
            "Lieferrantennummer bei dieser Firma, falls vorhanden."
            " Wird auf jeder Rechnung aufgeführt"
        )
    )

    lieferstop_datum = models.DateField(blank=True, null=True)
    lieferstop_grund = models.TextField(blank=True, null=True)

    zahlungsziel = models.PositiveIntegerField(
        default = settings.DEFAULT_ZAHLUNGSZIEL,
        help_text="max. Zahlungseingangsdauer in Tagen"
    )
    mahnfrist = models.PositiveIntegerField(
        default = settings.DEFAULT_MAHNFRIST,
        help_text="Frist in Tagen."
    )
    skonto = models.ManyToManyField(Skonto, verbose_name="Skonto liste")

    notizen = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"

    def __unicode__(self):
        if self.firma:
            if self.anzeigen:
                return u"%s - %s" % (self.firma, self.person)
            else:
                return u"%s" % self.firma
        else:
            return u"%s" % self.person


class KundeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Kunde, KundeAdmin)

#______________________________________________________________________________

class Lieferant(models.Model):
    """
    Lieferanten für die Eingansrechnungen
    """
    id = models.AutoField(primary_key=True,
        help_text="ID - Lieferranten Nummer"
    )
    kundenummer =  models.CharField(
        max_length=128, null=True, blank=True,
        help_text="Kundennummer bei diesem Lieferrant.",
    )
    person = models.ForeignKey(Person, null=True, blank=True)
    firma = models.ForeignKey(Firma, null=True, blank=True)

    zahlungsziel = models.PositiveIntegerField(null=True, blank=True,
        help_text="Zahlungseingangsdauer in Tagen"
    )
    skonto = models.ManyToManyField(Skonto, verbose_name="Skonto liste")

    notizen = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Lieferant"
        verbose_name_plural = "Lieferanten"
        ordering = ("firma", "person")

class LieferantAdmin(admin.ModelAdmin):
    pass

admin.site.register(Lieferant, LieferantAdmin)