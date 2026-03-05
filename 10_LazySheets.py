# -*- coding: utf-8 -*-
__title__   = "Lazy Sheets"
__doc__     = """v1.0 | 04.03.2026 | JTH

DESCRIPTION:
- Exercise 10 of EF 21-Day Pyrevit Challenge
- Place unplaced views on sheets!
"""


# IMPORTS ------------------------------------------------------

from hmac import new

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List
from System import Int64

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script
from collections import defaultdict


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

rvt_year = int(app.VersionNumber)
active_view = doc.ActiveView
output = script.get_output()

all_viewports   = FilteredElementCollector(doc).OfClass(Viewport).ToElements()
placed_view_ids = [vp.ViewId for vp in all_viewports]

random_sheet_id = FilteredElementCollector(doc).OfClass(ViewSheet).FirstElementId()

# FUNCTIONS ----------------------------------------------------

def is_unplaced(view):
    if not Viewport.CanAddViewToSheet(doc, random_sheet_id, view.Id):
        return False
    if view.Id not in placed_view_ids and not view.IsTemplate:
        return True


# MAIN ---------------------------------------------------------

# Alerts if no viewports or sheets are found in the project
forms.alert_ifnot(all_viewports or placed_view_ids, 'No Sheets/Viewports found in project! :o', exitscript=True)

# Select views, select titleblock
views = forms.select_views(title='Select Views to Place:', filterfunc=is_unplaced)
forms.alert_ifnot(views, 'No Views selected. Try again', exitscript=True)

tb_id = forms.select_titleblocks()
forms.alert_ifnot(tb_id, 'No Titleblock selected. Try again', exitscript=True)


## ALLOW CHANGES IN REVIT
t = Transaction(doc, __title__)
t.Start()  

# 
table_data = []
tb = None

with forms.ProgressBar(cancellable=True) as pb:
    n_views = len(views)
    for n, view in enumerate(views):
        new_sheet = ViewSheet.Create(doc, tb_id)
        
        sheet_name = '{} - {}'.format(new_sheet.SheetNumber, view.Name)
        link_sheet = output.linkify(new_sheet.Id, sheet_name)
        table_data.append([link_sheet])

        # Gets titleblock centroid in first loop, stays defined for subsequent loops
        if not tb:
            tb = FilteredElementCollector(doc, new_sheet.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().FirstElement()
            bb = tb.BoundingBox[new_sheet]
            centroid = (bb.Min + bb.Max)/2
        
        new_viewport = Viewport.Create(doc, new_sheet.Id, view.Id, centroid)

        if pb.cancelled:
            t.RollBack()
            forms.alert("Cancelled. No Changes Made.", exitscript=True)
            break
        else:
            pb.update_progress(n, n_views)

t.Commit()
## END CHANGES IN REVIT


output.print_table(table_data=table_data, columns=['Sheet'], title='Sheets Created')
