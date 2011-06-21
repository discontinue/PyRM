# coding: utf-8

import os
import datetime
import pprint
import csv
from decimal import Decimal

if __name__ == "__main__":
    os.chdir(os.path.expanduser("~/servershare/PyRM/"))
    os.environ['DJANGO_SETTINGS_MODULE'] = "testproject.settings"
    virtualenv_file = os.path.expanduser("~/pyrm_env/bin/activate_this.py")
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core import management

import reversion # django-reversion

from pyrm.models.rechnung import Rechnung
from pyrm.utils.csv_utils import get_dictlist




def get_buchungen(filepath):
    f = file(filepath, "rb")

    data = []
    in_buchungen = False
    for line in f:
        if line.startswith('"Buchungstag";'):
            in_buchungen = True
            # Damit der Zahlungtyp nicht " " ist, sondern "art"
            data.append(
                '"Buchungstag";"Valuta";"Auftraggeber/Zahlungsempf\xe4nger";"Empf\xe4nger/Zahlungspflichtiger";"Konto-Nr.";"BLZ";"Vorgang/Verwendungszweck";"W\xe4hrung";"Umsatz";"art"\r\n'
            )
            continue

        if in_buchungen:
            data.append(line)

    f.close()
    return data


def to_datetime_date(raw_date):
    d = datetime.datetime.strptime(raw_date, "%d.%m.%Y")
    return d.date()


class Command(BaseCommand):
    help = 'Import Conbank Buchungen.'
    args = "/path/to/Umsaetze_xxxxxx_31.01.2011.csv"

    @reversion.revision.create_on_success
    def handle(self, filepath, **options):
        if not os.path.isfile(filepath):
            raise CommandError("Filepath %r doesn't exist." % filepath)

        self.stdout.write("Import Cronbank Buchungen von %r\n" % filepath)

        self.verbosity = int(options.get('verbosity', 1))

        buchungen = get_buchungen(filepath)
#        print buchungen

        for line in get_dictlist(buchungen):
            if line["art"] == u"H":
                if self.verbosity >= 3:
                    self.stdout.write(pprint.pformat(line))
                    self.stdout.write("\n")

                raw_valuta = line["Valuta"]
                if not raw_valuta:
                    self.stdout.write("Skip, kein valuta Datum vorhanden.\n")
                    continue

                valuta = to_datetime_date(raw_valuta)
                if self.verbosity >= 2:
                    self.stdout.write("Konvertiertes Valuta-Datum: %r\n" % valuta)

                raw_umsatz = line["Umsatz"].replace(".", "").replace(",", ".")
                umsatz = Decimal(raw_umsatz)
                if self.verbosity >= 2:
                    self.stdout.write("Konvertierter Umsatz: %r\n" % umsatz)

                start_date = valuta - datetime.timedelta(days=40)
                end_date = valuta
                rechnungen = Rechnung.objects.filter(datum__range=(start_date, end_date))
                if self.verbosity:
                    self.stdout.write("Anzahl der Rechnungen im Zeitraum %s - %s: %i\n" % (start_date, end_date, rechnungen.count()))

                if self.verbosity >= 3:
                    for no, r in enumerate(rechnungen):
                        self.stdout.write("%i: %s\n" % (no, r))

                rechnungen = rechnungen.exclude(valuta__isnull=False)
                if self.verbosity:
                    self.stdout.write("Anzahl der Rechnungen ohne Valuta-Datum: %i\n" % rechnungen.count())

                if self.verbosity >= 3:
                    for no, r in enumerate(rechnungen):
                        self.stdout.write("%i: %s\n" % (no, r))

                matched_rechnungen = []
                for rechnung in rechnungen:
                    total_brutto = rechnung.get_total_brutto()

                    if umsatz == total_brutto:
                        if self.verbosity:
                            self.stdout.write("Rechnung mit richtigem Umsatz gefunden: %s\n" % rechnung)
                        if str(rechnung.nummer) in line["Vorgang/Verwendungszweck"]:
                            if self.verbosity:
                                self.stdout.write("Rechnungsnummer in Verwendungszweck gefunden.\n")
                            matched_rechnungen.append(rechnung)

                if len(matched_rechnungen) == 1:
                    rechnung = matched_rechnungen[0]
                    self.stdout.write("Passende Rechnung gefunden: %s - speichere Valuta-Datum.\n" % rechnung)

                    rechnung.valuta = valuta
                    rechnung.save()
                    reversion.revision.comment = "Setzten vom Valuta-Datum auf %s nach cronbank csv Abgleich." % valuta

                self.stdout.write("-"*79)
                self.stdout.write("\n")




if __name__ == "__main__":
    management.call_command("import_cronbank", settings.CRONBANK_FILEPATH, verbosity=3)
