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

# Python
import posixpath, re, datetime

# django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django import forms
from django.db import transaction
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

# PyLucid
from PyLucid.tools.utils import escape
from PyLucid.system.BasePlugin import PyLucidBasePlugin

# PyRM
from PyRM.models import Konto, Kunde, RechnungsPosition, Rechnung

# PyRM plugin
from PyLucid.plugins_external.PyRM_plugin.forms import CreateBillForm

if "PyRM" not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("PyRM is not in settings.INSTALLED_APPS!")

## Datumsformat bei Rechnungserstellung
#DATE_FORMAT = _(u"%d.%m.%Y")
#
## Anzahl der Rechnungen in der Übersicht
DISPLAY_BILL_LIMIT = 5
#
#PARSE_ERROR = "Kann Rechnungspositionen nicht parsen! Fehler in Zeile '%s': %s"
#RE_TR = re.compile(r".*?<tr>(.*?)</tr>.*?(?isx)")
#RE_TD = re.compile(r".*?<td>(.*?)</td>.*?(?isx)")


class PyRM_plugin(PyLucidBasePlugin):

#    def install(self):
#        """
#        Erstellt die nötigen Seite in PyLucid.
#
#        Macht eigentlich auch PyRM_PyLucid_setup.py !!!
#        """
#        from PyLucid.models import Page
#
#        # Default Einstellungen für alle Seiten
#        defaults = {
#            "template"      : self.current_page.template,
#            "style"         : self.current_page.style,
#            "markup"        : 0, # html
#            "createby"      : self.request.user,
#            "lastupdateby"  : self.request.user,
#        }
#
#        PyRM_root_page, _ = Page.objects.get_or_create(
#            name    = "PyRM",
#            content = "{% lucidTag PyRM_plugin.summary %}",
#            parent  = None, # Root
#            ** defaults
#        )
#        PyRM_root_page.save()
#
#        page_infos = (
#            ("Rechnung erstellen", "create_bill"),
#            ("Rechnungs Übersicht", "bills"),
#            ("Kunden", "customers"),
#        )
#
#        for page_name, method_name in page_infos:
#            page, _ = Page.objects.get_or_create(
#                name    = page_name,
#                content = "{%% lucidTag PyRM_plugin.%s %%}" % method_name,
#                parent  = PyRM_root_page,
#                ** defaults
#            )
#            page.save()
#
#        self.page_msg("Alle PyRM Seiten erstellt.")
#
#        # refresh_curent_page
#        self.current_page.id = PyRM_root_page.id
#        self.current_page = self.context["PAGE"] = PyRM_root_page


    def summary(self):
        """
        Übersicht
        """
        # Change the global page title:
        self.context["PAGE"].title = _(u"PyRM - Übersicht")
#        raise SyntaxError("TEST")
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
                    self.page_msg(repr(form_data["positionen"]))
                else:
                    return self._save_new_bill(form_data)
        else:
            form = CreateBillForm()

        context["form"] = form

        self._add_tiny_mce(js_filename="create_bill_tinymce")

        self._render_template("create_bill", context)#, debug=True)

    def _add_tiny_mce(self, js_filename):
        """
        Activate TinyMCE and load the init js script (js_filename), too.
        """
        # url to e.g. /media/PyLucid/tiny_mce/tiny_mce.js
        tiny_mce_url = posixpath.join(
            self.URLs["PyLucid_media_url"], "tiny_mce", "tiny_mce.js"
        )
        # url to e.g. .../internal_page/PyRM_plugin/js_filename.js
        use_tiny_mce_url = self.internal_page.get_url(
            js_filename, slug="js"
        )
        # Add external media files
        for url in (tiny_mce_url, use_tiny_mce_url):
            # Add tiny_mce.js to
            self.context["js_data"].append({
                "plugin_name": self.plugin_name,
                "url": url,
            })















