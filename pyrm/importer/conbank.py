# coding: utf-8

from django import forms
from django.core import management
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from django_tools.decorators import render_to



class UploadFileForm(forms.Form):
    file = forms.FileField()


def handle_uploaded_file(request):
    f = request.FILES['file']
    print f
    filepath = f.temporary_file_path()
    management.call_command("import_cronbank", filepath, verbosity=2)


@csrf_exempt
def import_view(request):
    request.upload_handlers.insert(0, TemporaryFileUploadHandler())
    return _upload_file_view(request)


@csrf_protect
@render_to("pyrm/cronbank_import.html")
def _upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request)
            return HttpResponseRedirect("")
    else:
        form = UploadFileForm()
    context = {
        "title": "Cronbank import",
        "form": form,
    }
    return context



