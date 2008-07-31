# -*- coding: utf-8 -*-

import sys, os, csv
from pprint import pprint

from django.http import HttpResponse
from django.conf import settings

from PyRM.models import Firma, Person, Kunde, Ort

import MySQLdb
db = MySQLdb.Connect(
    #db='cao datenbank',
    db=settings.DATABASE_NAME,
    user=settings.DATABASE_USER,
    passwd=settings.DATABASE_PASSWORD,
)
cursor = MySQLdb.cursors.DictCursor(db)

def kundenliste():
    Ort.objects.all().delete()
    Person.objects.all().delete()
    Firma.objects.all().delete()
    Kunde.objects.all().delete()

    cursor.execute("SELECT * FROM django_content_type;")
    for line in cursor:
        print line

#        if orts_name:
#            ort, created = Ort.objects.get_or_create(name = orts_name)
#        else:
#            ort = None
#
#        person = Person(
#            vorname = line["Vorname"],
#            nachname = line["Name"],
#            geschlecht = line["G."],
#
#            strasse = line["Strasse"],
#            plz = plz,
#            ort = ort,
#
#            email = line["Email"],
#            telefon = line["Telefon"],
#            #mobile =
#        )
#        person.save()

#        kunde = Kunde(
#            id = kundennummer,
#            person = person,
#            firma = firma,
#            anzeigen = anzeigen,
#        )
#        kunde.save()

        print "-"*80

#------------------------------------------------------------------------------

views = {
    "kundenliste": kundenliste,
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