# -*- coding: utf-8 -*-
"""
    PyRM.models
    ~~~~~~~~~~~~~~

    The database models for PyRM

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

#______________________________________________________________________________

KONTOARTEN = (
    ("A", "Aktivkonto"),
    ("P", "Passivkonto"),
    ("E", "Erlöskonto"),
    ("K", "Kostenkonto"),
    ("S", "Statistikkonto"),
)

MWST = (
    (7, 7),
    (19, 19),
)

GESCHLECHTER = (
    ('F', '[Firma]'),
    ('M', 'männlich'),
    ('W', 'weiblich'),
)

#______________________________________________________________________________

class Ort(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    land = models.CharField(max_length=128, default=settings.DEFAULT_LAND)

    class Meta:
        verbose_name = "Ort"
        verbose_name_plural = "Orte"
        ordering = ("name", "land")

    def __unicode__(self):
        return self.name

class OrtAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "land")
    list_display_links = ("name",)
    list_filter = ("land",)

admin.site.register(Ort, OrtAdmin)

#______________________________________________________________________________

class FirmaPersonBaseModel(models.Model):
    """
    Alle gemeinsamen Felder bei Firma/Peron Model.
    """
    #__________________________________________________________________________
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
        max_length=10, # 8 Zahlen + zwei Leerzeichen
        blank=True, null=True,
        help_text = "Bankleitzahl",
    )

    # IBAN
    # http://de.wikipedia.org/wiki/International_Bank_Account_Number
    # Unterschiedliche Länge!
    iban = models.CharField(
        max_length=38, # max. 31 Ziffern + 7 Leerzeichen
        blank=True, null=True,
        help_text = "International Bank Account Number",
    )

    # SWIFT-BIC
    # http://de.wikipedia.org/wiki/SWIFT
    bic = models.CharField(
        max_length=11, # max. 11 Ziffern (keine Leerzeichen)
        blank=True, null=True,
        help_text = "BIC bzw. Bank Identifier Code (auch SWIFT-Adresse)",
    )
    class Meta:
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

#______________________________________________________________________________

class Firma(FirmaPersonBaseModel):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=30)

    lieferrantennr = models.CharField(max_length=30,
        help_text=(
            "Lieferrantennummer bei dieser Firma, falls vorhanden."
            " Wird auf jeder Rechnung aufgeführt"
        )
    )
    UStIdNr = models.CharField(max_length=30,
        help_text="Umsatzsteuer-Identifikationsnummer"
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
    id = models.AutoField(primary_key=True,
        help_text="ID - Kundennummer"
    )
    person = models.ForeignKey(Person, null=True, blank=True)
    anzeigen = models.BooleanField(
        help_text="Name der Person mit anzeigen, wenn es eine Firma ist?"
    )
    firma = models.ForeignKey(Firma, null=True, blank=True)

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
    id = models.AutoField(primary_key=True,
        help_text="ID - Lieferranten Nummer"
    )
    person = models.ForeignKey(Person, null=True, blank=True)
    firma = models.ForeignKey(Firma, null=True, blank=True)

    zahlungsziel = models.PositiveIntegerField(null=True, blank=True,
        help_text="Zahlungseingangsdauer in Tagen"
    )

    notizen = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Lieferant"
        verbose_name_plural = "Lieferanten"
        ordering = ("firma", "person")

class LieferantAdmin(admin.ModelAdmin):
    pass

admin.site.register(Lieferant, LieferantAdmin)
#______________________________________________________________________________

class Konto(models.Model):
    """
    http://bk.buhl.de/wiki/index.php/Kontenplan_SKR04
    """
    datev_nummer = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    kontoart = models.CharField(max_length=1, choices=KONTOARTEN)
    mwst = models.CharField(max_length=1, choices=MWST, null=True, blank=True)

    class Meta:
        verbose_name = "Konto"
        verbose_name_plural = "Konten"

    def __unicode__(self):
        return self.name


class KontoAdmin(admin.ModelAdmin):
    list_display = (
        "datev_nummer", "kontoart", "mwst", "name"
    )
#        list_display_links = ("shortcut",)

admin.site.register(Konto, KontoAdmin)

#______________________________________________________________________________

class RechnungsPositionManager(models.Manager):
    def all_with_summ(self):
        """
        Liefert alle Positionen zurück, fügt das Attribute 'summe' hinzu.
        """
        # Alle Positionen
        positionen = self.get_query_set()

        # Summe ausrechnen und Attribute anhängen
        for position in positionen:
            position.summe = position.anzahl * position.einzelpreis

        return positionen

    def create_all(self, positionen, rechnung):
        """
        -Speichert alle Positionen zu einer Rechnung.
        -Aktualisiert Rechnung.summe
        """
        preis_summe = 0
        for anzahl, txt, preis in positionen:
            preis_summe += anzahl * preis

            # Erstellt einen neuen Eintrag
            position = self.model(
                anzahl = anzahl,
                beschreibung = txt,
                einzelpreis = preis,
                rechnung = rechnung,
            )
            position.save()

        # Rechnung Summe aktualisieren
        rechnung.summe = preis_summe
        rechnung.save()

class RechnungsPosition(models.Model):
    objects = RechnungsPositionManager()

    id = models.AutoField(primary_key=True)

    anzahl = models.PositiveIntegerField()
    beschreibung = models.TextField()
    einzelpreis = models.FloatField()

    rechnung = models.ForeignKey("Rechnung", related_name="positionen")

    class Meta:
        verbose_name = "Rechnungs Position"
        verbose_name_plural = "Rechnungs Positionen"

    def __unicode__(self):
        return self.beschreibung

class RechnungsPositionAdmin(admin.ModelAdmin):
    list_display = (
        "anzahl", "beschreibung", "einzelpreis", "rechnung"
    )
#        list_display_links = ("shortcut",)

admin.site.register(RechnungsPosition, RechnungsPositionAdmin)

#______________________________________________________________________________

class RechnungManager(models.Manager):
    def create(self, data_dict):
        """
        Create a new entry, use only key-values from the data_dict if a field
        exist.
        """
#        for i in dir(self.model._meta):
#            print i, getattr(self.model._meta, i, "---")

        # Build a list of all existing fieldnames
        field_names = [f.name for f in self.model._meta.fields]

        kwargs = {}
        for key in data_dict:
            if not key in field_names:
                # skip non existing field
                continue
            kwargs[key] = data_dict[key]

        obj = self.model(**kwargs)
        obj.save()
        if not isinstance(obj, models.Model):
            raise AttributeError(obj)
        return obj

class Rechnung(models.Model):
    """
    """
    objects = RechnungManager()

    id = models.AutoField(primary_key=True,
        help_text="ID - Rechnungsnummer"
    )

    bestellnummer = models.CharField(max_length=128, null=True, blank=True)
    datum = models.DateField()
    konto = models.ForeignKey(
        Konto, related_name="konto", null=True, blank=True
    )
    ggkto = models.ForeignKey(
        Konto, related_name="gegenkonto", help_text="Gegenkonto",
        null=True, blank=True
    )
    kunde = models.ForeignKey(Kunde, null=True, blank=True)

    anschrift = models.TextField(
        help_text="Komplette Anschrift",
    )

    lieferdatum = models.DateField(null=True, blank=True,
        help_text="Zeitpunkt der Leistungserbringung"
    )
    versand = models.DateField(null=True, blank=True,
        help_text="Versanddatum der Rechnung."
    )

    valuta = models.DateField(null=True, blank=True,
        help_text="Datum der Buchung laut Kontoauszug."
    )
    mahnstufe = models.PositiveIntegerField(default=0,
        help_text="Anzahl der verschickten Mahnungen."
    )

    summe = models.FloatField(
        help_text="Wird automatisch aus den Rechnungspositionen erechnet.",
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"
        ordering = ['-id']

    def __unicode__(self):
        return u"Rechnung Nr.%s" % self.id

class RechnungAdmin(admin.ModelAdmin):
    pass

admin.site.register(Rechnung, RechnungAdmin)