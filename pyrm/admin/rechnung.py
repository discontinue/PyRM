# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.conf.urls.defaults import patterns, url
from django.contrib import admin, messages
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from reversion.admin import VersionAdmin

from django_tools.decorators import render_to

from pyrm.models.base_models import BASE_FIELDSET
from pyrm.models.rechnung import RechnungsPosten, Rechnung
from pyrm.utils.django_modeladmin import add_missing_fields
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core import serializers


class RechnungsPostenAdmin(VersionAdmin):
    list_display = (
        "beschreibung", "menge", "einzelpreis", "einheit", "rechnung"
    )
    list_display_links = ("beschreibung",)
    list_filter = ("rechnung", "einheit")
    list_per_page = 20
    list_select_related = True
    search_fields = ("beschreibung",)

#    fieldsets = (
#        (None, {
#            'fields': ("anzahl", "beschreibung", "einzelpreis", "rechnung")
#        }),
#        BASE_FIELDSET
#    )
#    fieldsets = add_missing_fields(BasisPosten, fieldsets)


class PostenInline(admin.TabularInline):
#class PostenInline(admin.StackedInline):
    model = RechnungsPosten
#    class Media:
#        css = {"all":("/static/rechnungsposten.css",)}
    fieldsets = (
        (None, {
            "fields": ("order", "menge", "einheit", "beschreibung", "einzelpreis", "mwst")
        }),
        ("sonstiges", {
            'classes': ('collapse',),
            "fields": ("notizen",)
        })
    )


@render_to("pyrm/export/rechnung_KRB.csv", mimetype="text/plain")
def export_rechnung_as_csv(modeladmin, request, queryset):
    """
    Export as pseudo CSV (for copy&paste into LibreOffice ;)
    """
    context = {
        "queryset": queryset,
    }
    return context


class RechnungAdmin(VersionAdmin):
    inlines = (PostenInline,)
    list_display = ("nummer", "kunde", "datum", "print_link", "valuta", "summe", "lastupdatetime")
    list_display_links = ("nummer", "kunde")
    list_filter = ("mahnstufe", "kunde",)
    list_per_page = 20
    list_select_related = True
    search_fields = ['foreign_key__related_fieldname']

#    fieldsets = (
#        (None, {
#            'fields': (
#                "nummer", "bestellnummer", "kunde", "anschrift", "summe",
#                "mahnstufe"
#            )
#        }),
#        ('Datum', {
##            'classes': ('collapse',),
#            'fields': ("datum", "lieferdatum", "versand", "valuta")
#        }),
#        BASE_FIELDSET,
#    )
#    fieldsets = add_missing_fields(Rechnung, fieldsets)

    def get_actions(self, request):
        actions = super(RechnungAdmin, self).get_actions(request)
        actions["export_rechnung_as_csv"] = (export_rechnung_as_csv, "export_rechnung_as_csv", "Export Rechnung as CSV")
        return actions

    def print_link(self, instance):
        """ For adding a edit link into django admin interface """
        context = {
            "instance": instance,
            "is_copy": False,
        }
        return render_to_string('pyrm/admin/print_link.html', context)
    print_link.allow_tags = True
    print_link.short_description = "drucken"

#    @render_to("pyrm/admin/rechnung_drucken.html", debug=False)
#    def rechnung_drucken(self, request, pk):
#        rechnung = get_object_or_404(Rechnung, pk=pk)
#        context = {
#            "title": "Rechnung drucken",
#            "rechnung": rechnung,
#        }
#        return context
#
#    def get_urls(self):
#        urls = super(RechnungAdmin, self).get_urls()
#        my_urls = patterns('',
#            url(r'^(?P<pk>\d+)/rechnung_drucken/$', self.admin_site.admin_view(self.rechnung_drucken),
#            name="rechnung_drucken")
#        )
#        return my_urls + urls
