# -*- coding: utf-8 -*-
__title__   = "Tagless Shame List"
__doc__     = """v1.0 | 27.02.2026 | JTH

DESCRIPTION:
- Exercise 7 of EF 21-Day Pyrevit Challenge
- 
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document
rvt_year = int(app.VersionNumber)
output = script.get_output()

bic = BuiltInCategory
cat_dict = {
    'Doors': (bic.OST_Doors, bic.OST_DoorTags), 
    'Furniture': (bic.OST_Furniture, bic.OST_FurnitureTags), 
    'Windows': (bic.OST_Windows, bic.OST_WindowTags)
    }


# FUNCTION -----------------------------------------------------

def get_tagged_el_ids(f_all_el_tags):
    """Helper function to get tagged element ids depending on Revit API Version."""
    if rvt_year > 2021:
        return [el_id for tag in f_all_el_tags for el_id in tag.GetTaggedLocalElementIds()]
    else:
        return [tag.GetTaggedLocalElement().Id for tag in f_all_el_tags]


# MAIN ---------------------------------------------------------

# Select Category
selected_option = forms.CommandSwitchWindow.show(
    sorted(cat_dict), message='Select Category to Investigate:')

cat = cat_dict[selected_option][0]
cat_tags = cat_dict[selected_option][1]

# Select views, prompt user if no views selected
selected_views = forms.select_views()
if not selected_views:
    forms.alert('No views selected. Please select at least one view to continue.')
    
    # Give 'em one last chance
    selected_views = forms.select_views()
    if not selected_views:
        forms.alert('No views selected. Try running the script again.')


# For each view, create list of untagged elements
for view in selected_views:
    # Collect all elements and element tags of matching category
    all_els = FilteredElementCollector(doc, view.Id).OfCategory(cat).WhereElementIsNotElementType().ToElements()
    all_el_tags = FilteredElementCollector(doc, view.Id).OfCategory(cat_tags).WhereElementIsNotElementType().ToElements()

    # Create list of all tagged elements of matching category
    tagged_el_ids = []
    # for tag in all_el_tags:
    #     tagged_el = tag.GetTaggedLocalElements()
    #     tagged_el_id = tag.GetTaggedLocalElementIds()

    #     tagged_el_ids += tagged_el_id

    get_tagged_el_ids(all_el_tags)
    
    # Filter out tagged elements from list of all elements, results in list of untagged
    untagged_els = [el for el in all_els if el.Id not in tagged_el_ids]
    
    # Print view
    view_name = '{} ({})'.format(view.Name, view.ViewType)
    link_view = output.linkify(view.Id, view.Name)
    output.print_md('### View: {} '.format(link_view))

    # Print untagged
    for elem in untagged_els:
        cat_name     = elem.Category.Name
        elem_type_id = elem.GetTypeId()
        elem_type    = doc.GetElement(elem_type_id)
        family       = elem_type.Family

        elem_name = '{}: {}_{}'.format(cat_name,family.Name, elem.Name)
        link = output.linkify(elem.Id, elem_name)
        output.print_md('- {}'.format(link))

    output.print_md('---')
