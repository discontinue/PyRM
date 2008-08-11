# -*- coding: utf-8 -*-
"""
    django ModelAdmin utils
    ~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
from pprint import pprint

from django.core.exceptions import ImproperlyConfigured

def add_missing_fields(model_class, fieldsets,
                    ignore_fields=set(("id",)), field_name = "missing fields"):
    """
    Util for adding all missing fields in a admin.ModelAdmin.fieldsets
    """
    # Get all existing and editable fields
    existing_fields = set()
    for field in model_class._meta.fields:
        if field.editable == True:
            existing_fields.add(field.name)

    # Make a set of all used fieldnames in the given fieldsets
    used_fields = set()
    for section, field_dict in fieldsets:
        used_fields.update(set(field_dict["fields"]))

    # Make a set of all fields that are not in the given fieldsets
    missing_fields = existing_fields.difference(used_fields)
    missing_fields.difference_update(ignore_fields)

    if not missing_fields:
        # No field was missing
        return fieldsets

    # Add the missing fields into the section 'field_name'
    new_fieldset = list(fieldsets)
    new_fieldset.append(
        (field_name, {"fields": tuple(missing_fields)})
    )

    return new_fieldset
