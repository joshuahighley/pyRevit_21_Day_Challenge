# -*- coding: utf-8 -*-
__title__   = "Name Changer"
__doc__     = """v1.0 | 18.02.2026 | JTH

DESCRIPTION:
- Exercise 3 of EF 21-Day Pyrevit Challenge
- Change the name of views
"""


# IMPORTS ------------------------------------------------------

from Autodesk.Revit.DB import *

#.NET Imports
import clr
clr.AddReference('System')
from System.Collections.Generic import List

from Autodesk.Revit.UI.Selection import ObjectType

from pyrevit import script
from pyrevit.forms import select_views, select_sheets, alert

from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, Separator, Button, CheckBox)


# VARIABLES ----------------------------------------------------

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

output = script.get_output()


# MAIN ---------------------------------------------------------

# 1. Select Views - if none selected, alert
sel_views = select_views()
if not sel_views:
    alert('No views selected :(', exitscript=True)

# 2. Create form for user inputs
components = [Label('PREFIX:'), TextBox('prefix'),
            Label('FIND:'), TextBox('find'),
            Label('REPLACE:'), TextBox('replace'),
            Label('SUFFIX:'), TextBox('suffix'), 
            Separator(), Button('Rename')]

form = FlexForm('Title', components)
form.show()

values  = form.values
pref    = values['prefix']
find    = values['find']
replace = values['replace']
suffix  = values['suffix']

# 3. 
print('Renaming Views...')

## ALLOW CHANGES IN REVIT
t = Transaction(doc, 'Name Changer')
t.Start()
t_count = 0

# Rename list of selected views
for view in sel_views:
    old_name = view.Name
    new_name = pref + old_name.replace(find, replace) + suffix
    
    try:
        view.Name = new_name
        print("{} is now {}".format(old_name, new_name))
        t_count += 1
    except Exception as err:
        #Alt/to-do: rename with asterisk and create separate t_count list for misnamed views? 
        print("{} was not renamed (error: {})".format(old_name, str(err)))

t.Commit()
## END CHANGES IN REVIT

print(str(t_count) + " view(s) renamed.")
