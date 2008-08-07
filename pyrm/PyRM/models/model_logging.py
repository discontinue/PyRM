# -*- coding: utf-8 -*-
"""
    PyRM - Logging
    ~~~~~~~~~~~~~~

    -Basis logging model klasse.
    -loging signal handler

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from pprint import pformat
from datetime import datetime

from django.db import models
from django.contrib import admin
from django.db.models import signals
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from PyRM.middleware import threadlocals


class ModelLogManager(models.Manager):
    def log(self, **kwargs):
        e = self.model(**kwargs)
        e.save()

    def get_for_object(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=ct.pk, object_pk=obj.pk)


class ModelLog(models.Model):
    """
    A single revision for an object.
    """
    objects = ModelLogManager()

    object_pk = models.PositiveIntegerField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey("object_pk", "content_type")
    created_at = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(
        User, #blank=True, null=True, #editable=False,
        help_text="Benutzer der diesen Eintrag zuletzt geändert hat.",
        related_name="%(class)s_geaendert_von"
    )
    log_messages = models.TextField(blank=True)
    diff_data = models.TextField(blank=True)

    def save(self):
        self.user = threadlocals.get_current_user()
        super(ModelLog,self).save()

    class Meta:
        app_label = "PyRM"
        ordering = ["-created_at"]

class ModelLogAdmin(admin.ModelAdmin):
    list_display = (
        "object_pk", "content_type", #"content_object",
        "created_at", "user", "log_messages"
    )
    list_display_links = ("object_pk", "content_type")
    list_filter = ("content_type", "user")

admin.site.register(ModelLog, ModelLogAdmin)

#______________________________________________________________________________


class BaseLogModel(models.Model):
    def __init__(self, *args, **kwargs):
        self._old_data = None
        self._log_message = []
        super(BaseLogModel, self).__init__(*args, **kwargs)

    def set_old_data(self, data):
        self._old_data = data

    def get_old_data(self):
        return self._old_data

    def add_log_message(self, message):
        self._log_message.append(message)

    def get_and_delete_log_messages(self):
        if self._log_message == []:
            return "---"
        messages = "\n".join(self._log_message)
        self._log_message = []
        return messages

    class Meta:
        app_label = "PyRM"
        # http://www.djangoproject.com/documentation/model-api/#abstract-base-classes
        abstract = True # Abstract base classes

#______________________________________________________________________________


def _get_model_data(instance):
    """
    Returns a dict with all model fields (key, value)
    """
    data = {}
    for field in instance._meta.fields:
        data[field.name] = getattr(instance, field.name)
    return data


def model_logging_init(instance, **kwargs):
    """
    Save the current model data into the model.
    """
    data = _get_model_data(instance)
    instance.set_old_data(data)


def model_logging_save(instance, **kwargs):
    """
    Add a new ModelLog entry with the model-data-diff
    """
    old_data = instance.get_old_data()
    data = _get_model_data(instance)

    diff_data = {}
    for key, value in data.iteritems():
        if old_data[key] != value:
            diff_data[key] = old_data[key]

    ModelLog.objects.log(
        object_pk    = instance.pk,
        content_type = ContentType.objects.get_for_model(kwargs["sender"]),
        log_messages = instance.get_and_delete_log_messages(),
        diff_data    = pformat(diff_data),
    )



