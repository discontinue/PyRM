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
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django import forms


from django_addons.forms_addons import QuarterChoiceField
from pyrm_app.utils.unicode_stringio import UnicodeStringIO
from pyrm_app.models import Rechnung, RechnungsPosten, Firma, Person, Kunde, Ort



AKTIVER_ZEITRAUM = Rechnung.objects.exist_date_range()



class EpochSelectForm(forms.Form):
    quarter = QuarterChoiceField(epoch = AKTIVER_ZEITRAUM, reverse = True)



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

    if request.method == 'POST':
        form = EpochSelectForm(request.POST)
        if form.is_valid():
            start, end = form.cleaned_data["quarter"]
            print start, end
            
            # Geht nicht, warum?
#            url = reverse(
#                "pyrm_app-kontieren-kontieren",
#                kwargs = {
#                    "day1": start.day, 
#                    "month1": start.month, 
#                    "year1": start.year, 
#                    "day2": end.day,
#                    "month2": end.month,
#                    "year2": end.year,
#                }
#            )
            url = "/kontieren/%s.%s.%s-%s.%s.%s/" % (
                start.day, start.month, start.year, 
                end.day, end.month, end.year,
            )
            return HttpResponseRedirect(url)
    else:
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

@login_required
def kontieren(request, start, end):
    """
    TODO: weitermachen!
    """
    def to_date(date_string):
        """
        FIXME
        """
        day, month, year = [int(i) for i in date_string.split(".")]
        return datetime.date(year, month, day)
        
    response = HttpResponse(mimetype='text/plain')

    old_stdout = sys.stdout
    sys.stdout = UnicodeStringIO()
    #--------------------------------------------------------------------------
    print start, end
    start_date = to_date(start)
    end_date = to_date(end)
    #--------------------------------------------------------------------------
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    context = {
#        "count": count,
        "oldest": start_date,
        "newest": end_date,
#        "form": form,
        "output": output,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }

    return render_to_response(
        # TODO: Create new template for this view
        "kontieren_select.html", context,
        context_instance=RequestContext(request)
    )