# coding: utf-8

"""
    pyrm
    ~~~~
    
    Import der Buchungen aus Finanzbuchhaltung der MMS GmbH Bonn

    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

import sys, os, csv, re
import pprint
from decimal import Decimal
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import reversion # django-reversion

from pyrm.models import Rechnung, RechnungsPosten, Firma, Person, Kunde, Lieferant, Ort
from pyrm.importer.menu import _sub_menu, _start_view
from pyrm.utils.csv_utils import get_csv_tables, get_dictlist
from pyrm.models.konten import Konto
from pyrm.models.rechnung import Status


PROZ_RE = re.compile(r"(\d+?)\%")
RECHNUNG_RE = re.compile(r"^(\d{3})-(\d{3,4})$")


# Der Steuerschlüssel steht der datev kontonummer vorran
STEUER_SCHLUESSEL = {
    3: Decimal(19), # Umsatzsteuer 19%
    5: Decimal(16), # Umsatzsteuer 16%
    7: Decimal(16), # Vorsteuer 16%
    8: Decimal(7), # Vorsteuer 7%
    9: Decimal(19), # Vorsteuer 19%
}


def _get_decimal(raw_summe):
    summe1 = raw_summe.replace(".", "") # tausender punkte?
    summe2 = summe1.replace(",", ".")
    summe = Decimal(summe2)
    return summe


class Command(BaseCommand):
    help = "Import der Buchungen aus Finanzbuchhaltung der MMS GmbH Bonn."
    args = "/path/to/TRANSFER.CSV"

    @reversion.revision.create_on_success
    def handle(self, filepath, **options):
        if not os.path.isfile(filepath):
            raise CommandError("Filepath %r doesn't exist." % filepath)

        self.verbosity = int(options.get('verbosity', 1))

        buchungen, konten = get_csv_tables(filepath)

        self._insert_konten(konten)

        self.status_bezahlt = Status.objects.get(bezeichnung="bezahlt")

        self._insert_buchungen(buchungen)

    def _insert_konten(self, konten):
        dictlist = get_dictlist(konten, used_fieldnames=None)
        for line in dictlist:
            if self.verbosity >= 4:
                self.stdout.write("_" * 80)
                self.stdout.write("\n")
                self.stdout.write(pprint.pformat(line))

            nummer = int(line['Konto'])
            konto_name = line['Listenname']

            konto, created = Konto.objects.get_or_create(nummer=nummer,
                defaults={"name":konto_name}
            )
            if created:
                if self.verbosity:
                    self.stdout.write("Konto erstellt: %s\n" % konto)
            else:
                if konto.name != konto_name:
                    self.stdout.write("Konto %i wird von %r auf %r geändert\n" % (nummer, konto.name, konto_name))
                    konto.name = konto_name
                    konto.save()
                elif self.verbosity >= 2:
                    self.stdout.write("Vorhandes Konto genutzt: %s\n" % konto)

    def _check_rechnung(self, rechnung, summe_netto):
        summe_pyrm = rechnung.summe
        if summe_pyrm != summe_netto:
            self.stderr.write("Fehler: Rechnungssumme %s (PyRM) ist nicht %s (MMS) Rechnung: %s\n" % (
                summe_pyrm, summe_netto, rechnung
            ))
            return False
        return True

    def _update_rechnung(self, rechnung, summe_netto, datum, konto, ggkto):
        rechnung.status = self.status_bezahlt

        if rechnung.valuta == datum:
            if self.verbosity >= 1:
                self.stdout.write("Rechnungs valuta datum ok\n")
        else:
            if rechnung.valuta == None:
                if self.verbosity:
                    self.stdout.write("Rechnungs valuta datum auf %s gesetzt, ok\n" % datum)
            else:
                self.stderr.write("Fehler: Setzte Rechnungs valuta datum von %s (PyRM) auf %s (MMS)\n" % (
                    rechnung.valuta, datum
                ))
            rechnung.valuta = datum

        rechnung.save()
        reversion.revision.comment = "Korrigiert beim MMS import."


        alle_posten = RechnungsPosten.objects.filter(rechnung=rechnung)
        for posten in alle_posten:
            posten.konto = konto
            posten.gegenkonto = ggkto
            posten.save()
            reversion.revision.comment = "Neu erstellt beim MMS import."

    def _insert_buchungen(self, buchungen):
        dictlist = get_dictlist(buchungen, used_fieldnames=None)
        for line in dictlist:
            if self.verbosity >= 4:
                self.stdout.write("_" * 80)
                self.stdout.write("\n%s\n" % pprint.pformat(line))

            date_string = line["Datum"]
            #print "date_string:", date_string
            datum = datetime.strptime(date_string, "%d.%m.%Y").date()
            #datum = date.strptime(date_string, "%d.%m.%Y")

            raw_summe = line["Betrag"]
            summe = _get_decimal(raw_summe)

            konto_nr = int(line["Konto"])
            #print "konto_nr:", konto_nr, type(konto_nr)
            if konto_nr == 9000: # EB-Sachkonten
                if self.verbosity >= 2:
                    self.stdout.write("Endbestand des Kontos vom Vorjahr: %s\n" % summe)
                continue

            try:
                konto = Konto.objects.get(nummer=konto_nr)
            except Konto.DoesNotExist, err:
                print "*" * 79
                print "Fehler: Konto unbekannt:", err
                konto = None

            ggkto = line["GGKto"]
            if len(ggkto) > 4:
                # SteuerSchlüssel drin
                stsl_nr = int(ggkto[0])
                ggkto_nr = int(ggkto[1:])
                mwst = STEUER_SCHLUESSEL[stsl_nr]

                summe_netto = summe / ((mwst / Decimal(100)) + Decimal(1))
                if self.verbosity >= 3:
                    self.stdout.write(
                        "Brutto: %s - %s%% (Steuerschlüssel: %i) = %s Netto\n" % (
                            summe, mwst, stsl_nr, summe_netto
                        )
                    )
            else:
                summe_netto = summe
                ggkto_nr = int(ggkto)
                mwst = None

            try:
                ggkto = Konto.objects.get(nummer=ggkto_nr)
            except Konto.DoesNotExist, err:
                print "*" * 79
                print "Fehler: Gegenkonto unbekannt:", err
                ggkto = None

            if summe > 0:
                # Ausgangsrechnung für den Kunden
                rechnungs_typ = Rechnung.AUSGANGRE
            else:
                # zu bezahlender Eingangsrechnung eines Lieferanten
                rechnungs_typ = Rechnung.EINGANGRE


            kommentar = line["Kommentar"]
            if rechnungs_typ == Rechnung.AUSGANGRE and "-" in kommentar:
                if self.verbosity >= 3:
                    self.stdout.write("Kommentar: %s\n" % kommentar)
                try:
                    matches = RECHNUNG_RE.findall(kommentar)[0]
                    raw_kunden_nr, raw_re_nr = matches
                    kunden_nr = int(raw_kunden_nr)
                    re_nr = int(raw_re_nr)
                except (IndexError, ValueError), err:
                    print "Keine Re.Nr.: %s" % err
                else:
                    # Kunden nummer + Rechnungsnummer in Kommentar
                    if self.verbosity >= 3:
                        self.stdout.write("Aus Kommentar: KundenNr: %r, ReNr.: %r\n" % (kunden_nr, re_nr))

                    try:
                        kunde = Kunde.objects.get(kunden_nr=kunden_nr)
                    except Kunde.DoesNotExist, err:
                        print "FEHLER: Kunde %s nicht gefunden: %s" % (
                            kunden_nr, err
                        )
                        kunde = None
                    else:
                        try:
                            rechnung = Rechnung.objects.get(ausgangs_re_nr=re_nr)
                        except Rechnung.DoesNotExist, err:
                            print "FEHLER: Rechnung %s nicht gefunden: %s" % (
                                re_nr, err
                            )
                            rechnung = None
                        else:
                            if self.verbosity >= 3:
                                self.stdout.write("Rechnung über Kommentar gefunden: %s\n" % rechnung)
                                continue
                            if self._check_rechnung(rechnung, summe_netto) == True:
                                self._update_rechnung(rechnung, summe_netto, datum, konto, ggkto)
                                continue

            try:
                rechnungen = Rechnung.objects.filter(summe=summe, valuta=datum)
            except Rechnung.DoesNotExist:
                pass
            else:
                if len(rechnungen) == 0:
                    rechnung = None
                elif len(rechnungen) == 1:
                    rechnung = rechnungen[0]
                    if self.verbosity >= 3:
                        self.stdout.write("Rechnung über summe+datum gefunden: %s\n" % rechnung)
                    self._update_rechnung(rechnung, summe_netto, datum, konto, ggkto)
                    continue
                else:
                    sys.stderr.write("Fehler: Mehrere Rechnungen vom %s mit %s gefunden:\n" % (datum, summe))
                    print len(rechnungen)
                    for rechnung in rechnungen:
                        print "rechnung: %s" % rechnung
                    continue

            rechnung = Rechnung(
                rechnungs_typ=rechnungs_typ,
                notizen="Raw MMS import line: %r" % line,
                datum=datum,
                valuta=datum,
                status=self.status_bezahlt,
            )
            rechnung.save()
            reversion.revision.comment = "Neu erstellt beim MMS import."

            p = RechnungsPosten(
                rechnung=rechnung,
                menge=1,
                konto=konto,
                gegenkonto=ggkto,
                beschreibung="MMS import",
                notizen="Raw MMS import line: %r" % line,
                einzelpreis=summe,
                mwst=mwst,
            )
            p.save()
            reversion.revision.comment = "Neu erstellt beim MMS import."

            if self.verbosity >= 1:
                self.stdout.write("%s wurde erstellt: %s:" % (Rechnung.TYP_DICT[rechnungs_typ], rechnung))
                self.stdout.write("RechnungsPosition %s\n" % p)

