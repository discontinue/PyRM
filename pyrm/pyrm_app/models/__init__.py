# -*- coding: utf-8 -*-
"""
    pyrm_app.models
    ~~~~~~~~~~~~~~

    The database models for pyrm_app

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.db.models import signals

#from model_logging import log_post_init, log_post_save, log_pre_delete, \
#                                                        ModelLog, BaseLogModel
from konten import Konto, KONTO_CHOICES, GNUCASH_SKR03_MAP, MWST, StSl
from stammdaten import Ort, Person, Firma, Kunde, Lieferant
from AusgangsRechnung import AusgangsRechnung, AusgangsPosten
from EingangsRechnung import EingangsRechnung, EingangsPosten

from modelvcs.signal_handler import register

register(
    Konto, StSl,
    Ort, Person, Firma, Kunde, Lieferant,
    AusgangsRechnung, AusgangsPosten,
    EingangsRechnung, EingangsPosten,
)