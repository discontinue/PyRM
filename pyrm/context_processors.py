# coding: utf-8

from django.conf import settings


def pyrm(request):
    context = {
        "debug": settings.DEBUG,
        "media_url": settings.MEDIA_URL,
        "admin_url_prefix": settings.ADMIN_URL_PREFIX,
        "Django_media_prefix": settings.ADMIN_MEDIA_PREFIX,
    }
    return context
