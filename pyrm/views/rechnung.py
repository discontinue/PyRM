# coding: utf-8

from django.shortcuts import get_object_or_404

from django_tools.decorators import render_to

from pyrm.models.rechnung import Rechnung


@render_to("pyrm/html_print/rechnung.html", debug=False)
def rechnung_drucken(request, pk):
    rechnung = get_object_or_404(Rechnung, pk=pk)
    context = {
        "rechnung": rechnung,
        "is_copy": "is_copy" in request.GET,
    }
    return context
