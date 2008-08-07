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

from django.db.models import signals

from model_logging import model_logging_init, model_logging_save, \
                                                        ModelLog, BaseLogModel
from konten import Konto, KONTO_CHOICES, GNUCASH_SKR03_MAP, MWST, StSl
from stammdaten import Ort, Person, Firma, Kunde, Lieferant
from AusgangsRechnung import AusgangsRechnung, AusgangsPosten
from EingangsRechnung import EingangsRechnung, EingangsPosten

LOGGED_MODELS = (
    Konto, StSl,
    Ort, Person, Firma, Kunde, Lieferant,
    AusgangsRechnung, AusgangsPosten,
    EingangsRechnung, EingangsPosten,
)
for model in LOGGED_MODELS:
    signals.post_init.connect(model_logging_init, sender=model)
    signals.post_save.connect(model_logging_save, sender=model)
#    signals.pre_save.connect(model_logging_save, sender=model)