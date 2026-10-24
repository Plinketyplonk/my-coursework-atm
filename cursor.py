"""
Used for managing changing the cursor
"""

import pygame as p
from resource_path import *

print("Loading cursors")

cursors = {
    "normal" : p.Cursor((0,0), p.image.load(resource_path("assets/textures/UI/cursors/normal.png"))),
    "target" : p.Cursor((11,11), p.image.load(resource_path("assets/textures/UI/cursors/target.png"))),

    "normal_red" : p.Cursor((0,0), p.image.load(resource_path("assets/textures/UI/cursors/normal_red.png"))),
}

def change_cursor(cursor):
    p.mouse.set_cursor(cursors[cursor])

change_cursor("normal") # default cursor