# -*- coding: utf-8 -*-

"""
    pyrm_app - Eingangs-Rechnung
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Verwaltung für Eingangsrechnungen

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django import forms

from pyrm_app.models import Lieferant


class UploadForm(forms.Form):
    title = forms.ModelChoiceField(Lieferant.objects.all(), label="Lieferant")
    file  = forms.FileField(label="Datei")
    date = forms.DateField(label="Datum")

@login_required
def index(request):

    if request.method == 'POST':
        form = UploadForm(request.POST)
        if form.is_valid():
            # Do form processing here...
            #return HttpResponseRedirect('/url/on_success/')
            pass
    else:
        form = UploadForm()

    context = {
        "form": form,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }

    return render_to_response(
        "e-rechnung.html", context,
        context_instance=RequestContext(request)
    )