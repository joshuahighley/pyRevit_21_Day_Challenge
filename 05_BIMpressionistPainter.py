# -*- coding: utf-8 -*-
__title__   = "BIMpressionist Painter"
__doc__     = """v1.0 | 19.02.2026 | JTH

DESCRIPTION:
- Exercise 5 of EF 21-Day Pyrevit Challenge
- Paint objects by parameter value
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script

from collections import defaultdict
import random


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document
output = script.get_output()
active_view = doc.ActiveView

# Patterns & Colors
all_patterns  = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
solid_pattern = [i for i in all_patterns if i.GetFillPattern().IsSolidFill][0]

pastel_colors = [
    Color(244, 204, 204),  # soft pink
    Color(252, 229, 205),  # peach
    Color(255, 242, 204),  # light cream
    Color(217, 234, 211),  # pale green
    Color(208, 224, 227),  # soft cyan
    Color(201, 218, 248),  # light blue
    Color(207, 226, 243),  # sky pastel
    Color(234, 209, 220),  # dusty rose
    Color(221, 217, 195),  # warm gray
    Color(242, 220, 219),  # blush
    Color(255, 230, 153),  # soft yellow
    Color(182, 215, 168),  # muted green
    Color(162, 196, 201),  # grayish teal
    Color(164, 194, 244),  # muted blue
    Color(213, 166, 189),  # mauve
    Color(199, 178, 153),  # beige
    Color(180, 167, 214),  # lavender
    Color(234, 153, 153),  # medium pastel red
    Color(249, 203, 156),  # soft apricot
    Color(255, 229, 153),  # mellow yellow
    Color(147, 196, 125),  # medium green
    Color(118, 165, 175),  # muted turquoise
    Color(109, 158, 235),  # soft medium blue
    Color(194, 123, 160),  # dusty magenta
    Color(166, 166, 166),  # neutral gray
    Color(220, 180, 170),  # clay pastel
    Color(255, 204, 188),  # soft coral
    Color(255, 236, 179),  # pale sand
    Color(209, 231, 221),  # mint pastel
    Color(203, 225, 252),  # airy blue
    Color(215, 210, 233),  # light violet gray
    Color(240, 215, 218),  # rose mist
    Color(227, 242, 253),  # ice blue
    Color(232, 245, 233),  # pale mint
    Color(255, 249, 196),  # light lemon
    Color(225, 190, 231),  # pastel purple
    Color(197, 225, 165),  # soft lime
    Color(255, 224, 178),  # warm peach
    Color(176, 190, 197),  # cool gray blue
    Color(255, 213, 79),   # muted amber
    Color(129, 199, 132),  # soft medium green
    Color(79, 195, 247),   # gentle blue
    Color(244, 143, 177),  # pastel pink
    Color(255, 171, 145),  # salmon pastel
    Color(224, 224, 224),  # light gray
    Color(178, 223, 219),  # pastel aqua
    Color(200, 230, 201),  # soft sage
    Color(255, 204, 128),  # muted orange
    Color(189, 189, 189),  # medium light gray
    Color(210, 180, 140)   # tan pastel
]


# MAIN ---------------------------------------------------------

cat = BuiltInCategory.OST_Walls
elements = FilteredElementCollector(doc, active_view.Id)
walls_in_view = FilteredElementCollector(doc, active_view.Id).OfClass(Wall).ToElements()

dict_values = defaultdict(list)

for wall in walls_in_view:
    wall_type_name = wall.Name
    dict_values[wall_type_name].append(wall)

# Error check - no walls??
if not dict_values:
    forms.alert('No elements matching criteria were found in active view.', exitscript=True)

# Match the length of pastel_colors list to dict_values list
while len(pastel_colors) < len(dict_values):
    pastel_colors += pastel_colors

if len(pastel_colors) > len(dict_values):
    pastel_colors = pastel_colors[:len(dict_values)]


## ALLOW CHANGES IN REVIT --------------------------------------
t = Transaction(doc, __title__)
t.Start()  

table_data = []
count = 0

for key, elems in dict_values.items():
    color = pastel_colors[count]
    count += 1
    r, g, b = color.Red, color.Green, color.Blue

    override_settings = OverrideGraphicSettings()
    
    # Surface Overrides
    override_settings.SetSurfaceForegroundPatternId(solid_pattern.Id)
    override_settings.SetSurfaceForegroundPatternColor(color)
    
    # Cut Overrides
    override_settings.SetCutForegroundPatternId(solid_pattern.Id)
    override_settings.SetCutForegroundPatternColor(color)

    for el in elems:
        active_view.SetElementOverrides(el.Id, override_settings)

    swatch = '<div style="width:60px;height:25px;border:1px solid #999;border-radius:3px;background:rgb({0},{1},{2});"></div>'.format(r,g,b)

    ids = [w.Id for w in elems]
    select_link = output.linkify(ids, title='Select All')

    table_data.append([swatch, key, len(elems), select_link])

t.Commit()
## END CHANGES IN REVIT


# Print legend report
output.print_md("**Element Overrides Legend** (View: {})".format(active_view.Name))
output.print_table(table_data=table_data, columns=['Color', 'Name', 'Amount', 'Select All'])
