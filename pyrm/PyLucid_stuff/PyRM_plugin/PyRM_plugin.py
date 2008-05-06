# -*- coding: utf-8 -*-
"""
    PyRM - PyLucid plugin
    ~~~~~~~~~~~~~~~~~~~~~

    http://sourceforge.net/projects/pyrm/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev: $"

from django.utils.translation import ugettext as _
from django import newforms as forms

from PyLucid.system.BasePlugin import PyLucidBasePlugin

from PyRM.models import Konto, Kunde, RechnungsPosition, Rechnung


class CreateBillForm(forms.Form):
    """
    Form for creating a bill.
    http://www.djangoproject.com/documentation/newforms/
    """
    rechnungnummer = forms.IntegerField()
    bestellnummer = forms.IntegerField()
    datum = forms.DateTimeField()

    kunde = forms.ModelChoiceField(Konto.objects.all())
    ggkto = forms.ModelChoiceField(Konto.objects.all())
    kunde = forms.ModelChoiceField(Kunde.objects.all())

    lieferdatum = forms.DateTimeField()


class PyRM_plugin(PyLucidBasePlugin):

    def summary(self):
        """
        Übersicht
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Übersicht")

        self.page_msg(u"Übersicht")

    def customers(self):
        """
        Kunden
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Kunden")

        self.page_msg(u"Kunden")

    def bills(self):
        """
        Rechnungen
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Rechnungen")

        self.page_msg(u"Rechnungen")

    def create_bill(self):
        """
        Rechnung erstellen
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Rechnung erstellen")

        self.page_msg(u"Rechnung erstellen")



        if self.request.method == 'POST':
            self.page_msg(self.request.POST)
            form = CreateBillForm(self.request.POST)
#            if form.is_valid():
#                # Do form processing here...
#                return HttpResponseRedirect('/url/on_success/')
        else:
            form = CreateBillForm()

        self.response.write(form.as_p())

















