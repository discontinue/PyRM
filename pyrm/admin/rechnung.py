# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

from django.contrib import admin
from django.template.loader import render_to_string
from django_tools.decorators import render_to

from reversion.admin import VersionAdmin

from pyrm.models.base_models import BASE_FIELDSET
from pyrm.models.rechnung import RechnungsPosten, Rechnung
from pyrm.utils.django_modeladmin import add_missing_fields
from django.conf import settings


class StatusAdmin(VersionAdmin):
    pass

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

    def summe2(self, obj):
        if obj.summe < 0:
            return u'<span style="color:#ff0000;">%.2f\N{EURO SIGN}</span>' % obj.summe
        return u"<strong>%.2f\N{EURO SIGN}</strong>" % obj.summe
    summe2.short_description = "summe"
    summe2.allow_tags = True

    def valuta2(self, obj):
        if obj.valuta is None:
            return '<span style="color:#ff0000;">offen</span>'

        # FIXME: How can we call the existing solution here:
        return obj.valuta.strftime("%d.%m.%Y")

    valuta2.short_description = "valuta"
    valuta2.allow_tags = True

    inlines = (PostenInline,)
    list_display = ("kunde", "summe2", "print_link", "datum", "valuta2", "lastupdatetime")
    list_display_links = ("kunde",)
    list_filter = ("mahnstufe", "status", "rechnungs_typ", "kunde",)
    list_per_page = 20
    list_select_related = True
    search_fields = [
        "summe",
        "kunde__kunden_nr",
        "rechnungsposten__beschreibung",
    ]

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
