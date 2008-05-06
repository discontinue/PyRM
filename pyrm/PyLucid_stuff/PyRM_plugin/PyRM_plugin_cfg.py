# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Jens Diemer"
__url__         = "http://sourceforge.net/projects/pyrm/"
__description__ = "Rechnungmanager"
__long_description__ = """
"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : False,
    "must_admin"    : False,
}

plugin_manager_data = {
    "summary" : global_rights,
    "customers" : global_rights,
    "bills" : global_rights,
    "bill_detail" : global_rights,
    "create_bill" : global_rights,
}