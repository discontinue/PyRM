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
    """
    gewerbliche Auslandskunden mit gültiger UID arbeitest du mit Netto-VKP ohne die MwSt dazuzurechnen. Dafür muss dann aber auch auf der Rechnung drauf stehen, dass es sich um so einen Kunden handelt.
    """
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
    datev_nummer = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)
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
    mahnstufe ?
    """
    objects = RechnungManager()

    id = models.AutoField(primary_key=True)
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
    lieferdatum = models.DateField(null=True, blank=True)
    valuta = models.DateField(null=True, blank=True,
        help_text="Datum der Buchung laut Kontoauszug."
    )
    summe = models.FloatField(
        help_text="Wird automatisch aus den Rechnungspositionen erechnet.",
        null=True, blank=True
    )

    class Admin:
        pass

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"
        ordering = ['-id']

    def __unicode__(self):
        return u"Rechnung Nr.%s" % self.id

