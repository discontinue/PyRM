# coding: utf-8
"""
    PyRM - Django admin stuff
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import

from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse

from pyrm.admin.rechnung import StatusAdmin, RechnungsPostenAdmin, RechnungAdmin
from pyrm.admin.stammdaten import OrtAdmin, PersonAdmin, FirmaAdmin, SkontoAdmin, \
    KundeLieferantStammdatenAdmin, KundeAdmin, LieferantAdmin
from pyrm.models.rechnung import Status, RechnungsPosten, Rechnung
from pyrm.models.stammdaten import Ort, Person, Firma, Skonto, KundeLieferantStammdaten, Kunde, Lieferant


admin.site.register(Status, StatusAdmin)
admin.site.register(RechnungsPosten, RechnungsPostenAdmin)
admin.site.register(Rechnung, RechnungAdmin)

admin.site.register(Ort, OrtAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Firma, FirmaAdmin)

admin.site.register(Skonto, SkontoAdmin)

admin.site.register(KundeLieferantStammdaten, KundeLieferantStammdatenAdmin)
admin.site.register(Kunde, KundeAdmin)
admin.site.register(Lieferant, LieferantAdmin)


def export_as_json(modeladmin, request, queryset):
    """
    from:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages
    """
    response = HttpResponse(mimetype="text/javascript")
    serializers.serialize("json", queryset, stream=response, indent=4)
    return response

# Make export actions available site-wide
admin.site.add_action(export_as_json, 'export_selected_as_json')


#------------------------------------------------------------------------------

from reversion.models import Revision, Version

class RevisionAdmin(admin.ModelAdmin):
    list_display = ("id", "date_created", "user", "comment")
    list_display_links = ("date_created",)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    list_filter = ("user", "comment")
    search_fields = ("user", "comment")

admin.site.register(Revision, RevisionAdmin)


class VersionAdmin(admin.ModelAdmin):
    list_display = ("object_repr", "revision", "object_id", "content_type", "format",)
    list_display_links = ("object_repr", "object_id")
    list_filter = ("content_type", "format")
    search_fields = ("object_repr", "serialized_data")

admin.site.register(Version, VersionAdmin)
