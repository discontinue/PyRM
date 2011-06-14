# coding: utf-8

import sys

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import get_app, get_models
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django_tools.decorators import render_to

from pyrm.utils.unicode_stringio import UnicodeStringIO


#@login_required
@render_to(template_name="pyrm/main_menu.html", debug=False)
def menu(request):
    """
    Simple main menu
    """
    context = {
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return context


@login_required
def setup(request):
    """
    initialisiere alle Models
    """
    response = HttpResponse(mimetype='text/plain')

    old_stdout = sys.stdout
    sys.stdout = UnicodeStringIO()

    print "Setup!"

    app = get_app("pyrm")
    for model in get_models(app):
        model_name = model._meta.object_name
        print model_name
        if hasattr(model.objects, "setup"):
            print "Starte Model Manager setup:"
            setup_method = getattr(model.objects, "setup")
            setup_method()
        print "-" * 80

    context = {
        "output": sys.stdout.getvalue(),
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    sys.stdout = old_stdout

    return render_to_response(
        "import_output.html", context, context_instance=RequestContext(request)
    )
