# coding: utf-8

"""
    Kontenrahmen
    ~~~~~~~~~~~~

    http://de.wikipedia.org/wiki/Kontenrahmen

    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

from django.db import models
from django.contrib import admin
from pyrm.models.base_models import BaseModel


#______________________________________________________________________________

class Konto(BaseModel):
    nummer = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)

    class Meta:
        app_label = "pyrm"
        verbose_name = "Konto"
        verbose_name_plural = "Konten"

    def __unicode__(self):
        return u"%s - %s" % (self.nummer, self.name)

#______________________________________________________________________________

