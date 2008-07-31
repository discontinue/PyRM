# -*- coding: utf-8 -*-
"""
    PyRM - AusgangsRechnung
    ~~~~~~~~~~~~~~~~~~~~~~~

    + AusgangsPosten
    + AusgangsRechnung

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

class AusgangsPostenManager(models.Manager):
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

class AusgangsPosten(models.Model):
    """
    Jede einzelne Position auf einer Ausgangsrechnung.
    """
    objects = AusgangsPostenManager()

    id = models.AutoField(primary_key=True)

    anzahl = models.PositiveIntegerField()
    beschreibung = models.TextField()
    einzelpreis = models.FloatField()

    rechnung = models.ForeignKey(
        "AusgangsRechnung", #related_name="positionen"
    )

    class Meta:
        app_label = "PyRM"
        verbose_name = "Ausgangsrechnung-Position"
        verbose_name_plural = "Ausgangsrechnung-Positionen"

    def __unicode__(self):
        return self.beschreibung

class AusgangsPostenAdmin(admin.ModelAdmin):
    list_display = (
        "anzahl", "beschreibung", "einzelpreis", "rechnung"
    )
#        list_display_links = ("shortcut",)

admin.site.register(AusgangsPosten, AusgangsPostenAdmin)

#______________________________________________________________________________

class AusgangsRechnungManager(models.Manager):
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

class AusgangsRechnung(models.Model):
    """
    Rechnungen die man selber erstellt.
    """
    objects = AusgangsRechnungManager()

    id = models.AutoField(primary_key=True,
        help_text="ID - Rechnungsnummer"
    )

    bestellnummer = models.CharField(max_length=128, null=True, blank=True)
    datum = models.DateField()
    konto = models.ForeignKey(
        "Konto", null=True, blank=True,
        related_name="konto_set",
    )
    ggkto = models.ForeignKey(
        "Konto", help_text="Gegenkonto",
        related_name="gegenkonto_set",
        null=True, blank=True
    )
    kunde = models.ForeignKey("Kunde", null=True, blank=True)

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
        app_label = "PyRM"
        verbose_name = "Ausgangsrechnung"
        verbose_name_plural = "Ausgangsrechnungen"
        ordering = ['-id']

    def __unicode__(self):
        return u"Rechnung Nr.%s" % self.id

class AusgangsRechnungAdmin(admin.ModelAdmin):
    pass

admin.site.register(AusgangsRechnung, AusgangsRechnungAdmin)