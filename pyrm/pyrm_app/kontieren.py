# -*- coding: utf-8 -*-

"""
    pyrm_app - kontieren
    ~~~~~~~~~~~~~~~~~~~~

    Geldeingang der Rechnungen notieren/kontrolieren

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys
from pyrm_app.utils.unicode_stringio import UnicodeStringIO

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.conf import settings
from django import forms

from pyrm_app.models import Rechnung, RechnungsPosten, Firma, Person, Kunde, Ort


AKTIVER_ZEITRAUM = Rechnung.objects.exist_date_range()



class EpochSelectForm(forms.Form):
#    quarter = QuarterChoiceField(epoch = AKTIVER_ZEITRAUM, reverse = True)
    pass


@login_required
def index(request):
    """
    Zeitraum auswählen
    """
    response = HttpResponse(mimetype='text/plain')

    old_stdout = sys.stdout
    sys.stdout = UnicodeStringIO()
    #--------------------------------------------------------------------------

    count = Rechnung.objects.all().count()

    form = EpochSelectForm()

    #--------------------------------------------------------------------------
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    context = {
        "count": count,
        "oldest": AKTIVER_ZEITRAUM[0],
        "newest": AKTIVER_ZEITRAUM[1],
        "form": form,
        "output": output,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }

    return render_to_response(
        "kontieren_select.html", context,
        context_instance=RequestContext(request)
    )
