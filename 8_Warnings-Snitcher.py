# -*- coding: utf-8 -*-
__title__   = "Warnings Snitcher"
__doc__     = """v1.0 | 27.02.2026 | JTH

DESCRIPTION:
- Exercise 8 of EF 21-Day Pyrevit Challenge
- 
"""


# IMPORTS ------------------------------------------------------

from ctypes import cast
from pydoc import describe

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script

from collections import defaultdict

# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

output = script.get_output()

# FUNCTIONS ----------------------------------------------------



# MAIN ---------------------------------------------------------

# Collect all warnings
all_warnings = doc.GetWarnings()

# Sort warnings by desc
sorted_warnings = defaultdict(list)

for w in all_warnings:
    description = w.GetDescriptionText()
    sorted_warnings[description].append(w)

if not sorted_warnings:
    forms.alert('No warnings? Nice!! :)',  exitscript=True)

# Select warning types
sel_warning_names = forms.SelectFromList.show(sorted_warnings.keys(),
                                              button_name='Select',
                                              multiselect=True,
                                              title='Select Warning Types')
if not sel_warning_names:
    forms.alert('No Warning Types selected. Try again.')
    sel_warning_names = forms.SelectFromList.show(sorted_warnings.keys(),
                                              button_name='Select',
                                              multiselect=True,
                                              title='Select Warning Types')
if not sel_warning_names:
    forms.alert('No Warning Types selected. Try running the tool again.',  exitscript=True)


table_data = []

for w_description, list_w in sorted_warnings.items():
    if w_description not in sel_warning_names:
        continue

    for w in list_w:
        data = []

        fail_elem_ids   = w.GetFailingElements()
        add_elem_ids    = w.GetAdditionalElements()
        w_elem_ids      = list(fail_elem_ids) + list(add_elem_ids)
        w_elem          = [doc.GetElement(elem_id) for elem_id in w_elem_ids]

        cats            = {elem.Category.Name for elem in w_elem}
        cats            = ','.join(cats)

        levels = []
        for elem in w_elem:
            if elem.LevelId and elem.LevelId != ElementId.InvalidElementId:
                lvl = doc.GetElement(elem.LevelId)
                levels.append(lvl.Name)
        levels = (','.join(levels))

    link = output.linkify(w_elem_ids)

    data = [w_description[:40]+'...', link, len(w_elem_ids), cats, levels]
    table_data.append(data)

output.print_table(
    table_data=table_data,
    title = 'Warnings Report',
    columns = ['Warning Type','Select','Amount','Categories','Levels']
)
