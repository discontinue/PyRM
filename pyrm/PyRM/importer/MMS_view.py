# -*- coding: utf-8 -*-

import sys, os, csv, re
from pprint import pprint
from decimal import Decimal
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.conf import settings

from PyRM.models import Konto, MWST, StSl, \
            AusgangsRechnung, AusgangsPosten, EingangsRechnung, EingangsPosten,\
            Firma, Person, Kunde, Ort
from PyRM.importer.menu import _sub_menu, _start_view
from PyRM.utils.csv_utils import get_csv_tables, get_dictlist

from modelvcs.messages import add_message


CSV_DATEI = "./_daten/TRANSFER.CSV"
#CSV_DATEI = "./_daten/Beispielmandant TRANSFER.CSV"


PROZ_RE = re.compile(r"(\d+?)\%")

def _get_decimal(raw_summe):
    summe1 = raw_summe.replace(".", "") # tausender punkte?
    summe2 = summe1.replace(",", ".")
    summe = Decimal(summe2)
    return summe


def transfer_konten():
#    Konto.objects.all().delete()

    buchungen, konten = get_csv_tables(CSV_DATEI)

    exist_mwst = tuple([i[0] for i in MWST])

    dictlist = get_dictlist(konten, used_fieldnames=None)
    for line in dictlist:
#        pprint(line)
        datev_nummer = int(line['Konto'])
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

        try:
            konto = Konto.objects.get(datev_nummer = datev_nummer)
        except Konto.DoesNotExist:
            konto = Konto(
                datev_nummer = datev_nummer,
                name = konto_name,
                mwst = mwst,
            )
            add_message(konto, "Neues Konto aus MMS import")
            konto.save()
            print "Neues Konto erstellt:", konto
        else:
            print "Konto besteht schon:", konto
            must_save=False

            if konto_name != konto.name:
                print " *** andere Bezeichnung:"
                print konto_name, "!=", konto.name
                print "Setzte neuen Namen"
                konto.name = konto_name
                add_message(konto, "Neuer Konto Namen aus MMS import")
                konto.notizen += "\n neuer Konto namen aus MMS import"
                must_save=True

            if mwst != konto.mwst:
                print " *** andere MwSt.:"
                print mwst, "!=", konto.mwst
                print "setzte neue MwSt:"
                konto.mwst = mwst
                add_message(konto, "Neue MwSt.Satz aus MMS import")
                konto.notizen += "\n neue MwSt.Satz aus MMS import"
                must_save=True

            if must_save:
                konto.save()

        print "-"*80

RECHNUNG_RE = re.compile(r"^(\d{3})-(\d{3,4})$")

def transfer_buchungen():
#    Konto.objects.all().delete()

    buchungen, konten = get_csv_tables(CSV_DATEI)

    exist_mwst = tuple([i[0] for i in MWST])

    dictlist = get_dictlist(buchungen, used_fieldnames=None)
    for line in dictlist:
        kommentar = line["Kommentar"]
        print "_"*79
        pprint(line)
        print " -"*40

        date_string = line["Datum"]
        print "date_string:", date_string
        datum = datetime.strptime(date_string, "%d.%m.%Y")
        print "datum:", datum

        raw_summe = line["Betrag"]
        summe = _get_decimal(raw_summe)
        print "summe:", summe

        konto_nr = int(line["Konto"])
        print "konto_nr:", konto_nr, type(konto_nr)
        try:
            konto = Konto.objects.get(datev_nummer = konto_nr)
        except Konto.DoesNotExist, err:
            print "*"*79
            print "Konto unbekannt:", err
            print "Erstelle neuen Eintrag!"

        else:
            print "Konto:", konto

        gkonto = line["GGKto"]
        if len(gkonto) > 4:
            # SteuerSchlüssel drin
            stsl_nr = int(gkonto[0])
            stsl = StSl.objects.get(id = stsl_nr)
            print u"Steuerschlüssel:", stsl
            gkonto = gkonto[1:]

        Gkonto_nr = int(gkonto)
        try:
            gkonto = Konto.objects.get(datev_nummer = Gkonto_nr)
        except Konto.DoesNotExist, err:
            print "*"*79
            print "GKonto unbekannt:", err
        else:
            print "GKonto:", konto

        print " -"*40

        if summe<0:
            print "Ausgabe - Eingangsrechnung"
            RechnungModel = EingangsRechnung
        else:
            print "Einnahme - Ausgangsrechnung"
            RechnungModel = AusgangsRechnung

        kunde = None
        rechnung = None

        if "-" in kommentar:
            print "*********", kommentar
            try:
                matches = RECHNUNG_RE.findall(kommentar)[0]
                raw_kunden_nr, raw_re_nr = matches
                kunden_nr = int(raw_kunden_nr)
                re_nr = int(raw_re_nr)
            except (IndexError, ValueError), err:
                print "nein:", err
            else:
                # Kunden nummer + Rechnungsnimmer in Kommentar
#                print kunden_nr, re_nr
                kunde = Kunde.objects.get(nummer = kunden_nr)
                try:
                    rechnung = AusgangsRechnung.objects.get(nummer=re_nr)
                except AusgangsRechnung.DoesNotExist, err:
                    print "FEHLER: Rechnung %s nicht gefunden: %s" % (
                        re_nr, err
                    )
                    continue

        else:
            try:
                rechnungen = RechnungModel.objects.all().filter(summe = summe)
            except RechnungModel.DoesNotExist:
                pass
            else:
                if len(rechnungen) == 0:
                    rechnung = None
                elif len(rechnungen) == 1:
                    rechnung = rechnungen[0]
                else:
                    print "mehrere Rechnungen gefunden:"
                    print len(rechnungen)
                    for rechnung in rechnungen:
                        print "rechnung:", rechnung.pk, unicode(rechnung)
                    continue

        if kunde:
            print "kunde:", kunde.pk, unicode(kunde)
        if rechnung:
            print "rechnung:", rechnung.pk, unicode(rechnung)



#------------------------------------------------------------------------------

views = {
    "MSS_transfer_konten": transfer_konten,
    "MSS_transfer_buchungen": transfer_buchungen,
}

@login_required
def menu(request):
    return _sub_menu(request, views.keys())

@login_required
def start_view(request, unit=""):
    return _start_view(request, views, unit)
