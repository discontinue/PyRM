# coding: utf-8
"""
    pyrm.models
    ~~~~~~~~~~~

    The database models for pyrm

    :copyleft: 2008-2011 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


from django.db.models import signals

from stammdaten import Ort, Person, Firma, Kunde, Lieferant
from rechnung import Rechnung, RechnungsPosten

