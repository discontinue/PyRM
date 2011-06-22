# coding: utf-8

from django.conf import settings
from django.conf.urls.defaults import url, patterns, include
from django.contrib import admin

from pyrm.views.rechnung import rechnung_drucken

media_url = settings.MEDIA_URL.strip("/")
assert media_url != ""

admin.autodiscover()

urlpatterns = patterns('',

    url(
        r'^rechnung_drucken/(?P<pk>\d+)/$', rechnung_drucken,
        name="pyrm-rechnung_drucken"
    ),


    #__________________________________________________________________________
    # IMPORT VIEWS

    url(
        r'^mms_import/$', 'pyrm.importer.MMS_view.menu',
        name="pyrm-MMS-import"
    ),
    (
        r'^mms_import/(?P<unit>.+?)/$',
        'pyrm.importer.MMS_view.start_view'
    ),

    url(
        r'^cao_import/$', 'pyrm.importer.CAO_view.menu',
        name="pyrm-CAO-import"
    ),
    (
        r'^cao_import/(?P<unit>.+?)/$',
        'pyrm.importer.CAO_view.start_view'
    ),

    url(
        r'^conbank_import/$', 'pyrm.importer.conbank.import_view',
        name="pyrm-conbank-import"
    ),

    #__________________________________________________________________________
    # DJANGO ADMIN PANEL
    (
        r'^login/',
        'django.contrib.auth.views.login',
        {'template_name': 'login.html'}
    ),
    url(r'^%s/' % settings.ADMIN_URL_PREFIX, include(admin.site.urls)),
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
        r'^e-rechnung/$',
        'pyrm.e-rechnung.index',
        name="pyrm-e-rechnung"
    ),
    url(
        r'^e-rechnung/specify/(?P<file_path>.+?)$',
        'pyrm.e-rechnung.specify_file',
        name="pyrm-e-rechnung_specify"
    ),
    url(
        r'^e-rechnung/download/(?P<file_path>.+?)$',
        'pyrm.e-rechnung.download',
        name="pyrm-e-rechnung_download"
    ),

    #__________________________________________________________________________
    # Rechnungen Kontieren

    url(
        r'^kontieren/$', 'pyrm.kontieren.index',
        name="pyrm-kontieren"
    ),
    url(
        r'^kontieren/(?P<start>.+?)-(?P<end>.+?)/$',
        'pyrm.kontieren.kontieren',
        name="pyrm-kontieren-kontieren"
    ),

    #__________________________________________________________________________
    # OTHER VIEWS
    url(
        r'^import_menu/$', 'pyrm.importer.menu.menu',
        name="pyrm-import-menu"
    ),
    url(
        r'^setup/$', 'pyrm.index.setup',
        name="pyrm-setup"
    ),
    url(
        r'^$', 'pyrm.index.menu',
        name="pyrm-main-menu"
    ),
)

