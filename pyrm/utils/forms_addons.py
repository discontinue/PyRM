
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

if __name__ == "__main__":
    import doctest, datetime
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."