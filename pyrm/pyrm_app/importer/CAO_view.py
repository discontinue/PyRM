# -*- coding: utf-8 -*-

import sys, os, csv
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings

from pyrm_app.models import Firma, Person, Kunde, Ort
from pyrm_app.importer.menu import _sub_menu, _start_view


def _get_faktura_db_cursor():
    import MySQLdb
    db = MySQLdb.Connect(
        db='faktura',
        #db=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        passwd=settings.DATABASE_PASSWORD,
    )
    db.set_character_set('utf8')
    cursor = MySQLdb.cursors.DictCursor(db)
    return cursor


ORTE = {}

def kundenliste():
    try:
        cursor = _get_faktura_db_cursor()
    except Exception, err:
        print "ERROR: Can't connect to CAO database:", err
        return

    Ort.objects.all().delete()
    Person.objects.all().delete()
    Firma.objects.all().delete()
    Kunde.objects.all().delete()

    cursor.execute("SELECT * FROM ADRESSEN;")
    for line in cursor:
        print "_"*80

        orts_name = line["ORT"]
        if orts_name:
            orts_name = orts_name.decode("utf8")
            #print repr(orts_name), type(orts_name)
            orts_name = orts_name.strip()
            if orts_name in ORTE:
                # Doppelt bug
                ort = ORTE[orts_name]
            else:
                try:
                    ort = Ort.objects.get(name=orts_name)
                    #print "Existier schon:", ort
                except Ort.DoesNotExist:
                    ort = Ort(name=orts_name)
                    ort.save()
                    ORTE[orts_name] = ort
        else:
            ort = None

        gruppe = line['KUNDENGRUPPE']
        # 1 - person
        # 2 - firma
        # 999 - lieferrant

        abteilung = line['ABTEILUNG']
        nachname = line["NAME1"]
        anrede = line['ANREDE']

        if anrede == "Frau":
            geschlecht = "W"
        elif anrede == "Herr":
            geschlecht = "M"
        else:
            geschlecht = None

        if gruppe == 1: # person
            vorname = None
            if abteilung:
                #vorname = abteilung.replace(nachname, "")
                vorname = abteilung.split(" ", 1)[0]
#            print "vorname:", vorname
#            print "nachname:", nachname
#            print "g:", geschlecht

            person, created = Person.objects.get_or_create(
                vorname = vorname,
                nachname = nachname,
                geschlecht = geschlecht,

                #seid =

                strasse = line["STRASSE"],
                plz = int(line["PLZ"]),
                ort = ort,

                internet = line.get("INTERNET"),
                email = line.get("EMAIL"),
                telefon = line["TELE1"],
                fax = line.get("FAX"),
                mobile = line.get("FUNK"),
            )
            person.save()
            #print person
        elif gruppe == 2:
            pprint(line)
            firma = Firma(
                name1 = line["NAME1"],
                name2 = line["NAME2"],

                strasse = line["STRASSE"],
                plz = int(line["PLZ"]),
                ort = ort,

                internet = line.get("INTERNET"),
                email = line.get("EMAIL"),
                telefon = line["TELE1"],
                fax = line.get("FAX"),
                mobile = line.get("FUNK"),
            )
            firma.save()

        continue

        print "-"*79
        print "gruppe:", gruppe, type(gruppe)
        print n
        print line["NAME1"]
        print "-"*79

        continue



        kundennummer = int(line["KUNNUM1"])
#        kunde = Kunde(
#            id = kundennummer,
#            person = person,
#            firma = firma,
#            anzeigen = anzeigen,
#        )
#        kunde.save()



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