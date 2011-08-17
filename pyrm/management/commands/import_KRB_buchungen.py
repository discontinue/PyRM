# coding: utf-8

from __future__ import division, absolute_import

from datetime import datetime
from decimal import Decimal
import os
import pprint
import re
import sys

import reversion # django-reversion

from django.core.management.base import BaseCommand, CommandError

from pyrm.models import Kunde, Lieferant, Rechnung, RechnungsPosten
from pyrm.utils.csv_utils import get_dictlist
from pyrm.models.rechnung import Status




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
    if raw_datum == "":
        return

    if len(raw_datum) == 8:
        try:
            return datetime.strptime(raw_datum, "%d.%m.%y").date()
        except Exception, err:
            sys.stderr.write("*** Fehler 1: %s bei Datum: %r\n" % (err, raw_datum))
    elif len(raw_datum) == 10:
        try:
            return datetime.strptime(raw_datum, "%d.%m.%Y").date()
        except ValueError, err:
            sys.stderr.write("*** Fehler 2: %s bei Datum: %r\n" % (err, raw_datum))
    else:
        sys.stderr.write("*** Fehler: Ungültiges Datum: %r\n" % raw_datum)





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

        print "Lösche alte Einträge...",
        try:
            Rechnung.objects.all().delete()
        except Rechnung.DoesNotExist:
            pass

        try:
            RechnungsPosten.objects.all().delete()
        except RechnungsPosten.DoesNotExist:
            pass
        print "OK"

        status_offen = Status.objects.get(bezeichnung="offen")
        status_bezahlt = Status.objects.get(bezeichnung="bezahlt")

        for line in _get_dictlist(filepath):
            notiz = ""
            raw_summe = line["Wert"]

            if self.verbosity >= 4:
                self.stdout.write("_" * 80)
                self.stdout.write("\n")
                self.stdout.write(pprint.pformat(line))
                self.stdout.write("\n")
            if raw_summe == "" or line["Rechnungstext"].startswith("^^^"):
                self.stdout.write(" *** SKIP %r *** \n" % line)
                continue

            if self.verbosity >= 4:
                self.stdout.write(" -" * 40)
                self.stdout.write("\n")

            #----------------------------------------------------------------------

            raw_summe = raw_summe.split(" ")[0]
            summe = _get_decimal(raw_summe)
            if self.verbosity >= 3:
                self.stdout.write("Betrag: %r\n" % summe)

            #----------------------------------------------------------------------

            kunde = None
            lieferant = None

            kunden_nummer1 = line["K.Nr."]
            if kunden_nummer1 == "" or kunden_nummer1 == "999":
                # Kein kunde eingetragen
                kunden_nummer2 = None
            else:
                kunden_nummer2 = int(kunden_nummer1)

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

            if valuta:
                status = status_bezahlt
            else:
                status = status_offen

            kunde = None
            lieferant = None

            if summe > 0:
                # Ausgangsrechnung
                if re_nr == None:
                    self.stderr.write("Fehler: Rechnung ohne Re.Nummer???\n")
                    pprint.pprint(line)
                    continue

                if kunden_nummer2 is not None:
                    kunde = Kunde.objects.get(kunden_nr=kunden_nummer2)
                if self.verbosity >= 3:
                    self.stdout.write("Kunde: %r\n" % kunde)

                rechnung, created = Rechnung.objects.get_or_create(
                    ausgangs_re_nr=re_nr,
                    defaults={
                        "createtime":datum,

                        "rechnungs_typ":Rechnung.AUSGANGRE,
                        "status":status,

                        "kunde":kunde,
                        "datum":datum,
                        "valuta":valuta,
                    }
                )
                if not created:
                    self.stderr.write("*** Fehler: Re mit Nr. %s schon vorhanden!" % re_nr)
                    continue
            else:
                # Eingangsrechnung/Ausgaben
                if kunden_nummer2 is not None:
                    lieferant = Lieferant.objects.get(lieferranten_nr=kunden_nummer2)
                if self.verbosity >= 3:
                    self.stdout.write("Lieferant: %r\n" % lieferant)
                rechnung = Rechnung(
                    rechnungs_typ=Rechnung.EINGANGRE,
                    status=status,
                    createtime=datum,
                    lieferant=lieferant,
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

            self.stdout.write("Rechnung %s erstellt.\n" % rechnung)


