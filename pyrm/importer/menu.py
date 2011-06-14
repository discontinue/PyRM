# coding: utf-8
"""
    pyrm - importer
    ~~~~~~~~~~~~~~~



    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys
from pyrm.utils.unicode_stringio import UnicodeStringIO

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings


@login_required
def menu(request):
    """
    Simple main menu
    """
    context = {
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return render_to_response(
        "import_menu.html", context,context_instance=RequestContext(request)
    )

@login_required
def _sub_menu(request, views):
    """
    Simple sub menu
    """
    context = {
        "views": views,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return render_to_response(
        "import_sub_menu.html", context,context_instance=RequestContext(request)
    )

@login_required
def _start_view(request, views, unit):
    response = HttpResponse(mimetype='text/plain')

    old_stdout = sys.stdout
    sys.stdout = UnicodeStringIO()
    views[unit]()
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    context = {
        "output": output,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }

    return render_to_response(
        "import_output.html", context,context_instance=RequestContext(request)
    )