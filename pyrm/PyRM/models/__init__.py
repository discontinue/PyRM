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

MWST = (
    (7, 7),
    (19, 19),
)

from konten import Konto
from stammdaten import Ort, Person, Firma, Kunde, Lieferant
from AusgangsRechnung import AusgangsRechnung, AusgangsPosten
from EingangsRechnung import EingangsRechnung, EingangsPosten