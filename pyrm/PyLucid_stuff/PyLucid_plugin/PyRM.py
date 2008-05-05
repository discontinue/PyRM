# -*- coding: utf-8 -*-
"""
    PyRM - PyLucid plugin
    ~~~~~~~~~~~~~~~~~~~~~

    http://sourceforge.net/projects/pyrm/

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__version__= "$Rev: $"

from django.utils.translation import ugettext as _

from PyLucid.system.BasePlugin import PyLucidBasePlugin

class PyRM(PyLucidBasePlugin):

    def summary(self):
        """
        """
        # Change the global page title:
        self.context["PAGE"].title = _("PyRM - summary")

        self.page_msg("summary")
















