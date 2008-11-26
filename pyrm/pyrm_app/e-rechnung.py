# -*- coding: utf-8 -*-

"""
    pyrm_app - Eingangs-Rechnung
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Verwaltung für Eingangsrechnungen

    Nach einem Upload landen alle PDF Dateien im Verzeichnis ./neu/

    Direkt nach dem Upload kann man den Lieferanten und das Rechnungsdatum
    angeben. Zur hilfe wird der Text aus dem PDF mit pdftotext angezeigt.

    Gibt man einen Lieferanten und das Datum an, wird die Rechnung von ./neu/
    in ein Unterverzeichnis (benannt nach dem Lieferanten) verschoben und dem
    Dateinamen wird das Datum der Rechnung vorrangestellt.

    All PDF Dateien im Verzeichnis ./neu/ kann man im nachhinein noch
    automatisch verschieben. Das ist nützlich. So kann man viele PDF Dateien
    im Dateisystem in das ./neu/ Verzeichnis kopieren und dann anschließend
    ein nach dem anderen spezifizieren. Einfach auf dem Dateinamen klicken.

    Das downloaden der PDF Dateien ist auch möglich.

    TODO:
        - Man sollte Meta Daten anlegen können, z.B. "ist gedruckt/eingeheftet"
        - verschieben/umbenennen der Dateien
        - SHA-1 checksum Datei könnte man beim Upload anlegen

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, subprocess, shutil, datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django import forms

from django_addons.forms_addons import ExtFileField
from pyrm_app.models import Lieferant

NEU_E_RECHNUNG = os.path.join(settings.E_RECHNUNGEN_DIR, "neu")

FILE_DATE_FORMAT = "%Y%m%d"
FORM_DATE_FORMAT = "%d.%m.%Y"

#------------------------------------------------------------------------------

class UploadForm(forms.Form):
    file  = ExtFileField(ext_whitelist = (".pdf",))

class SpecifyForm(forms.Form):
    lieferant = forms.ModelChoiceField(
        Lieferant.objects.all(), label="Lieferant"
    )
    datum = forms.DateField(
        label="Datum",
        input_formats=["%d.%m.%y", FORM_DATE_FORMAT]
    )

#------------------------------------------------------------------------------

class FilePath(object):
    def __init__(self, file_path):
        if not os.path.isfile(file_path):
            raise Http404("File '%s' not found!" % file_path)
        if not file_path.startswith(settings.E_RECHNUNGEN_DIR):
            raise Http404("path '%s' not allowed!" % file_path)

        self.file_path = file_path
        self.abs_path = os.path.abspath(file_path)
        self.path, self.filename = os.path.split(file_path)
    
    def get_lieferant_from_path(self):
        last_path = os.path.split(self.path)[-1]
        try:
            no, name = last_path.split("-",1)
            no = int(no)
            name = name.strip()
        except ValueError:
            return None
        
        return Lieferant.objects.get(nummer = no)
    
    def get_date_from_filename(self):
        date_string = self.filename.split("_",1)[0]
        try:
            return datetime.datetime.strptime(date_string, FILE_DATE_FORMAT)
        except ValueError:
            return None        

    def get_specify_url(self):
        return reverse(
            'pyrm_app-e-rechnung_specify', kwargs={"file_path": self.file_path}
        )

    def get_download_url(self):
        return reverse(
            'pyrm_app-e-rechnung_download', kwargs={"file_path": self.file_path}
        )

#------------------------------------------------------------------------------

def handle_uploaded_file(f):
    """
    Neue EingangsRechnungs PDF Datei
    """
    if not os.path.isdir(NEU_E_RECHNUNG):
        os.makedirs(NEU_E_RECHNUNG)

    destination = os.path.join(NEU_E_RECHNUNG, f.name)
    new_file = file(destination, 'wb+')
    for chunk in f.chunks():
        new_file.write(chunk)

    new_file.close()
    
    fp = FilePath(destination)
    url = fp.get_specify_url()
    return HttpResponseRedirect(url)


def move_rechnung(file_path, lieferant, datum):

    date_prefix = datum.strftime(FILE_DATE_FORMAT)
    path, filename = os.path.split(file_path)

    if filename.startswith(date_prefix):
        new_filename = filename
    else:
        new_filename = date_prefix + "_" + filename

    dest_path = os.path.join(settings.E_RECHNUNGEN_DIR, unicode(lieferant))
    if not os.path.isdir(dest_path):
        print "os.makedirs:", dest_path
        os.makedirs(dest_path)

    destination = os.path.join(dest_path, new_filename)

    print "shutil.move: '%s'->'%s'" % (file_path, destination)
    shutil.move(file_path, destination)




@login_required
def specify_file(request, file_path):
    """
    Eine Bestehende Rechnung einsortieren.
    Es wird per pdftotext der Text der PDF Datei angezeigt.
    """
    fp = FilePath(file_path)
    file_path_abs = fp.abs_path

    process = subprocess.Popen(
        [settings.PDFTOTEXT, "-layout", file_path_abs, "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    process.wait()
    returncode = process.returncode
    stderr = process.stderr.read()

    pdf_text = process.stdout.read()
#    pdf_text = pdf_text.replace("  ", " ")

    if request.method == 'POST':
        form = SpecifyForm(request.POST)
        if form.is_valid():
            move_rechnung(
                file_path,
                form.cleaned_data["lieferant"],
                form.cleaned_data["datum"]
            )
            url = reverse('pyrm_app-e-rechnung')
            return HttpResponseRedirect(url)
    else:
        lieferant = fp.get_lieferant_from_path()
        init_data = {
            "lieferant": lieferant,
        }
        
        datum = fp.get_date_from_filename()
        if datum:
            init_data["datum"] = datum.strftime(FORM_DATE_FORMAT)
        
        print init_data
        form = SpecifyForm(initial=init_data)
#        .fields["lieferant"]

    back_url = reverse('pyrm_app-e-rechnung')

    context = {
        "url": request.path_info,
        "back_url": back_url,
        "download_url": fp.get_download_url(),
        "form": form,
        "file_path": file_path,
        "pdf_text": pdf_text,
        "returncode": returncode,
        "stderr": stderr,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }

    return render_to_response(
        "e-rechnung_specify.html", context,
        context_instance=RequestContext(request)
    )


def filelist():
    """
    Erstellt eine Liste mit allen vorhandenen EingangsRechnungen.
    """
    def remove_start(start_string, text):
        if text.startswith(start_string):
            return text[len(start_string):]
        else:
            return text

    data = {}
    for root, dirs, files in os.walk(settings.E_RECHNUNGEN_DIR):
        file_list = []
        for fn in sorted(files, reverse=True):
            if not fn.lower().endswith(".pdf"):
                continue
            file_path = os.path.join(root, fn)

            fp = FilePath(file_path)
            specify_url = fp.get_specify_url()
            download_url = fp.get_download_url()

            file_list.append({
                "specify_url": specify_url,
                "download_url": download_url,
                "name": fn
            })
        if file_list:
            dir = remove_start(settings.E_RECHNUNGEN_DIR, root)
            data[dir] = file_list

    return data


@login_required
def download(request, file_path):
    """
    Download einer PDF Rechnungsdatei
    """
    fp = FilePath(file_path)

    filename = fp.filename

    f = file(file_path, "rb")
    file_data = f.read()
    f.close()

    response = HttpResponse(file_data, mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response



@login_required
def index(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_uploaded_file(request.FILES['file'])
    else:
        form = UploadForm()

    context = {
        "form": form,
        "filelist": filelist(),
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }

    return render_to_response(
        "e-rechnung.html", context,
        context_instance=RequestContext(request)
    )