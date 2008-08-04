# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib import admin

media_url = settings.MEDIA_URL.strip("/")
assert media_url != ""

urlpatterns = patterns('',
    url(r'^skr_import/$', 'PyRM.importer.SKR03_view.menu', name="PyRM-SKR03-import"),
    (r'^skr_import/(?P<unit>\w*?)/$', 'PyRM.importer.SKR03_view.import_csv'),

    url(r'^mms_import/$', 'PyRM.importer.MMS_view.menu', name="PyRM-MMS-import"),
    (r'^mms_import/(?P<unit>\w*?)/$', 'PyRM.importer.MMS_view.import_csv'),

    url(r'^cao_import/$', 'PyRM.importer.CAO_view.menu', name="PyRM-CAO-import"),
    (r'^cao_import/(?P<unit>[a-z]*?)/$', 'PyRM.importer.CAO_view.import_csv'),

    url(r'^krb_import/$', 'PyRM.importer.KRB_view.menu', name="PyRM-MRB-import"),
    (r'^krb_import/(?P<unit>[a-z]*?)/$', 'PyRM.importer.KRB_view.import_csv'),

    (r'^%s/(.*)' % settings.ADMIN_URL_PREFIX, admin.site.root),

    (
        r'^%s/(?P<path>.*)$' % media_url,
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT},
    ),

    url(r'^import_menu/$', 'PyRM.importer.menu.menu', name="PyRM-import-menu"),
    url(r'^$', 'PyRM.index.menu', name="PyRM-main-menu"),
)