# -*- coding: utf-8 -*-

import sys, os, csv
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

from PyRM.models import Firma, Person, Kunde, Ort
from PyRM.importer.menu import _sub_menu, _start_view

from utils.csv_utils import get_dictlist

KUNDENLISTE = "./_daten/20080729 KRB Kundenliste.csv"


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


    f = file(KUNDENLISTE, "r")
    data = f.readlines()
    f.close()

    dictlist = get_dictlist(data, used_fieldnames=None)
    for line in dictlist:
        if line["ID.1"]=="" or line["Vorname"]=="sonstiges":
            continue
        pprint(line)

        kundennummer = int(line["ID.1"])

        person, firma = get_kunden_obj(line)

        if line['N.'] == "j":
            anzeigen = True
        else:
            anzeigen = False

        kunde = Kunde(
            nummer = kundennummer,
            person = person,
            firma = firma,
            anzeigen = anzeigen,
        )
        kunde.save()

        print "-"*80

#------------------------------------------------------------------------------

views = {
    "kundenliste": kundenliste,
}
@login_required
def menu(request):
    return _sub_menu(request, views.keys())

@login_required
def start_view(request, unit=""):
    return _start_view(request, views, unit)