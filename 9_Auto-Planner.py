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
from pyrevit import forms, script
from collections import defaultdict
import datetime


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

rvt_year = int(app.VersionNumber)
active_view = doc.ActiveView
view_fam_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewTypeFloorPlan)
output = script.get_output()


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

if not all_rooms:
    forms.alert('No apartments found.', exitscript=True)

# Sort rooms into collectives (all of one flat in one list)
for room in all_rooms:
    try:
        building = room.LookupParameter('Building').AsString()
        flat = room.LookupParameter('Flat').AsString()
    except:
        forms.alert("Mising Room Parameter ['Building', 'Flat'].", exitscript=True)

    if flat:
        key = "{}_{}".format(building, flat)
        dict_flats[key].append(room)


## ALLOW CHANGES IN REVIT
t = Transaction(doc, __title__)
t.Start()  


table_data = []

# Create room dict of room info
for room in dict_flats:
    list_rooms  = dict_flats[room]
    offset_ft   = UnitUtils.ConvertToInternalUnits(30, UnitTypeId.Centimeters)

    # Create new view    
    new_view    = ViewPlan.Create(doc, view_fam_type_id, list_rooms[0].LevelId)
    room_bb     = bb_from_multiple(list_rooms, new_view)
    new_view.CropBox = room_bb
    new_view.CropBoxActive = True
    new_view.CropBoxVisible = True

    # If basic room name is taken as view name, try with the date
    try:
        new_view.Name = room
    except:
        new_view.Name = room + datetime.datetime.now().strftime(" (%Y%m%d-%H%M)")

    # 
    # link_rooms = output.linkify(room.Id, "Select {} Rooms".format(len(room.Id)))
    link_view  = output.linkify(new_view.Id, new_view.Name)

    # Get room area, append
    total_m2 = 0
    for room in list_rooms:
        m2 = UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters)
        m2 = round(m2,2)
        total_m2 += m2

    data_row = [link_view, total_m2]
    table_data.append(data_row)

t.Commit()
## END CHANGES IN REVIT


# Print report
output.print_table(table_data=table_data,
                    title="Auto-Planner Report",
                    columns=['Apartment', 'Total Area m²'],
                    formats=['**{}**', '{}m²'])
