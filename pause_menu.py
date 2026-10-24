"""
Da pause menu 🗣 for quitting and STUFF
"""

import sounds

paused = False

typing_save_name = False
typing_load_name = False

buttons = []

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        sounds.sound.ui_sounds["menu_open"].play()
    else:
        sounds.sound.ui_sounds["menu_close"].play()



class Menu_Button:
    def __init__(self, pos, function, texture_name, size = (244,52)):
        self.local_pos = pos # local pos

        self.global_pos = (self.local_pos[0] + 810, self.local_pos[1] + 240) # pause menu is blit at (810, 240) so offset local button coord to global

        self.size = size

        self.texture_name = texture_name

        self.function = function

    
    def check_if_clicked(self, running, mouse_pos): # keep mouse_pos at the end to keep tidy
        if (mouse_pos[0] > self.global_pos[0] and mouse_pos[0] < self.global_pos[0] + self.size[0]) and (mouse_pos[1] > self.global_pos[1] and mouse_pos[1] < self.global_pos[1] + self.size[1]):
            running = self.function(running)
        return running
        

# any parameters added to one of these functions needs to be added to ALL OTHER FUNCTIONS and to the check_if_clicked in 

def quit(running):
    running = False
    # should lowk add a quit confirm thing here
    return running

def save(running):
    global typing_save_name

    typing_save_name = True
    return running

def load(running):
    global typing_save_name, typing_load_name

    typing_save_name = True
    typing_load_name = True
    return running

buttons.append(Menu_Button((28, 540), quit, "PM_Quit"))

buttons.append(Menu_Button((28, 480), save, "PM_Save"))

buttons.append(Menu_Button((28, 420), load, "PM_Load"))

buttons.append(Menu_Button((28, 360), quit, "PM_Settings"))