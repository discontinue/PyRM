# coding: utf-8
"""
    pyrm - Basis Models
    ~~~~~~~~~~~~~~~~~~~

    Basis Model Klassen.

    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.db import models

from django_tools.models import UpdateInfoBaseModel

#from pyrm.utils.django_modeladmin import add_missing_fields



#______________________________________________________________________________

class BaseModel(UpdateInfoBaseModel):
    """
    Grundmodell für fast alle Klassen.
    """
    notizen = models.TextField(blank=True, null=False)

    class Meta:
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes


BASE_FIELDSET = ('Metadaten', {
#    'classes': ('collapse',),
    'fields': (
        "createtime", "lastupdatetime",
        "createby", "lastupdateby",
        "notizen",
    )
})

#______________________________________________________________________________


