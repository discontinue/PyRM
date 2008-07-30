# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),
    (r'^import/$', 'PyRM.KRB_csv_import_view.import_csv'),


    (r'^%s/(.*)' % settings.ADMIN_URL_PREFIX, admin.site.root),
)
