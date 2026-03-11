# -*- coding: utf-8 -*-
__title__   = "Flat Summarizer"
__doc__     = """v1.0 | 19.02.2026 | JTH

DESCRIPTION:
- Exercise 4 of EF 21-Day Pyrevit Challenge
- 
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms
from collections import defaultdict


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document



# FUNCTIONS ----------------------------------------------------



# MAIN ---------------------------------------------------------

# Collect rooms
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
dict_flats = defaultdict(list)

# Create room dict of room info
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
t = Transaction(doc, 'Flat Summarizer')
t.Start()  

for key, room_list in dict_flats.items():
    sum_m2_balc = 0.0
    sum_m2_living = 0.0
    room_ct = 0

    #calc sums
    for room in room_list:
        occ = room.get_Parameter(BuiltInParameter.ROOM_OCCUPANCY).AsString().lower()
        if not occ:
            link_room = output.linkify(room.Id)
            print('Room is missing Occupancy parameter. Please verify room: ' + link_room)
            continue
        
        area_m2 = UnitUtils.ConvertFromInternalUnits(room.Area, UnitTypeId.SquareMeters)
        area_m2 = round(area_m2, 2)

        if occ == 'balcony':
            sum_m2_balc += area_m2
        elif occ == 'living':
            sum_m2_living += area_m2
        
        room_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString().lower()
        if 'living' in room_name or 'bed' in room_name:
            room_ct += 1

    # Convert sums to internal units
    sum_ft2_balc = UnitUtils.ConvertToInternalUnits(sum_m2_balc, UnitTypeId.SquareMeters)
    sum_ft2_living = UnitUtils.ConvertToInternalUnits(sum_m2_living, UnitTypeId.SquareMeters)

    for room in room_list:
        # read
        p_out_balc = room.LookupParameter('[Sum m²] - Balcony')
        p_out_living = room.LookupParameter('[Sum m²] - Living')
        p_out_count = room.LookupParameter('RoomCount')

        # write
        p_out_living.Set(sum_ft2_living)
        p_out_balc.Set(sum_ft2_balc)
        p_out_count.Set(str(room_ct))

t.Commit()
## END CHANGES IN REVIT
