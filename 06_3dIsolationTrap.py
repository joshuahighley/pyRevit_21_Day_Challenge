# -*- coding: utf-8 -*-
__title__   = "3DIsolationTrap"
__doc__     = """v1.0 | 24.02.2026 | JTH

DESCRIPTION:
- Exercise 6 of EF 21-Day Pyrevit Challenge
- 
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr, datetime
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document
output = script.get_output()

view3d_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.ViewType3D)
all_groups     = FilteredElementCollector(doc).OfClass(Group).ToElements()


# FUNCTIONS ----------------------------------------------------

def create_new_3D_view(isolate_ids):
    new_view = View3D.CreateIsometric(doc, view3d_type_id)

    # Convert Python list to .NET List!
    List_isolate_ids = List[ElementId](isolate_ids)

    # Isolate Elements
    new_view.IsolateElementsTemporary(List_isolate_ids)
    new_view.ConvertTemporaryHideIsolateToPermanent()

    return new_view


# MAIN ---------------------------------------------------------

# Get groups
all_group_types  = FilteredElementCollector(doc).OfClass(GroupType)
dict_group_types = {Element.Name.GetValue(g) :g for g in all_group_types}

if not dict_group_types:
    forms.alert('No GroupTypes in the project. Try again', exitscript=True)

# USER INPUT select groups, catches no selected groups
sel_group_type_names = forms.SelectFromList.show(dict_group_types.keys(), 
                                                 multiselect=True,
                                                 button_name='Select Group Types',
                                                 title='Select Groups To Isolate')

if not sel_group_type_names:
    forms.alert('No Group Types Selected. Please Try again', exitscript=True)

# List of selected group names
sel_group_types  = [dict_group_types[sel_g_name] for sel_g_name in sel_group_type_names]
group_type_names = [Element.Name.GetValue(g) for g in sel_group_types]


## ALLOW CHANGES IN REVIT vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
t = Transaction(doc, __title__)
t.Start()  

# Create new views
new_views = []
view_mode = forms.alert("Would you like Single/Multiple Views?",
                        title = 'Select View Mode',
                        options=["Single View (All)","Multiple Views (Each)"])

if view_mode == "Single View (All)":
    # Get, filter group instances
    all_groups_to_isolate = [g for g in all_groups if g.Name in group_type_names]

    # Get group elements
    keep_ids = [el_id for group in all_groups_to_isolate for el_id in group.GetMemberIds()]
    new_view = create_new_3D_view(keep_ids)
    new_views.append(new_view)

elif view_mode == "Multiple Views (Each)":
    for group_name in group_type_names:
        # Get, filter group names
        all_groups_to_isolate = [g for g in all_groups if g.Name == group_name]
        el_isolate_ids        = [el_id for g in all_groups_to_isolate for el_id in g.GetMemberIds()]

        new_view = create_new_3D_view(el_isolate_ids)
        new_view.Name = group_name + datetime.datetime.now().strftime(" (%y%m%d_%H%M%S)")
        new_views.append(new_view)


t.Commit()
## END CHANGES IN REVIT ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# Open new view
output.print_md('## New 3D Views Report')
output.print_md("- **Mode:** {}".format(view_mode))
output.print_md("- **Created Views:** {}".format(len(new_views)))

for v in new_views:
    link = output.linkify(v.Id, v.Name)
    print(link)
