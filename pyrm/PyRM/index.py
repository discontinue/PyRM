# -*- coding: utf-8 -*-

import sys

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db.models import get_app, get_models
from django.contrib.auth.decorators import login_required

from PyRM.utils.unicode_stringio import UnicodeStringIO

#@login_required
def menu(request):
    """
    Simple main menu
    """
    context = {
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return render_to_response(
        "main_menu.html", context,context_instance=RequestContext(request)
    )

@login_required
def setup(request):
    """
    initialisiere alle Models
    """
    response = HttpResponse(mimetype='text/plain')

    old_stdout = sys.stdout
    sys.stdout = UnicodeStringIO()

    print "Setup!"

    app = get_app("PyRM")
    for model in get_models(app):
        model_name = model._meta.object_name
        print model_name
        if hasattr(model.objects, "setup"):
            print "Starte Model Manager setup:"
            setup_method = getattr(model.objects, "setup")
            setup_method()
        print "-"*80

    context = {
        "output": sys.stdout.getvalue(),
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    sys.stdout = old_stdout

    return render_to_response(
        "import_output.html", context,context_instance=RequestContext(request)
    )