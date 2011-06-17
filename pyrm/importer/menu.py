# coding: utf-8
"""
    pyrm - importer
    ~~~~~~~~~~~~~~~



    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys


from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings

from django_tools.decorators import render_to

from pyrm.utils.unicode_stringio import UnicodeStringIO


@login_required
@render_to(template_name="import/menu.html", debug=False)
def menu(request):
    """
    Simple main menu
    """
    context = {
        "title": "import menu",
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return context


@login_required
@render_to(template_name="import/sub_menu.html", debug=False)
def _sub_menu(request, views):
    """
    Simple sub menu
    """
    context = {
        "title": "import sub menu",
        "views": views,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return context


@login_required
@render_to(template_name="import/output.html", debug=False)
def _start_view(request, views, unit):
    old_stdout = sys.stdout
    sys.stdout = UnicodeStringIO()
    views[unit]()
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    context = {
        "output": output,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
    }
    return context
