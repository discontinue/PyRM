# -*- coding: utf-8 -*-
"""
    pyrm_app - Rechnung
    ~~~~~~~~~~~~~~~~~~~~~~~

    + RechnungsPosten
    + Rechnung

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

from pyrm_app.models.base_models import BaseModel
from pyrm_app.models.base_models import BASE_FIELDSET
from pyrm_app.utils.django_modeladmin import add_missing_fields

#______________________________________________________________________________

class RechnungsPostenManager(models.Manager):
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

class RechnungsPosten(BaseModel):
    """
    Jede einzelne Position auf einer Rechnung.
    """
    objects = RechnungsPostenManager()

    anzahl = models.PositiveIntegerField(
#        help_text = u"Rechnungstext für diese Position."
    )
    beschreibung = models.TextField(
        help_text = u"Rechnungstext für diese Position."
    )
    einzelpreis = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        help_text = u"Preis pro Einheit"
    )

    def __unicode__(self):
        return self.beschreibung

    rechnung = models.ForeignKey(
        "Rechnung", #related_name="positionen"
    )

    class Meta:
        app_label = "pyrm_app"
        verbose_name = verbose_name_plural = "Rechnungsposten"


class RechnungsPostenAdmin(admin.ModelAdmin):
    list_display = (
        "anzahl", "beschreibung", "einzelpreis", "rechnung"
    )
    list_display_links = ("beschreibung",)
    list_filter = ("rechnung",)
    list_per_page = 20
    list_select_related = True
    search_fields = ("beschreibung",)

#    fieldsets = (
#        (None, {
#            'fields': ("anzahl", "beschreibung", "einzelpreis", "rechnung")
#        }),
#        BASE_FIELDSET
#    )
#    fieldsets = add_missing_fields(BasisPosten, fieldsets)

admin.site.register(RechnungsPosten, RechnungsPostenAdmin)

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

class Rechnung(BaseModel):
    """
    Rechnungen die man selber erstellt.
    """
    objects = RechnungManager()

    bestellnummer = models.CharField(
        max_length=128, null=True, blank=True,
        help_text="Bestell- bzw. Auftragsnummer"
    )

    datum = models.DateField(null=True, blank=True,
        help_text="Datum der Rechung."
    )
    lieferdatum = models.DateField(null=True, blank=True,
        help_text="Zeitpunkt der Leistungserbringung"
    )
    valuta = models.DateField(null=True, blank=True,
        help_text="Datum der Buchung laut Kontoauszug."
    )


    summe = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        help_text="Summe aller einzelnen Posten.",
        null=True, blank=True
    )

    def __unicode__(self):
        return u"Re.Nr.%s %s %i€" % (self.nummer, self.datum, self.summe)

    class Meta:
        app_label = "pyrm_app"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes
        ordering = ['-nummer']

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

    mahnstufe = models.PositiveIntegerField(default=0,
        help_text="Anzahl der verschickten Mahnungen."
    )

    class Meta:
        app_label = "pyrm_app"
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"



class PostenInline(admin.TabularInline):
#class PostenInline(admin.StackedInline):
    model = RechnungsPosten



class RechnungAdmin(admin.ModelAdmin):
#    inlines = (PostenInline,)
    list_display = ("nummer", "kunde", "datum", "valuta", "summe")
    list_display_links = ("nummer", "kunde")
    list_filter = ("mahnstufe", "kunde",)
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
        ('Datum', {
#            'classes': ('collapse',),
            'fields': ("datum", "lieferdatum", "versand", "valuta")
        }),
        BASE_FIELDSET,
    )
    fieldsets = add_missing_fields(Rechnung, fieldsets)

admin.site.register(Rechnung, RechnungAdmin)