# -*- coding: utf-8 -*-
"""
    PyRM - Basis Models
    ~~~~~~~~~~~~~~~~~~~

    Basis Model Klassen.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from datetime import datetime

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from PyRM.utils.django_modeladmin import add_missing_fields

from modelvcs.middleware import threadlocals

#______________________________________________________________________________

class BaseModel(models.Model):
    """
    Grundmodell für fast alle Klassen.
    """
    erstellt_am = models.DateTimeField(default = datetime.now,
        editable=False,
        help_text="Zeitpunkt der Erstellung",
    )
    erstellt_von = models.ForeignKey(
        User, blank=True, null=True, editable=False,
        help_text="Benutzer der diesen Eintrag erstellt hat.",
        related_name="%(class)s_erstellt_von"
    )
    geaendert_am = models.DateTimeField(
        editable=False,
        blank=True, null=True,
        help_text="Zeitpunkt der letzten Änderung",
    )
    geaendert_von = models.ForeignKey(
        User, blank=True, null=True, editable=False,
        help_text="Benutzer der diesen Eintrag zuletzt geändert hat.",
        related_name="%(class)s_geaendert_von"
    )

    notizen = models.TextField(blank=True, null=False)

    def save(self):
        current_user = threadlocals.get_current_user()

        if self.erstellt_von == None:
            # This is a new object
            self.erstellt_von = current_user
        else:
            self.geaendert_von = current_user
            self.geaendert_am = datetime.now()

        super(BaseModel,self).save()

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

BASE_FIELDSET = ('Metadaten', {
#    'classes': ('collapse',),
    'fields': (
#        "erstellt_am", "erstellt_von",
#        "geaendert_am", "geaendert_von",
        "notizen",
    )
})

#______________________________________________________________________________


