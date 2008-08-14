# -*- coding: utf-8 -*-

"""
    pyrm_app - Eingangs-Rechnung
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Verwaltung für Eingangsrechnungen

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, subprocess

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django import forms

from django_addons.forms_addons import ExtFileField
from pyrm_app.models import Lieferant

NEU_E_RECHNUNG = os.path.join(settings.E_RECHNUNGEN_DIR, "neu")


class UploadForm(forms.Form):
    file  = ExtFileField(ext_whitelist = (".pdf",))

class SpecifyForm(forms.Form):
    title = forms.ModelChoiceField(Lieferant.objects.all(), label="Lieferant")
    date = forms.DateField(label="Datum")

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
    url = get_specify_url(destination)
    return HttpResponseRedirect(url)

def get_specify_url(file_path):
    return reverse(
        'pyrm_app-e-rechnung_specify', kwargs={"file_path": file_path}
    )

@login_required
def specify_file(request, file_path):
    if not os.path.isfile(file_path):
        raise Http404("File '%s' not found!" % file_path)
    if not file_path.startswith(NEU_E_RECHNUNG):
        raise Http404("Wrong path '%s'!" % file_path)

    file_path_abs = os.path.abspath(file_path)
    process = subprocess.Popen(
        [settings.PDFTOTEXT, file_path_abs, "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    process.wait()
    returncode = process.returncode
    pdf_text = process.stdout.read()
    stderr = process.stderr.read()

    if request.method == 'POST':
        form = SpecifyForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = SpecifyForm()

    context = {
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
    data = {}
    for root, dirs, files in os.walk(settings.E_RECHNUNGEN_DIR):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue
            if root not in data:
                data[root] = []

            file_path = os.path.join(root, file)
            url = get_specify_url(file_path)
            data[root].append({
                "url": url,
                "name": file,
            })
    return data



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