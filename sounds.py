"""
All the code for managing sounds and music
"""

import pygame as p
from resource_path import *
import json

class sound_manager():
    def __init__(self):
        print("Loading sounds")
        
        self.ui_sounds = {
                        "carousel_click" : p.mixer.Sound(resource_path("assets/sounds/ui/building/scroll_click.wav")),
                        "bin_tile" : p.mixer.Sound(resource_path("assets/sounds/ui/building/bin_tile.wav")),
                        "generic_click" : p.mixer.Sound(resource_path("assets/sounds/ui/generic/click.wav")),
                        "place_tile" : p.mixer.Sound(resource_path("assets/sounds/ui/building/place.wav")),
                        "menu_open" : p.mixer.Sound(resource_path("assets/sounds/ui/generic/menu_open.wav")),
                        "menu_close" : p.mixer.Sound(resource_path("assets/sounds/ui/generic/menu_close.wav")),
                        "ui_select" : p.mixer.Sound(resource_path("assets/sounds/ui/generic/ui_select.wav")),
                        "generic_deny" : p.mixer.Sound(resource_path("assets/sounds/ui/generic/deny.wav")),
                        "generic_error" : p.mixer.Sound(resource_path("assets/sounds/ui/generic/error.wav"))
                    }
    
        try:
            with open("settings.json", "rt") as f:
                loaded_settings = json.load(f)
            self.ui_volume = float(loaded_settings["ui_volume"]) # set all the independent volumes directly
            self.update_master_volume(float(loaded_settings["master_volume"])) # only master volume shall use its update method
        except Exception as e:
            self.master_volume = 1
            self.ui_volume = 1
            print(f"THERE WAS AN ERROR LOADING SETTINGS WHILE TRYING TO LOAD VOLUMES.\n{e}\n (defaulting all volumes to full)")
        
    

    def update_ui_volume(self, new_vol):
        self.ui_volume = new_vol
        final_ui_volume = self.ui_volume * self.master_volume
        print(final_ui_volume)
        for sound in self.ui_sounds:
            self.ui_sounds[sound].set_volume(final_ui_volume)

        

    def update_master_volume(self, new_vol):
        self.master_volume = new_vol
        self.update_ui_volume(self.ui_volume)
        
    

    def boop(self):
        self.ui_sounds["bin_tile"].play()

sound = sound_manager()
