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

# django
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User

# PyRM
from PyRM.middleware import threadlocals
from utils.django_modeladmin import add_missing_fields

#______________________________________________________________________________

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
    land = models.CharField(max_length=128, default=settings.DEFAULT_LAND)

    class Meta:
        app_label = "PyRM"
        verbose_name = "Ort"
        verbose_name_plural = "Orte"
        ordering = ("name", "land")
        unique_together = (("name", "land"),)

    def __unicode__(self):
        if self.land == settings.DEFAULT_LAND:
            return self.name
        else:
            return "%s (%s)" % (self.name, self.land)

#______________________________________________________________________________


class OrtAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "land")
    list_display_links = ("name",)
    list_filter = ("land",)

admin.site.register(Ort, OrtAdmin)

#______________________________________________________________________________

class BaseModel(models.Model):
    """
    Basis Klasse für Person, Firma, Kunde und Lieferrant.
    """
    id = models.AutoField(primary_key=True)

    erstellt_am = models.DateTimeField(
        auto_now_add=True, help_text="Zeitpunkt der Erstellung",
    )
    erstellt_von = models.ForeignKey(
        User, editable=False, blank=True, null=True,
        help_text="Benutzer der diesen Eintrag erstellt hat.",
        related_name="%(class)s_erstellt_von"
    )
    geaendert_am = models.DateTimeField(
        auto_now=True, help_text="Zeitpunkt der letzten Änderung",
    )
    geaendert_von = models.ForeignKey(
        User, editable=False, blank=True, null=True,
        help_text="Benutzer der diesen Eintrag zuletzt geändert hat.",
        related_name="%(class)s_geaendert_von"
    )

    notizen = models.TextField(blank=True, null=True)

    def save(self):
        current_user = threadlocals.get_current_user()
        self.geaendert_von = current_user

        if self.erstellt_von == None:
            # This is a new object
            self.erstellt_von = current_user

        id = self.id
        erstellt_von = self.erstellt_von

        super(BaseModel,self).save()

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

#______________________________________________________________________________

class FirmaPersonBaseModel(BaseModel):
    """
    Basis Klasse für Personen und Firmen mit allen gemeinsamen Felder.
    """
    internet = models.URLField(verify_exists=False, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    telefon = models.PhoneNumberField(blank=True, null=True)
    fax = models.PhoneNumberField(blank=True, null=True)
    mobile = models.PhoneNumberField(blank=True, null=True)

    strasse = models.CharField(max_length=128, blank=True, null=True)
    strassen_zusatz = models.CharField(max_length=128, blank=True, null=True)
    plz = models.PositiveIntegerField(blank=True, null=True)
    ort = models.ForeignKey(Ort, blank=True, null=True)

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
        app_label = "PyRM"
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
        app_label = "PyRM"
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    def __unicode__(self):
        return self.name1


class FirmaAdmin(admin.ModelAdmin):
    list_display = (
        "name1", "plz", "ort",
        "erstellt_von", "erstellt_am", "geaendert_von", "geaendert_am",
    )
    list_display_links = ("name1",)
    list_filter = ("ort",)
    fieldsets = (
        (None, {
            'fields': ("name1","name2", "notizen")
        }),
        ("kontakt", {
            'fields': ("telefon", "mobile", "fax", "email", "internet")
        }),
        ("Adresse", {
            'fields': ("strasse", "strassen_zusatz", "plz", "ort")
        }),
        ("bank", {
            'fields': ("UStIdNr", "kontonr", "blz", "iban", "bic")
        }),
    )
    fieldsets = add_missing_fields(Firma, fieldsets)

admin.site.register(Firma, FirmaAdmin)

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
        app_label = "PyRM"
        verbose_name = "Person"
        verbose_name_plural = "Personen"
        unique_together = (("vorname", "nachname"),)

    def __unicode__(self):
        if self.vorname:
            return " ".join((self.vorname, self.nachname))
        else:
            return self.nachname


class PersonAdmin(admin.ModelAdmin):
    list_display = ("vorname", "nachname", "strasse", "plz", "ort")
    list_display_links = ("vorname", "nachname")
    list_filter = ("ort",)

admin.site.register(Person, PersonAdmin)


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
        app_label = "PyRM"
        verbose_name = "Skonto"
        verbose_name_plural = "Skonto Einträge"
        ordering = ("zahlungsziel", "skonto")

class SkontoAdmin(admin.ModelAdmin):
    pass

admin.site.register(Skonto, SkontoAdmin)


#______________________________________________________________________________


class Kunde(BaseModel):
    """
    Firmen- und Privat-Kunden für Ausgangsrechnungen.
    """
    nummer = models.IntegerField(
        unique=True, help_text="Kundennummer Nummer"
    )
    person = models.ForeignKey(Person, null=True, blank=True)
    anzeigen = models.BooleanField(
        help_text="Name der Person mit anzeigen, wenn es eine Firma ist?"
    )
    firma = models.ForeignKey(Firma, null=True, blank=True)

    seid = models.DateField(auto_now_add=True, null=True, blank=True)

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

    class Meta:
        app_label = "PyRM"
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
    list_display = ("nummer", "person", "firma",)

admin.site.register(Kunde, KundeAdmin)

#______________________________________________________________________________

class Lieferant(BaseModel):
    """
    Lieferanten für die Eingansrechnungen
    """
    nummer = models.IntegerField(
        unique=True, help_text="Lieferranten Nummer"
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

    class Meta:
        app_label = "PyRM"
        verbose_name = "Lieferant"
        verbose_name_plural = "Lieferanten"
        ordering = ("firma", "person")

class LieferantAdmin(admin.ModelAdmin):
    pass

admin.site.register(Lieferant, LieferantAdmin)