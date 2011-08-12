# coding: utf-8

import os
from datetime import datetime
import pprint

from django.core.management.base import BaseCommand, CommandError

import reversion # django-reversion

from pyrm.models import Firma, Person, Kunde, Ort
from pyrm.utils.csv_utils import get_dictlist
from pyrm.models.stammdaten import Lieferant





def _get_dictlist(filename):
    # python csv module doesn't work with unicode! So no codecs.open() here!
    f = file(filename, "rb")
    data = f.readlines()
    f.close()

    dictlist = get_dictlist(data, encoding="latin-1", used_fieldnames=None)
    return dictlist






class Command(BaseCommand):
    help = 'Import KRB Lieferanten.'
    args = "/path/to/KRB_lieferanten.csv"

    @reversion.revision.create_on_success
    def handle(self, filepath, **options):
        if not os.path.isfile(filepath):
            raise CommandError("Filepath %r doesn't exist." % filepath)

        self.verbosity = int(options.get('verbosity', 1))

#        Ort.objects.all().delete()
#        Person.objects.all().delete()
#        Firma.objects.all().delete()
#        Lieferant.objects.all().delete()

        for line in _get_dictlist(filepath):
            if self.verbosity >= 3:
                self.stdout.write("_" * 80)
                self.stdout.write("\n")

            if line["name"] in ("", "sonstiges"):
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

            if line["nr"]:
                nummer = int(line["nr"])
            else:
                nummer = None

            lieferant, created = Lieferant.objects.get_or_create(nummer=nummer)
            if created:
                self.stdout.write("Neuer Lieferant wird erstellt: %s\n" % lieferant)
            else:
                self.stdout.write("Lieferant schon vorhanden: %s\n" % lieferant)
                continue

            orts_name = line["Ort"]
            if orts_name:
                ort, created = Ort.objects.get_or_create(name=orts_name)
                if created and self.verbosity >= 3:
                    self.stdout.write("Ort erstellt: %s\n" % ort)
                elif self.verbosity >= 3:
                    self.stdout.write("Vorhanden Ort genutzt: %s\n" % ort)
            else:
                ort = None

            if line["PLZ"]:
                plz = int(line["PLZ"])
            else:
                plz = None

            firma, created = Firma.objects.get_or_create(
                name1=line["name"],
                defaults={
                    "strasse": line["Strasse"],
                    "plz": plz,
                    "ort": ort,
                }
            )
            if created:
                self.stdout.write("neue Firma erstellt: %s\n" % firma)
            else:
                self.stdout.write("Vorhandene Firma genutzt: %s\n" % firma)
            firma.save()
            reversion.revision.comment = "KRB lieferanten import"

            info = []
            for i in range(2):
                key = "info%i" % (i + 1)
                if line[key]:
                    info.append(line[key])
            info = "\n".join(info)
            if info:
                lieferant.notizen = info

            lieferant.firma = firma
            lieferant.save()
            reversion.revision.comment = "KRB lieferanten import"
