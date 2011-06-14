# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.contrib import admin

from pyrm.models.rechnung import RechnungsPosten, Rechnung
from pyrm.admin.rechnung import RechnungsPostenAdmin, RechnungAdmin
from pyrm.models.stammdaten import Ort, Person, Firma, Skonto, Kunde
from pyrm.admin.stammdaten import OrtAdmin, PersonAdmin, FirmaAdmin, SkontoAdmin, \
    KundeAdmin


admin.site.register(RechnungsPosten, RechnungsPostenAdmin)
admin.site.register(Rechnung, RechnungAdmin)

admin.site.register(Ort, OrtAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Firma, FirmaAdmin)

admin.site.register(Skonto, SkontoAdmin)
admin.site.register(Kunde, KundeAdmin)

