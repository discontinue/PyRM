#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Install PyRM into PyLucid via symlink.

You can use delete_symlinks() to remove the links, look at the bottom.

You must change the path to PyLucid!
"""

import os, shutil

# Please setup this path:
PYLUCID_PATH = "~/workspace/PyLucid_trunk/pylucid"


LINK_FILES = ("standalone_PyRM_linux.sh", "PyRM_PyLucid_setup.py")


class Path(object):
    def __init__(self, pylucid_path):
        self.own = os.getcwd()
        print "PyRM dir '%s'" % self.own
        self.pyrm_pylucid = os.path.join(self.own, "PyLucid_stuff")

        self.pylucid_base = os.path.expanduser(pylucid_path)
        self.check()
        print "PyLucid dir '%s'." % self.pylucid_base

        self.pylucid_app = self.PyLucid_path("PyRM")
        self.pylucid_plugin = self.PyLucid_path(
            "PyLucid", "plugins_external", "PyRM_plugin"
        )
        self.pylucid_ipage = self.PyLucid_path(
            "media", "PyLucid", "internal_page", "PyRM_plugin"
        )

    def check(self):
        if not os.path.isdir(os.path.join(self.pylucid_base, "PyLucid")):
            msg = (
                "The path '%s' seems to be wrong! Please change PYLUCID_PATH."
            ) % self.base
            raise WrongPath(msg)

    #__________________________________________________________________________
    # BUILD PATHS

    def PyRM_path(self, *parts):
        """
        .../PyRM/*
        """
        return os.path.join(self.own, *parts)

    def PyRM_PyLucid_path(self, *parts):
        """
        .../PyRM/PyLucid_stuff/*
        """
        return os.path.join(self.pyrm_pylucid, *parts)

    def PyLucid_path(self, *parts):
        """
        .../pylucid/*
        """
        return os.path.join(self.pylucid_base, *parts)

#------------------------------------------------------------------------------

def delete_all(path):
    def unlink(path):
        print "unlink:"
        print path
        try:
            os.unlink(path)
        except OSError, e:
            print ">>> Error:", e
        print

    unlink(path.pylucid_app)
    unlink(path.pylucid_plugin)
    unlink(path.pylucid_ipage)
    unlink(path.PyLucid_path("PyRM_settings.py"))
    for filename in LINK_FILES:
        unlink(path.PyLucid_path(filename))


def create_all(path):
    def link(method, src, dst):
        print "link:"
        print "src:", src
        print "dst:", dst
        try:
            method(src, dst)
        except OSError, e:
            print ">>> Error:", e
        print

    link(os.symlink, path.PyRM_path("PyRM"), path.pylucid_app)
    link(os.symlink, path.PyRM_PyLucid_path("PyRM_plugin"), path.pylucid_plugin)
    link(os.symlink,
        path.PyRM_PyLucid_path("PyLucid_internal_page"), path.pylucid_ipage
    )

    for filename in LINK_FILES:
        link(os.link,
            path.PyRM_PyLucid_path(filename),
            path.PyLucid_path(filename)
        )

    link(os.link,
        path.PyRM_PyLucid_path("django_merged_settings.py"),
        path.PyLucid_path("PyRM_settings.py")
    )
    print
    print "NOTE: You should update the PyRM settings file!"

#------------------------------------------------------------------------------

def WrongPath(Exception):
    pass

#------------------------------------------------------------------------------

if __name__ == "__main__":
    path = Path(PYLUCID_PATH)
    print
    delete_all(path)
    create_all(path)

