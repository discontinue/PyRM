# coding: utf-8

import os, re
from datetime import datetime
import pprint
from decimal import Decimal

import reversion # django-reversion

from pyrm.models import Kunde, Lieferant, Rechnung, RechnungsPosten

from pyrm.utils.csv_utils import get_dictlist


from django.core.management.base import BaseCommand, CommandError


def _get_dictlist(filename):
    # python csv module doesn't work with unicode! So no codecs.open() here!
    f = file(filename, "rb")
    data = f.readlines()
    f.close()

    dictlist = get_dictlist(data, encoding="latin-1", used_fieldnames=None)
    return dictlist

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
        get_all_rechnungs_posten = RE_TEXT_REXP.findall(text_line.strip())
        if get_all_rechnungs_posten == []:
            return [(Decimal(1), raw_text, summe)]

        assert len(get_all_rechnungs_posten) == 1
        get_all_rechnungs_posten = get_all_rechnungs_posten[0]

        raw_anzahl, txt, raw_preis = get_all_rechnungs_posten
        anzahl = Decimal(str(raw_anzahl))
        preis = _get_decimal(raw_preis)

        result.append((anzahl, txt, preis))
        test_summe += (anzahl * preis)

    assert test_summe == summe
    return result


class Command(BaseCommand):
    help = 'Import KRB Buchungen.'
    args = "/path/to/KRB_buchungen.csv"

    @reversion.revision.create_on_success
    def handle(self, filepath, **options):
        if not os.path.isfile(filepath):
            raise CommandError("Filepath %r doesn't exist." % filepath)

        self.verbosity = int(options.get('verbosity', 1))

        try:
            Rechnung.objects.all().delete()
        except Rechnung.DoesNotExist:
            pass

        try:
            RechnungsPosten.objects.all().delete()
        except RechnungsPosten.DoesNotExist:
            pass

        try:
            Lieferant.objects.all().delete()
        except Lieferant.DoesNotExist:
            pass


        for line in _get_dictlist(filepath):
            notiz = ""
            raw_summe = line["Wert"]

            if self.verbosity >= 3:
                self.stdout.write("_" * 80)
                self.stdout.write("\n")
                self.stdout.write(pprint.pformat(line))
                self.stdout.write("\n")
            if raw_summe == "" or line["Rechnungstext"].startswith("^^^"):
                self.stdout.write(" *** SKIP *** \n")
                continue

            if self.verbosity >= 3:
                self.stdout.write(" -" * 40)
                self.stdout.write("\n")

            #----------------------------------------------------------------------

            raw_summe = raw_summe.split(" ")[0]
            summe = _get_decimal(raw_summe)
            if self.verbosity >= 3:
                self.stdout.write("Betrag: %r\n" % summe)

            #----------------------------------------------------------------------

            kunden_nummer1 = line["K.Nr."]
            if kunden_nummer1 == "" or kunden_nummer1 == "999":
                # Kein kunde eingetragen
                kunde = None
            else:
                kunden_nummer2 = int(kunden_nummer1)
                kunde = Kunde.objects.get(nummer=kunden_nummer2)
            if self.verbosity >= 3:
                self.stdout.write("Kunde: %r\n" % kunde)

            #----------------------------------------------------------------------

            datum = _get_datum(raw_datum=line["R.Datum"])
            raw_valuta_datum = line["gezahlt\nEingang"]
            try:
                valuta = _get_datum(raw_datum=raw_valuta_datum)
            except ValueError, err:
                self.stdout.write("ValueError: %s\n" % err)
                notiz += raw_valuta_datum

            #----------------------------------------------------------------------

            re_posten = _get_re_posten(line["Rechnungstext"], summe)
            if self.verbosity >= 3:
                self.stdout.write("RE.Posten:\n")
                if len(re_posten) > 1:
                    self.stdout.write(" *" * 40)
                    self.stdout.write("\n")
                self.stdout.write(pprint.pformat(re_posten))
                self.stdout.write("\n")

            #----------------------------------------------------------------------

            raw_nr = line["R.Nr."]
            if raw_nr == "":
                re_nr = None
            else:
                re_nr = int(raw_nr)

            #----------------------------------------------------------------------

            if summe < 0:
                self.stdout.write("TODO: Ausgabe - Eingangsrechnung\n")
                if self.verbosity >= 2:
                    self.stdout.write("*" * 79)
                    self.stdout.write("\n")
                continue


            if re_nr == None:
                self.stdout.write("Fehler: Rechnung ohne Re.Nummer???\n")
                continue

            rechnung = Rechnung(
                createtime=datum,

                nummer=re_nr,
                kunde=kunde,
                datum=datum,
                valuta=valuta,
            )
            rechnung.save()
            reversion.revision.comment = "KRB import"

            for menge, txt, preis in re_posten:
                p = RechnungsPosten(
                    menge=menge,
                    beschreibung=txt,
                    einzelpreis=preis,
                    rechnung=rechnung
                )
                p.save()
                reversion.revision.comment = "KRB import"

            self.stdout.write("Einnahme - Rechnung %s erstellt.\n" % rechnung)


