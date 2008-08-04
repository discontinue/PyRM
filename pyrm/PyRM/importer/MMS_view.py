# -*- coding: utf-8 -*-

import sys, os, csv, re
from datetime import datetime
from pprint import pprint

from django.http import HttpResponse
from django.conf import settings

from PyRM.models import Konto, MWST#Firma, Person, Kunde, Ort

from utils.csv_utils import get_csv_tables, get_dictlist

CSV_DATEI = "./_daten/TRANSFER.CSV"


PROZ_RE = re.compile(r"(\d+?)\%")

def transfer_konten():
    Konto.objects.all().delete()

    buchungen, konten = get_csv_tables(CSV_DATEI)

    exist_mwst = tuple([i[0] for i in MWST])

    dictlist = get_dictlist(konten, used_fieldnames=None)
    for line in dictlist:
        print "_"*79
#        if line["ID.1"]=="" or line["Vorname"]=="sonstiges":
#            continue
        for k,v in line.iteritems():
            if v:
                print k, v

        konto_name = line['Listenname']

        mwst = None
        try:
            mwst_string = PROZ_RE.findall(konto_name)[0]
        except IndexError:
            pass
        else:
            mwst = int(mwst_string)
            if mwst in exist_mwst:
                print "MwSt: %s%%" % mwst

        konto = Konto(
            datev_nummer = line['Konto'],
            name = konto_name,
            #kontoart =
            mwst = mwst,
        )
        konto.save()

        print "-"*80



def transfer_buchungen():
#    Konto.objects.all().delete()

    buchungen, konten = get_csv_tables(CSV_DATEI)

    exist_mwst = tuple([i[0] for i in MWST])

    dictlist = get_dictlist(buchungen, used_fieldnames=None)
    for line in dictlist:
        print "_"*79
        pprint(line)

        date_string = line["Datum"]
        print "date_string:", date_string
        datum = datetime.strptime(date_string, "%d.%m.%Y")
        print "datum:", datum

        konto_nr = int(line["Konto"])
        print "konto_nr:", konto_nr, type(konto_nr)
#        try:
        konto = Konto.objects.get(datev_nummer = konto_nr)
#        except Konto.DoesNotExist, err:
#            print "*"*79
#            print "Konto unbekannt:", err
#        else:
        print "Konto:", konto

        Gkonto_nr = int(line["GGKto"])
        try:
            gkonto = Konto.objects.get(datev_nummer = Gkonto_nr)
        except Konto.DoesNotExist, err:
            print "*"*79
            print "Konto unbekannt:", err
        else:
            print "Konto:", konto

        print "-"*80

#______________________________________________________________________________

views = {
    "MSS_transfer_konten": transfer_konten,
    "MSS_transfer_buchungen": transfer_buchungen,
}
def menu(request):
    response = HttpResponse()
    for view in views.keys():
        response.write('<a href="%s/">%s</a><br />' % (view, view))

    return response

def import_csv(request, unit=""):
    response = HttpResponse(mimetype='text/plain')

    if unit not in views:
        response.write("Wrong URL!")
    else:
        old_stdout = sys.stdout
        sys.stdout = response
        views[unit]()
        sys.stdout = old_stdout

    return response