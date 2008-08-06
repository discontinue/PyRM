# -*- coding: utf-8 -*-

import sys, os, csv, re
import codecs
from datetime import datetime
from pprint import pprint
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

from PyRM.importer.menu import _sub_menu, _start_view
from PyRM.models import Firma, Person, Kunde, Lieferant, Ort, Konto, \
            AusgangsRechnung, AusgangsPosten, EingangsRechnung, EingangsPosten

from utils.csv_utils import get_dictlist

KUNDENLISTE = "./_daten/20080729 KRB Kundenliste.csv"
BUCHUNGEN = "./_daten/20080805 KRB Buchungen.csv"


def _get_dictlist(filename):
    f = file(filename, "r")
    data = f.readlines()
    f.close()

    dictlist = get_dictlist(data, used_fieldnames=None)
    return dictlist


def get_kunden_obj(line):
    if line['spezielle Adresszeile']:
        daten = line['spezielle Adresszeile'].split("\n")
        print "*"*79
        for no,l in enumerate(daten):
            print no, l
        plz, ort_name = daten[4].split(" ", 1)
        print "*"*79
        ort = Ort(name=ort_name, land="Frankreich")
        ort.save()
        firma = Firma(
            name1 = daten[0],
            strasse = daten[2],
            strassen_zusatz = daten[3],
            plz = int(plz),
            ort = ort,
        )
        firma.save()
        person = Person(
            vorname="Thorsten",
            nachname="Beitzel",
            geschlecht="M",
        )
        person.save()
        return person, firma

    orts_name = line["Ort"]
    if orts_name:
        ort, created = Ort.objects.get_or_create(name = orts_name)
    else:
        ort = None

    try:
        person = Person.objects.get(
            vorname = line["Vorname"],
            nachname = line["Name"],
        )
    except Person.DoesNotExist:
        plz = line.get("PLZ")
        if plz == "":
            plz = None

        person = Person(
            vorname = line["Vorname"],
            nachname = line["Name"],
            geschlecht = line["G."],

            strasse = line["Strasse"],
            plz = plz,
            ort = ort,

            email = line["Email"],
            telefon = line["Telefon"],
            #mobile =
        )
        person.save()

    if line["Firma"] != "":
        firma, created = Firma.objects.get_or_create(name1 = line["Firma"])
        firma.save()
    else:
        firma = None

    return person, firma


def kundenliste():
    Ort.objects.all().delete()
    Person.objects.all().delete()
    Firma.objects.all().delete()
    Kunde.objects.all().delete()

    for line in _get_dictlist(KUNDENLISTE):
        print "_"*80
        if line["ID.1"]=="" or line["Vorname"]=="sonstiges":
            print line
            continue
        pprint(line)
        print " -"*40

        kundennummer = int(line["ID.1"])

        person, firma = get_kunden_obj(line)

        if line['N.'] == "j":
            anzeigen = True
        else:
            anzeigen = False

        kwargs = {
            "nummer": kundennummer,
            "person": person,
            "firma": firma,
            "anzeigen": anzeigen,
        }
#        print repr(kwargs)
        try:
            kunde = Kunde(**kwargs)
            kunde.save()
        except Exception, err:
            print "Fehler:", err

#------------------------------------------------------------------------------

KONTO_MAP = {
    135 : 27,   # EDV-Software
    650 : 420,  # Büroeinrichtung
    4200: 1200, # Erlöse Steuerfrei -> Bankkonto
    4400: 8400, # Einnahmen 16%
    4401: 8400, # Einnahmen 16%
    5400: 3400, # Wareneingang
    6430: 1800, # Handy
    6470: 4805, # Reperatur
    6600: 4610, # Werbekosten
    6800: 4910, # Porto
    6815: 4930, # Bürobedarf
}

def _get_decimal(raw_summe):
    summe1 = raw_summe.replace(".", "") # tausender punkte?
    summe2 = summe1.replace(",", ".")
    summe = Decimal(summe2)
    return summe


def _get_datum(raw_datum):
    if raw_datum != "":
        return datetime.strptime(raw_datum, "%d.%m.%y")


