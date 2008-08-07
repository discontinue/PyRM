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

from model_logging import log_post_init, log_pre_save, log_post_save, \
                                        log_pre_delete, ModelLog, BaseLogModel
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
    signals.post_init.connect(log_post_init, sender=model)
    signals.pre_save.connect(log_pre_save, sender=model)
    signals.post_save.connect(log_post_save, sender=model)
    signals.pre_delete.connect(log_pre_delete, sender=model)