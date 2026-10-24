"""
All the code for managing sounds and music
"""

import pygame as p
from resource_path import *

class sound_manager():
    def __init__(self):
        print("Loading sounds")

        self.master_volume = 1
        
        self.ui_volume = 1
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
        
    

    def update_ui_volume(self, new_vol):
        self.ui_volume = new_vol
        final_ui_volume = self.ui_volume * self.master_volume
        for sound in self.ui_sounds:
            self.ui_sounds[sound].set_volume(final_ui_volume)

        

    def update_master_volume(self, new_vol):
        self.master_volume = new_vol
        self.update_ui_volume(self.ui_volume)
        
    

    def boop(self):
        self.ui_sounds["bin_tile"].play()

sound = sound_manager()

# ngl i think everything is too loud sooo..

sound.update_master_volume(0.1)