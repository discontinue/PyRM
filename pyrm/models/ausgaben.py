# coding: utf-8

"""
    pyrm - Ausgaben
    ~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

from decimal import Decimal
import datetime

from django.conf import settings
from django.db import models

import reversion # django-reversion

from pyrm.models.base_models import BaseModel


class Ausgaben(BaseModel):
    """
    Ausgaben/Eingansrechnungen
    """
    lieferant = models.ForeignKey("Lieferant", null=True, blank=True)
    anschrift = models.TextField(
        help_text="Abweichende Anschrift",
        null=True, blank=True
    )

    beschreibung = models.TextField(
        help_text=u"Rechnungstext"
    )
    betrag = models.DecimalField(
        max_digits=7, decimal_places=2,
        null=True, blank=True,
        help_text=u"Betrag der Rechnung (Netto zzgl.MwSt.)"
    )
    mwst = models.DecimalField(
        max_digits=4, decimal_places=2,
        null=True, blank=True,
        default=Decimal(str(settings.PYRM.DEFAULT_MWST)),
        help_text=u"MwSt. für diese Position.",
    )

    datum = models.DateField(null=True, blank=True,
        default=datetime.datetime.now(),
        help_text="Datum der Rechung."
    )
    lieferdatum = models.DateField(null=True, blank=True,
        help_text="Zeitpunkt der Leistungserbringung"
    )
    valuta = models.DateField(null=True, blank=True,
        help_text="Datum der Buchung laut Kontoauszug."
    )

    def __unicode__(self):
        return u'Ausgabe: "%s" %s (%s)' % (self.beschreibung, self.betrag, self.datum)

    class Meta:
        app_label = "pyrm"
        ordering = ['-datum']
        verbose_name = "Ausgaben"
        verbose_name_plural = "Ausgaben"

reversion.register(Ausgaben)
