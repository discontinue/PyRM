# -*- coding: utf-8 -*-

"""
    django forms addons
    ~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os

from django import forms

class QuarterChoiceField(forms.ChoiceField):
    """
    >>> start = datetime.date(2007, 1, 1)
    >>> end = datetime.date(2008, 12, 31)
    >>> t = QuarterChoiceField(epoch = (start, end))
    >>> t.choices
    [(1, 'I.2007'), (2, 'II.2007'), (3, 'III.2007'), (4, 'IV.2007'), \
(5, 'I.2008'), (6, 'II.2008'), (7, 'III.2008'), (8, 'IV.2008')]

    >>> t = QuarterChoiceField(epoch = (start, end), reverse=True)
    >>> t.choices
    [(1, 'IV.2008'), (2, 'III.2008'), (3, 'II.2008'), (4, 'I.2008'), \
(5, 'IV.2007'), (6, 'III.2007'), (7, 'II.2007'), (8, 'I.2007')]

    >>> t = QuarterChoiceField(epoch = (end, start))
    Traceback (most recent call last):
    ...
    AssertionError
    """
    def __init__(self, *args, **kwargs):
        """
        kwarg 'epoch' must be two datetime objects.
        """
        oldest, newest = kwargs.pop("epoch")
        reverse = kwargs.pop("reverse", False)
        super(QuarterChoiceField, self).__init__(*args, **kwargs)
        self.choices = self.build_choices(oldest, newest, reverse)

    def build_choices(self, oldest, newest, reverse):
        """
        FIXME: Nur die wirklichen Quartale sollten genommen werden und nicht
            alle des Jahres.        
        """
        assert(oldest<newest)

        time_range = range(oldest.year, newest.year+1)
        roman_range = ["I", "II", "III", "IV"]
        if reverse:
            time_range.reverse()
            roman_range.reverse()

        choices = []
        no = 0
        for year in time_range:
            for roman in roman_range:
                no += 1
                choices.append(
                    (no, "%s.%s" % (roman, year))
                )
        return choices


class ExtFileField(forms.FileField):
    """
    Same as forms.FileField, but you can specify a file extension whitelist.
    
    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ExtFileField, self).clean(*args, **kwargs)
        filename = data.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ext not in self.ext_whitelist:
            raise forms.ValidationError("Not allowed filetype!")

if __name__ == "__main__":
    import doctest, datetime
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."