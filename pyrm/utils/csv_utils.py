#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Some shared CSV utils.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import sys, os, csv


def get_csv_tables(filename):
    f = file(filename, "r")
    data = f.readlines()
    f.close()

    tables = {}
    table_no = 0

    for line in data:
        line = line.strip()
        if line.startswith(":") or line == "":
            continue

        if line.startswith("***"):
            table_no += 1
            tables[table_no] = []
            continue

        line = line.decode("latin-1").encode("utf-8")

        tables[table_no].append(line)

    tables = tables.values()
    return tables

CSV_READER_KWARGS = {
    "delimiter": ";",
    "skipinitialspace": True,
}

def get_all_fieldnames(table_data):
    fieldnames = csv.reader(table_data, **CSV_READER_KWARGS).next()
    return fieldnames

def get_dictlist(table_data, used_fieldnames=None):
    """
    used_fieldnames = A list of used fieldnames. If definied: Filter the fields.
    """
    dictlist = []
    reader = csv.DictReader(table_data, **CSV_READER_KWARGS)
    for fields in reader:
        if used_fieldnames:
            result = {}
            for fieldname in used_fieldnames:
                result[fieldname] = fields[fieldname]
            fields = result

        dictlist.append(fields)

    # First item is all keys
    return dictlist[1:]


def convert(data, mapping):
    """
    >>> data = [{"a":"1", "b":"foo"}, {"a":2, "b":"bar"}]
    >>> convert(data, mapping={"a":("x", int), "b":("y", None)})
    [{'y': 'foo', 'x': 1}, {'y': 'bar', 'x': 2}]
    """
    result = []
    for line in data:
        new_line = {}
        for key, value in line.iteritems():
            if not key in mapping:
                continue

            new_key, map_func = mapping[key]
            if map_func:
                value = map_func(value)

            new_line[new_key] = value

        result.append(new_line)

    return result



if __name__ == "__main__":
    print "start DocTest..."
    import doctest
    doctest.testmod()#verbose=True)
    print "DocTest end."