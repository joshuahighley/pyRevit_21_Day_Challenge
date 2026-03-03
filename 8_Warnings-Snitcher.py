# -*- coding: utf-8 -*-
__title__   = "Warnings Snitcher"
__doc__     = """v1.0 | 27.02.2026 | JTH

DESCRIPTION:
- Exercise 8 of EF 21-Day Pyrevit Challenge
- 
"""


# IMPORTS ------------------------------------------------------

from email.policy import default
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
warnings = doc.GetWarnings()
all_warnings = defaultdict(list)

# Sort warnings by desc
sorted_warnings = defaultdict(list)
for w in sorted_warnings:
    description = w.GetDescriptionText()
    sorted_warnings[description].append(w)



# Select warning types


for w in warnings:
    desc = w.GetDescriptionText()

    fail_elem_ids = w.GetFailingElements()
    add_elem_ids = w.GetAdditionalElements()

    elem_ids = list(fail_elem_ids) + list(add_elem_ids)
    elems = [doc.GetElement(e_id) for e_id in elem_ids]

    all_warnings[desc].append(w)
    
    link = output.linkify(elem_ids)

    print('\n' + desc)
    print(link)
    print('-'*30)



# items = ['one', 'two', 'three']
# sel_warm_types = forms.SelectFromList.show(items, button_name='Select Item', multiselect=True)

