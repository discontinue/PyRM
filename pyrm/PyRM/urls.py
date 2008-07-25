from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/(.*)' % settings.ADMIN_URL_PREFIX, admin.site.root),
)
