# coding: utf-8

from __future__ import division, absolute_import

from datetime import datetime
from decimal import Decimal
from xml.sax import saxutils
import os
import pprint
import re

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


RE_TEXT_REXP = re.compile(r"^(\d+)[x ]+(.*?)[a ]+([\d,]+)$")
def _get_re_posten(raw_text, summe):
    text = saxutils.unescape(raw_text.strip(), entities={"&quot;":'"'})
    text_lines = text.splitlines()
    result = []
    test_summe = Decimal(0)
    for text_line in text_lines:
        get_all_rechnungs_posten = RE_TEXT_REXP.findall(text_line.strip())
        if get_all_rechnungs_posten == []:
            return [(Decimal(1), text, summe)]

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

#        try:
#            Rechnung.objects.all().delete()
#        except Rechnung.DoesNotExist:
#            pass
#
#        try:
#            RechnungsPosten.objects.all().delete()
#        except RechnungsPosten.DoesNotExist:
#            pass

        status_offen = Status.objects.get(bezeichnung="offen")
        status_bezahlt = Status.objects.get(bezeichnung="bezahlt")

        for line in _get_dictlist(filepath):
            notiz = ""
            raw_summe = line["Wert"]

            if self.verbosity >= 3:
                self.stdout.write("_" * 80)
                self.stdout.write("\n")
                self.stdout.write(pprint.pformat(line))
                self.stdout.write("\n")
            if raw_summe == "" or line["Rechnungstext"].startswith("^^^"):
                self.stdout.write(" *** SKIP: %r *** \n" % line)
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

            kunde = None
            lieferant = None

            kunden_nummer1 = line["K.Nr."]
            if kunden_nummer1 == "" or kunden_nummer1 == "999":
                # Kein kunde eingetragen
                kunden_nummer2 = None
            else:
                kunden_nummer2 = int(kunden_nummer1)

            #----------------------------------------------------------------------

            def _get_datum(raw_datum):
                if raw_datum != "":
                    try:
                        return datetime.strptime(raw_datum, "%d.%m.%y").date()
                    except ValueError:
                        return datetime.strptime(raw_datum, "%d.%m.%Y").date()

            raw_datum = line["R.Datum"]
            try:
                datum = _get_datum(raw_datum)
            except ValueError, err:
                self.stderr.write(" *** Re.Datum Fehler: %s\n" % err)
                self.stdout.write("%s\n" % pprint.pformat(line))
                datum = None
                notiz += "\nRaw Datum: %r\n" % raw_datum

            raw_valuta_datum = line["gezahlt\nEingang"]
            try:
                valuta = _get_datum(raw_valuta_datum)
            except ValueError, err:
                self.stderr.write(" *** ValutaDatum Fehler: %s\n" % err)
                self.stdout.write("%s\n" % pprint.pformat(line))
                valuta = None
                notiz += "\nRaw ValutaDatum: %r\n" % raw_valuta_datum

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

            if summe > 0 and "Gutschrift" not in line["Rechnungstext"]:
                # Ausgangsrechnung
                if re_nr == None:
                    self.stderr.write(" *** Fehler: Ausgangsrechnung ohne Re.Nummer???\n")
                    if self.verbosity:
                        pprint.pprint(line)
                    continue

                if kunden_nummer2 is not None:
                    try:
                        kunde = Kunde.objects.get(kunden_nr=kunden_nummer2)
                    except Kunde.DoesNotExist:
                        self.stderr.write(" *** Fehler: Kunde mit Nr. %r nicht gefunden!\n" % kunden_nummer2)
                        if self.verbosity:
                            pprint.pprint(line)
                        kunde = None
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
                    if self.verbosity >= 1:
                        self.stdout.write("schon vorhanden: %s\n" % rechnung)
                    continue
            else:
                # Eingangsrechnung/Ausgaben
                if kunden_nummer2 is not None:
                    lieferant = Lieferant.objects.get(lieferranten_nr=kunden_nummer2)
                if self.verbosity >= 3:
                    self.stdout.write("Lieferant: %r\n" % lieferant)

                rechnung, created = Rechnung.objects.get_or_create(
                    datum=datum,
                    summe=summe,
                    defaults={
                        "rechnungs_typ":Rechnung.EINGANGRE,
                        "status":status,
                        "createtime":datum,
                        "lieferant":lieferant,
                        "valuta":valuta,
                    }
                )
                if not created:
                    if self.verbosity >= 1:
                        self.stdout.write("schon vorhanden: %s\n" % rechnung)
                    continue

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

            self.stdout.write("%s erstellt.\n" % rechnung)


