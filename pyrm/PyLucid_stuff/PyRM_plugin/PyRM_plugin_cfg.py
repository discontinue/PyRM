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
    "must_login"    : True,
    "must_admin"    : True,
}

plugin_manager_data = {
    "summary" : global_rights,
#    "summary" : {"must_login":False, "must_admin":False},
    "customers" : global_rights,
    "bills" : global_rights,
    "bill_detail" : global_rights,
    "create_bill" : global_rights,

    "install": {
        "must_login"    : True,
        "must_admin"    : True,
        "admin_sub_menu": {
            "section"       : "PyRM", # The sub menu section
            "title"         : "Erstelle alle PyRM CMS Seiten",
            "help_text"     : "WARNUNG: Alle Seiten gleichen namens werden gelöscht",
            "open_in_window": False, # Should be create a new JavaScript window?
            "weight" : -5, # sorting weight for every section entry
        },
    }
}