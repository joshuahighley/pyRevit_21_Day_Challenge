# -*- coding: utf-8 -*-
__title__   = "Dream Picker"
__doc__     = """v1.0 | 05.03.2026 | JTH

DESCRIPTION:
- Exercise 11 of EF 21-Day Pyrevit Challenge
- Allows user to rectangle select multiple instances of the initially selected object and nothing else.
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ISelectionFilter
from pyrevit import forms, revit


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# CLASSES -----------------------------------------------------

class type_id_filter(ISelectionFilter):
    def AllowElement(self, element):
        if element.GetTypeId() == sel_el_type_id:
            return True


# MAIN ---------------------------------------------------------

# Get selected elements from their Ids. If nothing selected, ValueError alert form
try:
    sel_el_ids  = uidoc.Selection.GetElementIds()
    sel_el = doc.GetElement(sel_el_ids[0])
    sel_el_type_id = sel_el.GetTypeId()
except ValueError:
    forms.alert(msg="Nothing Selected. Try again.", 
                title='Value Error', 
                sub_msg='Probably. But if you are confident you selected something contact your local pyRevit person.',
                exitscript=True)

# Create a note that tells the user they selected multiple things, but it's only filtering for the first
mult_note = ""
if len(sel_el_ids) > 1:
    mult_note = " (the first item in your selection of {} things.".format(len(sel_el_ids))

# Try to drag select other elements matching first's Type Id
objs = []
try:
    with forms.WarningBar(title='Drag to select multiple instances of: ' + sel_el.Name + mult_note):
        objs = revit.pick_rectangle(type_id_filter())
except AttributeError:
    forms.alert(msg="Wrong thing selected. Try again.", 
                title='Attribute Error', 
                sub_msg='This script filters by TypeId, so this thing must not have one. Rooms are a common culprit.',
                exitscript=True)
except Exception:
    raise SystemExit    # Ends the script if the user hits escape

# Set the Revit UI selection to the drag selection results
list_el_ids = List[ElementId]([el.Id for el in objs])
uidoc.Selection.SetElementIds(list_el_ids)

# If the drag select results are less than 1 element, let the user know
if len(list_el_ids) < 1:
    forms.alert(msg="Nothing Selected. Try again.", 
                title='Selection Results', 
                sub_msg='Probably. But if you are confident you selected something contact your local pyRevit person.',
                exitscript=True)
