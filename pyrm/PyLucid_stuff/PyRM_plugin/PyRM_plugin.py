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

import re, datetime

from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.newforms.util import ValidationError
from django import newforms as forms
from django.db import transaction

from PyLucid.system.BasePlugin import PyLucidBasePlugin

from PyRM.models import Konto, Kunde, RechnungsPosition, Rechnung

# Datumsformat bei Rechnungserstellung
DATE_FORMAT = _(u"%d.%m.%Y")

# Anzahl der Rechnungen in der Übersicht
DISPLAY_BILL_LIMIT = 5


POSITION_RE = re.compile(
    r"""
        ^          # Anfang jeder neuen Zeile
        (\d+?)     # Positions Anzahl
        [ x]+      # Leerzeichen und "x" (optional)
        (.*?)      # Positions Text
        [ a]+      # Leerzeichen und "a" (optional)
        (\d+?)     # Positions Preis
        [^\d]{0,2} # Ein bis zwei nicht Zahlen (z.B. '€')
        $          # Zeilenende
        (?x)
    """
)
PARSE_ERROR = "Kann Rechnungspositionen nicht parsen! Fehler in Zeile '%s': %s"

class PositionenField(forms.CharField):
#    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
#        self.max_length, self.min_length = max_length, min_length
#        super(CharField, self).__init__(*args, **kwargs)
    def clean(self, value):
        # Validates max_length and min_length
        value = super(PositionenField, self).clean(value)

        value = value.replace("\r\n", "\n").replace("\r", "\n")
        value = value.strip()
        result = []
        for line in value.splitlines():
            matches = POSITION_RE.findall(line)
            if matches == []:
                raise ValidationError(PARSE_ERROR % (line, "RE empty"))

            try:
                anzahl, txt, preis = matches[0]
            except ValueError, e:
                raise ValidationError(PARSE_ERROR % (line, e))

            try:
                anzahl = int(anzahl)
                preis = int(preis)
            except TypeError, e:
                raise ValidationError(PARSE_ERROR % (line, e))

            result.append((anzahl, txt, preis,))

        return result


class CreateBillForm(forms.Form):
    """
    Form for creating a bill.
    http://www.djangoproject.com/documentation/newforms/
    """
    bestellnummer = forms.IntegerField(required=False)
    datum = forms.DateField(
        initial=datetime.date.today().strftime(smart_str(DATE_FORMAT)),
        input_formats=[DATE_FORMAT]
    )

    kunde = forms.ModelChoiceField(Konto.objects.all(), required=False)
    ggkto = forms.ModelChoiceField(Konto.objects.all(), required=False)

    lieferdatum = forms.DateField(input_formats=DATE_FORMAT, required=False)

#    anzahl = forms.IntegerField()
#    beschreibung = forms.CharField()
#    einzelpreis = forms.IntegerField()
    positionen = PositionenField(
        min_length = 10,
        widget=forms.Textarea(attrs={'rows': '10'}),
        initial=(
            "1x BeispielPosition eins a 5€\n"
            "2x Noch eine Position a 10€\n"
            "4x die letzte Position a 20€\n"
        ),
        help_text=_("Die eizelnen Rechnungspositionen"),
    )


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

    #__________________________________________________________________________
    # VIEW BILL

    def bills(self):
        """
        Rechnungs Übersicht
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Rechnungen")

        bills = Rechnung.objects.all()[:DISPLAY_BILL_LIMIT]
        for bill in bills:
            bill.link = self.URLs.methodLink("bill_detail", bill.id)

        context = {
            "bills": bills,
            "count": Rechnung.objects.count(),
            "limit": DISPLAY_BILL_LIMIT,
        }
        self._render_template("bill_summary", context)#, debug=True)

    def bill_detail(self, id):
        """
        Rechnungsdetails ausgeben
        """
        try:
            id = id.strip("/")
            id = int(id)
            bill = Rechnung.objects.get(id = id)
        except Exception, e:
            self.page_msg.red("Error:", e)
            return

        # Alle Positionen der Rechnung ermitteln, mit summen Attribut
        positionen = bill.positionen.all_with_summ()

        context = {
            "bill": bill,
            "positionen": positionen,
        }
        self._render_template("bill_detail", context)#, debug=True)

    #__________________________________________________________________________
    # CREATE BILL

    @transaction.commit_manually
    def _save_new_bill(self, form_data):
        self.page_msg(form_data)
        try:
            rechnung = Rechnung.objects.create(form_data)
            rechnung.save()
            self.page_msg.green("Rechnung '%s' erstellt." % rechnung.id)

            RechnungsPosition.objects.create_all(
                form_data["positionen"], rechnung
            )
            self.page_msg.green("Rechnungs Positionen erstellt.")
        except Exception, e:
            self.page_msg.red("Fehler:", e)
            transaction.rollback()
        else:
            transaction.commit()

        return self.bills()


    def create_bill(self):
        """
        Rechnung erstellen
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Rechnung erstellen")

        context = {}

        if self.request.method == 'POST':
            #self.page_msg(self.request.POST)
            form = CreateBillForm(self.request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                if "preview" in self.request.POST:
                    context["preview"] = form_data["positionen"]
                else:
                    return self._save_new_bill(form_data)
        else:
            form = CreateBillForm()

        context["form"] = form
        self._render_template("create_bill", context)#, debug=True)

















