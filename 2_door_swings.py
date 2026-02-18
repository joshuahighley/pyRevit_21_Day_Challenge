# -*- coding: utf-8 -*-
__title__   = "Door Swing Detective"
__doc__     = """v1.0 | 17.02.2026 | JTH

DESCRIPTION:
- Exercise 2 of EF 21-Day Pyrevit Challenge
- Find mirrored door families

HOW-TO:
1. 

TODO:
[FEATURE] - 

Last Updates:
- [17.02.2026] Started the process!
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

mir_param = 'IsMirrored'    #Project parameter to indicate if door (or in the future window) is mirrored
cat = BuiltInCategory.OST_Doors


# FUNCTIONS ----------------------------------------------------


# MAIN ---------------------------------------------------------

# 1. Get All Doors
all_doors = FilteredElementCollector(doc).OfCategory(cat).WhereElementIsNotElementType().ToElements()

# 2. Find Swing Direction
t = Transaction(doc, 'Door Swing')

## ALLOW CHANGES IN REVIT
t.Start()

for door in all_doors:
    val = 'Mirrored' if door.Mirrored else 'Unmirrored'
    param = door.LookupParameter(mir_param)
    mark = door.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)

    try:
        param.Set(val)
        print('Door #{}: {}'.format(mark.AsValueString(), val))
    except(AttributeError):
        forms.alert(mir_param + ' parameter not found in project.', exitscript=True)

t.Commit()
## END CHANGES IN REVIT
