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

from PyRM.models import StSl
from PyRM.models.base_models import BASE_FIELDSET
from PyRM.models.base_rechnung import BasisRechnung, BasisPosten, \
                                                                BasisPostenAdmin
from PyRM.utils.django_modeladmin import add_missing_fields

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

class AusgangsPosten(BasisPosten):
    """
    Jede einzelne Position auf einer Ausgangsrechnung.
    """
    objects = AusgangsPostenManager()

    rechnung = models.ForeignKey(
        "AusgangsRechnung", #related_name="positionen"
    )

    class Meta:
        app_label = "PyRM"
        verbose_name = "Ausgangsrechnung-Position"
        verbose_name_plural = "Ausgangsrechnung-Positionen"

admin.site.register(AusgangsPosten, BasisPostenAdmin)

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

class AusgangsRechnung(BasisRechnung):
    """
    Rechnungen die man selber erstellt.
    """
    objects = AusgangsRechnungManager()

    nummer = models.PositiveIntegerField(
        primary_key=True,
        help_text="Rechnungs Nummer"
    )

    kunde = models.ForeignKey("Kunde", null=True, blank=True)

    anschrift = models.TextField(
        help_text="Abweichende Anschrift",
        null=True, blank=True
    )
    versand = models.DateField(null=True, blank=True,
        help_text="Versanddatum der Rechnung."
    )

    konto = models.ForeignKey(
        "Konto", null=True, blank=True,
        related_name = "%(class)s_konto",
    )
    stsl = models.ForeignKey(StSl,
        blank=True, null=True,
        help_text = u"Der Datev-SteuerSchlüssel (StSl)"
    )
    ggkto = models.ForeignKey(
        "Konto", null=True, blank=True,
        related_name = "%(class)s_gkonto",
        help_text="Gegenkonto",
    )

    mahnstufe = models.PositiveIntegerField(default=0,
        help_text="Anzahl der verschickten Mahnungen."
    )

    class Meta:
        app_label = "PyRM"
        verbose_name = "Ausgangsrechnung"
        verbose_name_plural = "Ausgangsrechnungen"



class PostenInline(admin.TabularInline):
#class PostenInline(admin.StackedInline):
    model = AusgangsPosten



class AusgangsRechnungAdmin(admin.ModelAdmin):
#    inlines = (PostenInline,)
    list_display = ("nummer", "kunde", "datum", "valuta", "konto", "summe")
    list_display_links = ("nummer", "kunde")
    list_filter = ("mahnstufe", "kunde", "konto",)
    list_per_page = 20
    list_select_related = True
#    search_fields = ['foreign_key__related_fieldname']
    fieldsets = (
        (None, {
            'fields': (
                "nummer", "bestellnummer", "kunde", "anschrift", "summe",
                "mahnstufe"
            )
        }),
        ('Kontenrahmen', {
#            'classes': ('collapse',),
            'fields': ("konto", "stsl", "ggkto")
        }),
        ('Datum', {
#            'classes': ('collapse',),
            'fields': ("datum", "lieferdatum", "versand", "valuta")
        }),
        BASE_FIELDSET,
    )
    fieldsets = add_missing_fields(AusgangsRechnung, fieldsets)

admin.site.register(AusgangsRechnung, AusgangsRechnungAdmin)