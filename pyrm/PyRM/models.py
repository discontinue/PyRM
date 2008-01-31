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
from django.db import models

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


class Ort(models.Model):
    name = models.CharField(max_length=30)

    class Admin:
        pass

    class Meta:
        verbose_name = "Ort"
        verbose_name_plural = "Orte"

    def __unicode__(self):
        return self.name


class Firma(models.Model):
    name = models.CharField(max_length=30)
    zusatz = models.TextField(blank=True,
        help_text="Für zusätze auf jeder Rechnung wie z.B. LieferrantenNr."
    )
    class Admin:
        pass

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmen"

    def __unicode__(self):
        return self.name


class Person(models.Model):
    vorname = models.CharField(max_length=30)
    nachname = models.CharField(max_length=30)
    email = models.EmailField(blank=True)

    class Admin:
        pass

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personen"

    def __unicode__(self):
        return " ".join((self.vorname, self.nachname))


class Kunde(models.Model):
    kundennummer = models.IntegerField()
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHTER)
    person = models.ForeignKey(Person)
    anzeigen = models.BooleanField(
        help_text="Name der Person mit anzeigen, wenn es eine Firma ist?"
    )
    firma = models.ForeignKey(Firma, null=True, blank=True)
    strasse = models.CharField(max_length=30)
    plz = models.PositiveIntegerField()
    ort = models.ForeignKey(Ort)

    class Admin:
        pass

    class Meta:
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"

    def __unicode__(self):
        return self.person


class Konto(models.Model):
    """
    http://bk.buhl.de/wiki/index.php/Kontenplan_SKR04
    """
    datev_nummer = models.PositiveIntegerField()
    name = models.CharField(max_length=30)
    kontoart = models.CharField(max_length=1, choices=KONTOARTEN)
    mwst = models.CharField(max_length=1, choices=MWST, null=True, blank=True)

    class Admin:
        list_display = (
            "datev_nummer", "kontoart", "mwst", "name"
        )
#        list_display_links = ("shortcut",)

    class Meta:
        verbose_name = "Konto"
        verbose_name_plural = "Konten"

    def __unicode__(self):
        return self.name


class RechnungsPosition(models.Model):
    anzahl = models.PositiveIntegerField()
    beschreibung = models.TextField()
    einzelpreis = models.FloatField()
    rechnung = models.ForeignKey("Rechnung", related_name="positionen")

    class Admin:
        list_display = (
            "anzahl", "beschreibung", "einzelpreis", "rechnung"
        )
#        list_display_links = ("shortcut",)

    class Meta:
        verbose_name = "Rechnungs Position"
        verbose_name_plural = "Rechnungs Positionen"

    def __unicode__(self):
        return self.beschreibung


class Rechnung(models.Model):
    rechnungnummer = models.IntegerField()
    bestellnummer = models.CharField(max_length=128, null=True, blank=True)
    konto = models.ForeignKey(Konto, related_name="konto")
    ggkto = models.ForeignKey(
        Konto, related_name="gegenkonto", help_text="Gegenkonto"
    )
    kunde = models.ForeignKey(Kunde)
#    positionen = models.ManyToManyField(RechnungsPosition)
    lieferdatum = models.DateField(null=True, blank=True)

    class Admin:
        pass

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"

    def __unicode__(self):
        return self.rechnungnummer

