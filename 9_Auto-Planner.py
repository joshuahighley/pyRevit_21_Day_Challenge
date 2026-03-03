# -*- coding: utf-8 -*-
__title__   = "Auto-Planner"
__doc__     = """v1.0 | 02.03.2026 | JTH

DESCRIPTION:
- Exercise 9 of EF 21-Day Pyrevit Challenge
- 
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
from pyrevit import forms
from collections import defaultdict
import datetime


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

rvt_year = int(app.VersionNumber)
active_view = doc.ActiveView
view_fam_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeFloorPlan)


# FUNCTIONS ----------------------------------------------------

# Checks Revit version year, gives proper integer type (64 for R26)
def get_el_by_int_id(id_int):
    if rvt_year >2025:
        elem_id = ElementId(Int64(int_id))
    else:
        elem_id = ElementId(id_int)
    return doc.GetElement(elem_id)

# Creates a bounding box for multiple rooms
def bb_from_multiple(list_rooms, new_view):
    bb_min  = [1000000,  1000000,  0]
    bb_max  = [-1000000, -1000000, 0]

    list_bb = [room.BoundingBox[new_view] for room in list_rooms]
    for bb in list_bb:
        if bb.Min.X < bb_min[0]:    bb_min[0] = bb.Min.X
        if bb.Min.Y < bb_min[1]:    bb_min[1] = bb.Min.Y
        if bb.Max.X > bb_max[0]:    bb_max[0] = bb.Max.X
        if bb.Max.Y > bb_max[1]:    bb_max[1] = bb.Max.Y

    new_bb = BoundingBoxXYZ()
    new_bb.Min = XYZ(bb_min[0] - offset_ft, bb_min[1] - offset_ft, 0)
    new_bb.Max = XYZ(bb_max[0] + offset_ft, bb_max[1] + offset_ft, 0)

    return new_bb


# MAIN ---------------------------------------------------------

# Collect rooms
dict_flats = defaultdict(list)
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()

# Sort rooms into collectives (all of one flat in one list)
for room in all_rooms:
    try:
        building = room.LookupParameter('Building').AsString()
        flat = room.LookupParameter('Flat').AsString()
        #occ = room.get_Parameter(BuiltInParameter.ROOM_OCCUPANCY).AsString()
    except:
        forms.alert("Mising Room Parameter ['Building', 'Flat'].", exitscript=True)

    if flat:
        key = "{}_{}".format(building, flat)
        dict_flats[key].append(room)


## ALLOW CHANGES IN REVIT
t = Transaction(doc, __title__)
t.Start()  

ct = 0
# Create room dict of room info
for room in dict_flats:
    list_rooms = dict_flats[room]
    offset_ft = UnitUtils.ConvertToInternalUnits(20, UnitTypeId.Centimeters)
    view_bb     = BoundingBoxXYZ()

    view_bb = bb_from_multiple(list_rooms, active_view)

    # Create new view    
    new_view = ViewPlan.Create(doc, view_fam_type_id, list_rooms[0].LevelId)
    room_bb = bb_from_multiple(list_rooms, new_view)
    new_view.CropBoxActive = True
    new_view.CropBoxVisible = True
    new_view.DetailLevel = ViewDetailLevel.Fine
    new_view.CropBox = view_bb

    ct += 1
    try:
        new_view.Name = room + str(ct)
    except:
        new_view.Name = 'test_' + str(ct) + datetime.datetime.now().strftime(" (%Y%m%d-%H%M)")

t.Commit()
## END CHANGES IN REVIT
