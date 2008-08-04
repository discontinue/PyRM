# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
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
        "main_menu.html", context,context_instance=RequestContext(request)
    )