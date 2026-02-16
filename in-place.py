# -*- coding: utf-8 -*-
__title__   = "In-Place Hunter"
__doc__     = """Version = 1.0

DATE
16.02.2026

DESCRIPTION:
- Exercise 1 of EF 21-Day Pyrevit Challenge
- Finds and lists in-place model elements.

HOW-TO:
1. Click button
2. Read report

TODO:
[FEATURE] - 

Last Updates:
- [16.02.2026] Started the process!

Author: JTH"""


# IMPORTS ----------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from pyrevit import script


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document


# FUNCTIONS ----------------------------------------------------

def get_in_place_elements():
    #Get all elements
    elements = FilteredElementCollector(doc).OfClass(FamilyInstance).ToElements()

    #Check if element is in-place
    inplace_elems = []

    for elem in elements:
        try:
            elem_type_id        = elem.GetTypeId()
            elem_type           = doc.GetElement(elem_type_id)
            elem_family         = elem_type.Family
            if elem_family.IsInPlace:
                inplace_elems.append(elem)
        except:
            pass

    return inplace_elems


# MAIN ----------------------------------------------------

in_place_elements = get_in_place_elements()

#Get pyRevit Output
output = script.get_output()

#Create Interactive Report
output.print_md('## In-Place Elements:')
output.print_md('---')

for elem in in_place_elements:
    cat_name = elem.Category.Name
    elem_info = "ID: " + str(elem.Id) + ", Category: " + cat_name
    link = output.linkify(elem.Id, elem_info)
    print(link)

print("{} In-Place Elements found.".format(len(in_place_elements)))
