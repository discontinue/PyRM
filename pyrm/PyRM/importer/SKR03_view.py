# -*- coding: utf-8 -*-
"""
    PyRM - SKR03 import
    ~~~~~~~~~~~~~~~~~~~

    Importiert die SKR03 Konten.
    Nutzt die Daten aus der GnuCash Datei "acctchrt_skr03.gnucash-xea":
        GnuCash is freely licensed under the GNU GPL
        http://gnucash.org

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys, re, os, socket, urllib2
from xml.etree import ElementTree as ET
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

from PyRM.models import Konto, MWST, GNUCASH_SKR03_MAP#Firma, Person, Kunde, Ort
from PyRM.importer.menu import _sub_menu, _start_view

SKR_URL = (
    "http://svn.gnucash.org/"
    "trac/browser/gnucash/trunk/accounts/de_DE/"
    "acctchrt_skr03.gnucash-xea?format=raw"
)
SKR_DATEI = "./_daten/acctchrt_skr03.gnucash-xea"
EXIST_MWST = tuple([i[0] for i in MWST])
PROZ_RE = re.compile(r"(\d+?)\%")


def import_skr03():
    print "SKR Datei:", SKR_DATEI

    if not os.path.isfile(SKR_DATEI):
        # SKR Datei ist nicht da -> Aus dem Netz saugen
        path = os.path.split(SKR_DATEI)[0]
        if not os.path.isdir(path):
            os.makedirs(path)

        socket.setdefaulttimeout(5) # set a timeout
        response = urllib2.urlopen(SKR_URL)
        f = file(SKR_DATEI, "w")
        content = response.read()
        f.write(content)
        response.close()
        f.close()
        print "Saved a new SRK file, response from svn.gnucash.org"

    f = file(SKR_DATEI, "r")
    etree = ET.parse(f)
    f.close()
    root = etree.getroot()
#    root = ET.Element("gnc")
#    print root, len(root)


    Konto.objects.all().delete()
    pprint(GNUCASH_SKR03_MAP)


#    for item in root.findall("account"):
    for node in root:
        print "_"*79
        if not node.tag.endswith("account"):
            continue

        data = {}
        for item in node:
            key = item.tag.split("}")[1]
            data[key] = item.text.strip()

        if not "code" in data:
            # Kein datevkonto
            continue

        datev_nr = data["code"]
        raw_name = data["name"]
        konto_name = raw_name.replace(datev_nr, "").strip()

        raw_kontoart = data["type"]
        if raw_kontoart == "ROOT": # Root Account
            continue

        pprint(data)
        print "-"*79

        kontoart = GNUCASH_SKR03_MAP[raw_kontoart]

        print "konto_name:", konto_name
        print "datev_nr:", datev_nr
        print "kontoart:", kontoart

        mwst = None
        try:
            mwst_string = PROZ_RE.findall(konto_name)[0]
        except IndexError:
            pass
        else:
            mwst = int(mwst_string)
            assert(mwst in EXIST_MWST)
            print "MwSt: %s%%" % mwst

        konto = Konto(
            datev_nummer = datev_nr,
            name = konto_name,
            kontoart = kontoart,
            mwst = mwst,
        )
        konto.save()

    print " - END - "

#------------------------------------------------------------------------------

views = {
    "import_skr03": import_skr03,
}

@login_required
def menu(request):
    return _sub_menu(request, views.keys())

@login_required
def start_view(request, unit=""):
    return _start_view(request, views, unit)