# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib import admin

media_url = settings.MEDIA_URL.strip("/")
assert media_url != ""

urlpatterns = patterns('',
    #__________________________________________________________________________
    # IMPORT VIEWS

    url(
        r'^mms_import/$', 'pyrm_app.importer.MMS_view.menu',
        name="pyrm_app-MMS-import"
    ),
    (
        r'^mms_import/(?P<unit>\w*?)/$',
        'pyrm_app.importer.MMS_view.start_view'
    ),

    url(
        r'^cao_import/$', 'pyrm_app.importer.CAO_view.menu',
        name="pyrm_app-CAO-import"
    ),
    (
        r'^cao_import/(?P<unit>[a-z]*?)/$',
        'pyrm_app.importer.CAO_view.start_view'
    ),

    url(
        r'^krb_import/$', 'pyrm_app.importer.KRB_view.menu',
        name="pyrm_app-KRB-import"
    ),
    (
        r'^krb_import/(?P<unit>[a-z]*?)/$',
        'pyrm_app.importer.KRB_view.start_view'
    ),


    #__________________________________________________________________________
    # DJANGO ADMIN PANEL
    (
        r'^login/',
        'django.contrib.auth.views.login',
        {'template_name': 'login.html'}
    ),
    (r'^%s/(.*)' % settings.ADMIN_URL_PREFIX, admin.site.root),

    #__________________________________________________________________________
    # STATIC FILES
    (
        r'^%s/(?P<path>.*)$' % media_url,
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT},
    ),

    #__________________________________________________________________________
    # EingangsRechnung Verwaltung

    url(
        r'^e-rechnung/$', 'pyrm_app.e-rechnung.index',
        name="pyrm_app-e-rechnung"
    ),
    url(
        r'^e-rechnung/specify/(?P<file_path>.+?)$', 'pyrm_app.e-rechnung.specify_file',
        name="pyrm_app-e-rechnung_specify"
    ),

    #__________________________________________________________________________
    # OTHER VIEWS

    url(
        r'^kontieren/$', 'pyrm_app.kontieren.index',
        name="pyrm_app-kontieren"
    ),
    url(
        r'^import_menu/$', 'pyrm_app.importer.menu.menu',
        name="pyrm_app-import-menu"
    ),
    url(
        r'^setup/$', 'pyrm_app.index.setup',
        name="pyrm_app-setup"
    ),
    url(
        r'^$', 'pyrm_app.index.menu',
        name="pyrm_app-main-menu"
    ),
)