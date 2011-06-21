# coding: utf-8

import os
from datetime import datetime
import pprint

from django.core.management.base import BaseCommand, CommandError

import reversion # django-reversion

from pyrm.models import Firma, Person, Kunde, Ort
from pyrm.utils.csv_utils import get_dictlist





def _get_dictlist(filename):
    # python csv module doesn't work with unicode! So no codecs.open() here!
    f = file(filename, "rb")
    data = f.readlines()
    f.close()

    dictlist = get_dictlist(data, encoding="latin-1", used_fieldnames=None)
    return dictlist






class Command(BaseCommand):
    help = 'Import KRB Kundenliste.'
    args = "/path/to/KRB_kudenliste.csv"

    @reversion.revision.create_on_success
    def handle(self, filepath, **options):
        if not os.path.isfile(filepath):
            raise CommandError("Filepath %r doesn't exist." % filepath)

        self.verbosity = int(options.get('verbosity', 1))

        Ort.objects.all().delete()
        Person.objects.all().delete()
        Firma.objects.all().delete()
        Kunde.objects.all().delete()

        for line in _get_dictlist(filepath):
            if self.verbosity >= 3:
                self.stdout.write("_" * 80)
                self.stdout.write("\n")
            if line["ID.1"] == "" or line["Vorname"] == "sonstiges":
                self.stdout.write("SKIP:")
                if self.verbosity >= 3:
                    self.stdout.write(pprint.pformat(line))
                else:
                    self.stdout.write(repr(line))
                self.stdout.write("\n")
                continue

            if self.verbosity >= 3:
                self.stdout.write(pprint.pformat(line))
                self.stdout.write("\n")
                self.stdout.write(" -" * 40)
                self.stdout.write("\n")

            kundennummer = int(line["ID.1"])

            person, firma = self.get_kunden_obj(line)

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
    #        self.stdout.write(repr(kwargs)
            try:
                kunde = Kunde(**kwargs)
                kunde.save()
                reversion.revision.comment = "KRB import"
            except Exception, err:
                self.stdout.write("Fehler: %s\n" % err)

    def get_kunden_obj(self, line):
        if line['spezielle Adresszeile']:
            daten = line['spezielle Adresszeile'].split("\n")
            self.stdout.write("*" * 79)
            self.stdout.write("\n")

            for no, l in enumerate(daten):
                self.stdout.write("%s %s\n" % (no, l))

            plz, ort_name = daten[4].split(" ", 1)
            self.stdout.write("*" * 79)
            self.stdout.write("\n")
            ort = Ort(name=ort_name, land="Frankreich")
            ort.save()
            reversion.revision.comment = "KRB import"

            firma = Firma(
                name1=daten[0],
                strasse=daten[2],
                strassen_zusatz=daten[3],
                plz=int(plz),
                ort=ort,
            )
            firma.save()
            reversion.revision.comment = "KRB import"

            person = Person(
                vorname="Thorsten",
                nachname="Beitzel",
                geschlecht="M",
            )
            person.save()
            reversion.revision.comment = "KRB import"
            return person, firma

        orts_name = line["Ort"]
        if orts_name:
            ort, created = Ort.objects.get_or_create(name=orts_name)
            if created and self.verbosity >= 3:
                self.stdout.write("Ort erstellt: %s\n" % ort)
            elif self.verbosity >= 3:
                self.stdout.write("Vorhanden Ort genutzt: %s\n" % ort)
        else:
            ort = None

        try:
            person = Person.objects.get(
                vorname=line["Vorname"],
                nachname=line["Name"],
            )
        except Person.DoesNotExist:
            plz = line.get("PLZ")
            if plz == "":
                plz = None

            person = Person(
                vorname=line["Vorname"],
                nachname=line["Name"],
                geschlecht=line["G."],

                strasse=line["Strasse"],
                plz=plz,
                ort=ort,

                email=line["Email"],
                telefon=line["Telefon"],
                #mobile =
            )
    #        add_message(person, "KRB import")
            person.save()
            reversion.revision.comment = "KRB import"

        if line["Firma"] != "":
            firma, created = Firma.objects.get_or_create(
                name1=line["Firma"],
                defaults={
                    "name2": line["Volle Firmenbezeichnung"],
                    "internet": line["Homepage"],
                    "email": line["Email"],
                    "strasse": line["Strasse"],
                    "telefon": line["Telefon"],
                    "fax": line["Fax"],
                    #"strassen_zusatz"=daten[3],
                    "plz": int(line["PLZ"]),
                    "ort": ort,
                }
            )
            if created:
                self.stdout.write("neue Firma erstellt: %s\n" % firma)
            else:
                self.stdout.write("Vorhandene Firma genutzt: %s\n" % firma)
            firma.save()

            createtime = datetime.strptime(line["Eintritt"], "%d.%m.%y")
            firma.createtime = createtime
            firma.save()
        else:
            firma = None

        return person, firma