RE_TEXT_REXP = re.compile(r"^(\d+)[x ]+(.*?)[a ]+([\d,]+)$")
def _get_re_posten(raw_text, summe):
    text_lines = raw_text.strip().splitlines()
    result = []
    test_summe = Decimal(0)
    for text_line in text_lines:
        posten = RE_TEXT_REXP.findall(text_line.strip())
        if posten == []:
            return [(1, raw_text, summe)]

        assert len(posten) == 1
        posten = posten[0]

        raw_anzahl, txt, raw_preis = posten
        anzahl = int(raw_anzahl)
        preis = _get_decimal(raw_preis)

        result.append((anzahl, txt, preis))
        test_summe += (anzahl * preis)

    assert test_summe == summe
    return result


def buchungen():
    AusgangsRechnung.objects.all().delete()
    AusgangsPosten.objects.all().delete()

    EingangsRechnung.objects.all().delete()
    EingangsPosten.objects.all().delete()

    Lieferant.objects.all().delete()


    for line in _get_dictlist(BUCHUNGEN):
        notiz = ""
        raw_summe = line["Wert"]

        print "_"*80
        pprint(line)
        if raw_summe == "" or line["Rechnungstext"].startswith("^^^"):
            print " *** SKIP *** "
            continue
        print " -"*40

        #----------------------------------------------------------------------

        raw_summe = raw_summe.split(" ")[0]
        summe = _get_decimal(raw_summe)
        print "Betrag:", summe

        #----------------------------------------------------------------------

        kunden_nummer1 = line["K.Nr."]
        if kunden_nummer1 == "" or kunden_nummer1 == "999":
            # Kein kunde eingetragen
            kunde = None
        else:
            kunden_nummer2 = int(kunden_nummer1)
            kunde = Kunde.objects.get(nummer = kunden_nummer2)
        print "Kunde:", kunde

        #----------------------------------------------------------------------

        datum = _get_datum(raw_datum = line["R.Datum"])
        raw_valute_datum = line["gezahlt\nEingang"]
        try:
            valuta = _get_datum(raw_datum = raw_valute_datum)
        except ValueError, err:
            print "ValueError:", err
            notiz += raw_valute_datum

        #----------------------------------------------------------------------

        re_posten = _get_re_posten(line["Rechnungstext"], summe)
        print "RE.Posten:"
        if len(re_posten)>1:
            print " *"*40
        pprint(re_posten)

        #----------------------------------------------------------------------

        raw_datev_nr = line["Art"]
        if raw_datev_nr == "":
            konto = None
        else:
            datev_nr = int(raw_datev_nr)
            if datev_nr in KONTO_MAP:
                datev_nr = KONTO_MAP[datev_nr]
            konto = Konto.objects.get(datev_nummer = datev_nr)
        print "Konto:", konto

        #----------------------------------------------------------------------

        raw_nr = line["R.Nr."]
        if raw_nr == "":
            re_nr = None
        else:
            re_nr = int(raw_nr)

        #----------------------------------------------------------------------

        if summe<0:
            print "Ausgabe - Eingangsrechnung"
            print "*"*79
            if kunde:
                # Kunde als Lieferant eintragen
                lieferant, created = Lieferant.objects.get_or_create(
                    person = kunde.person,
                    firma = kunde.firma,
                )
                lieferant.save()
            else:
                lieferant = None

            rechnung = EingangsRechnung(
                nummer = re_nr,
                lieferant = lieferant,
                datum = datum,
                valuta = valuta,
                konto = konto,
                summe = summe,
            )
            rechnung.save()
            PostenModel = EingangsPosten
        else:
            print "Einnahme - Ausgangsrechnung"
            rechnung = AusgangsRechnung(
                nummer = re_nr,
                kunde = kunde,
                datum = datum,
                valuta = valuta,
                konto = konto,
                summe = summe,
            )
            rechnung.save()
            PostenModel = AusgangsPosten


        for anzahl, txt, preis in re_posten:
            PostenModel(
                anzahl = anzahl,
                beschreibung = txt,
                einzelpreis = preis,
                rechnung = rechnung
            ).save()

#------------------------------------------------------------------------------

views = {
    "kundenliste": kundenliste,
    "buchungen": buchungen,
}
@login_required
def menu(request):
    return _sub_menu(request, views.keys())

@login_required
def start_view(request, unit=""):
    return _start_view(request, views, unit)