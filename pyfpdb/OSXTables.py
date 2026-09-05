#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""XWindows specific methods for TableWindows Class.
"""
#    Copyright 2008 - 2011, Ray E. Barker

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

########################################################################

import L10n
_ = L10n.get_translation()

#    Standard Library modules
import re
import os

#    pyGTK modules
import gtk

#    Other Library modules
QUARTZ_AVAILABLE = True
try:
    from Quartz.CoreGraphics import *
except ImportError:
    try:
        from Quartz import *
    except ImportError:
        QUARTZ_AVAILABLE = False

#    FPDB modules
from TableWindow import Table_Window

class Table(Table_Window):

    def get_window_list(self):
        """Retrieve the current Quartz CGWindowList description array."""
        if not QUARTZ_AVAILABLE:
            return []

        try:
            options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
            win_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            if win_list:
                return win_list
        except Exception:
            pass

        try:
            win_list = CGWindowListCreate(0, 0)
            return CGWindowListCreateDescriptionFromArray(win_list)
        except Exception:
            return []

    def find_table_parameters(self):

#    This is called by __init__(). Find the poker table window of interest,
#    given the self.search_string. Then populate self.number, self.title, 
#    self.window, and self.parent (if required).

        self.number = None
        win_list_dict = self.get_window_list()

        for d in win_list_dict:
            window_name = d.get(kCGWindowName, "") or d.get("kCGWindowName", "")
            if not window_name:
                continue
            if re.search(self.search_string, window_name, re.I):
                title = window_name
                if self.check_bad_words(title): continue
                self.number = int(d.get(kCGWindowNumber, d.get("kCGWindowNumber", 0)))
                self.title = title
                return self.title
        if self.number is None:
            return None
  
    def get_geometry(self):

        win_list_dict = self.get_window_list()

        for d in win_list_dict:
            wnum = d.get(kCGWindowNumber, d.get("kCGWindowNumber", None))
            if wnum == self.number:
                bounds = d.get(kCGWindowBounds, d.get("kCGWindowBounds", {}))
                return {'x'      : int(bounds.get('X', 0)),
                        'y'      : int(bounds.get('Y', 0)),
                        'width'  : int(bounds.get('Width', 0)),
                        'height' : int(bounds.get('Height', 0))
                       }
        return None

    def get_window_title(self):
        win_list_dict = self.get_window_list()

        for d in win_list_dict:
            wnum = d.get(kCGWindowNumber, d.get("kCGWindowNumber", None))
            if wnum == self.number:
                return d.get(kCGWindowName, d.get("kCGWindowName", None))
        return None

    def topify(self, window):
#    The idea here is to call set_transient_for on the HUD window, with the table window
#    as the argument. This should keep the HUD window on top of the table window, as if 
#    the hud window was a dialog belonging to the table.

#    This is the gdkhandle for the HUD window
        gdkwindow = gtk.gdk.window_foreign_new(window.window.xid)
        gdkwindow.set_transient_for(window.window)
