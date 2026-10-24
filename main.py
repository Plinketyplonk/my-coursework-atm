"""
The main file that links everything C:
"""

import pygame as p


# pygame essentials

p.init()
clock = p.time.Clock()


import render
renderer = render.Renderer() # init the renderer

import sounds, render, pause_menu, save_game, galaxy.stations, galaxy.galaxy_map, building

running = True



class Key_Events_Class():
    def __init__(self):
        pass

    def key_down_handling(self, ev):
        global running

        key = ev.key

        if pause_menu.typing_save_name: # lock other keyboard actions when typing
            key_unicode = p.key.name(key)
            blocked_keys = ["\\", '"', "/", "?", "|", "*", ":", "<", ">", "."] # cant include in the save name

            modifier_keys = {"-" : "_", "=" : "+", "1" : "!", "3" : "£", "4" : "$", "5" : "%", "6" : "^", "7" : "&", "9" :"(", "0" : ")", "'" : "@", "#" : "~", "`" : "¬"} # when holding shift, use the alt key

            if key_unicode == "return":
                pause_menu.typing_save_name = False

                if pause_menu.typing_load_name: # load
                    if save_game.load_save():
                        renderer.main_ticker.push_ticker(1) # load worked

                        renderer.generic_ui.changed_since_last_frame = True # change fuel level gauge
                        renderer.grid_map.changed_since_last_frame = True
                        renderer.galaxy_map.changed_since_last_frame = True
                        renderer.galaxy_map.info_changed_since_last_frame = True
                    else:
                        renderer.main_ticker.push_ticker(2) # load failed (no file)

                    pause_menu.typing_load_name = False

                else: # save
                    if save_game.save_game("", ""):
                        renderer.main_ticker.push_ticker(0) # save worked

            elif key_unicode == "escape":
                pause_menu.typing_save_name = False
                pause_menu.typing_load_name = False
                
            elif key_unicode == "backspace":
                save_game.current_save = save_game.current_save[:-1]
            elif len(key_unicode) == 1 and key_unicode not in blocked_keys: # blocks special keys
                if p.key.get_pressed()[p.K_LSHIFT] or p.key.get_pressed()[p.K_RSHIFT]:
                    key_unicode = modifier_keys[key_unicode]

                save_game.current_save += key_unicode

        else:
            if key == p.K_SPACE and not galaxy.galaxy_map.map_visible:
                building.toggle_build_mode()

            elif key == p.K_LSHIFT:
                if building.build_mode: # hold shift to place multiple tiles
                    building.multi_place = True
                    renderer.building_ui.element_data["grid"]["moved_since_last_frame"] = True
            
            elif key == p.K_ESCAPE:
                pause_menu.toggle_pause()

            elif (key == p.K_m or key == p.K_TAB) and not building.build_mode:
                galaxy.galaxy_map.toggle_map()

            elif (key == p.K_e):
                building.fuel_level += int(input("Fuel: "))
                renderer.generic_ui.changed_since_last_frame = True # change fuel level gauge
            elif (key == p.K_q):
                print(renderer.active_camera.pos)

            elif key == p.K_w:
                renderer.active_camera.player_accelerate_camera("W")
            elif key == p.K_s:
                renderer.active_camera.player_accelerate_camera("S")
            elif key == p.K_a:
                renderer.active_camera.player_accelerate_camera("A")
            elif key == p.K_d:
                renderer.active_camera.player_accelerate_camera("D")

    def key_up_handling(self, ev):
        global running
        key = ev.key

        if key == p.K_LSHIFT:
            if building.build_mode:
                if building.selected_tile != 1:
                    sounds.sound.ui_sounds["bin_tile"].play()
                    building.multi_place = False
                    building.drag_placing = False
                    building.selected_tile = 1
                    renderer.building_ui.element_data["grid"]["moved_since_last_frame"] = True
        
        elif key == p.K_w:
                renderer.active_camera.player_movement[1][0] = False
        elif key == p.K_s:
            renderer.active_camera.player_movement[1][1] = False
        elif key == p.K_a:
            renderer.active_camera.player_movement[0][0] = False
        elif key == p.K_d:
            renderer.active_camera.player_movement[0][1] = False



class Mouse_Events_Class():
    def __init__(self):
        pass

    def resolve_scolling(self, button):
        if building.build_mode:
            if p.mouse.get_pos()[1] > renderer.display_resolution[1] - renderer.building_ui.element_data["tile_carousel"]["height"]:
                if button == 4:
                    renderer.building_ui.element_data["tile_carousel"]["scroll_speed"] += renderer.building_ui.element_data["tile_carousel"]["scroll_speed_add"]
                    renderer.building_ui.element_data["tile_carousel"]["moved_since_last_frame"] = True
                else:
                    renderer.building_ui.element_data["tile_carousel"]["scroll_speed"] -= renderer.building_ui.element_data["tile_carousel"]["scroll_speed_add"]
                    renderer.building_ui.element_data["tile_carousel"]["moved_since_last_frame"] = True
                    
    def resolve_left_click_down(self):
        global running
        mouse_pos = p.mouse.get_pos()

        if pause_menu.paused:
            for button in pause_menu.buttons:
                running = button.check_if_clicked(running, mouse_pos)

        elif building.build_mode:
            # check if clicking on tile carousel area
            if (mouse_pos[1] > renderer.display_resolution[1] - renderer.building_ui.element_data["tile_carousel"]["height"]):
                if mouse_pos[0] < 1648:
                    building.select_tile(renderer.building_ui.element_data["tile_carousel"]["scroll_pos"], renderer.building_ui.element_data["tile_carousel"]["tile_padding"], mouse_pos[0])
                else:
                    for button in renderer.building_ui.element_data["tile_carousel"]["buttons"]:
                        button_pressed =  button.check_if_interacted(mouse_pos)
                        if button_pressed == "load":
                            save_game.load_save()
                        elif button_pressed == "save":
                            save_game.save_game("")
            elif building.multi_place and building.selected_tile != 1:
                building.drag_placing = True

        else: # if not building mode
            if mouse_pos[0] > 1880 and mouse_pos[1] < 120:
                for button in renderer.generic_ui.buttons:
                    button_pressed = button.check_if_interacted(mouse_pos)
            
            if galaxy.galaxy_map.map_visible:
                result = galaxy.galaxy_map.jump_to_new_station(mouse_pos, renderer.active_camera)
                if result[0]: # true when the jump is done
                    renderer.galaxy_map.changed_since_last_frame = True
                    renderer.galaxy_map.info_changed_since_last_frame = True
                    renderer.generic_ui.changed_since_last_frame = True # change fuel level gauge
                if result[1] != -1: # -1 means no error to add
                    renderer.galaxy_map.ticker.push_ticker(result[1])

    def resolve_left_click_up(self):
        mouse_pos = p.mouse.get_pos()
        if building.build_mode:
            if building.selected_tile != 1: # ie if smth getting dragged and dropped somewhere (1 is the None tile)
                if mouse_pos[1] > renderer.display_resolution[1] - renderer.building_ui.element_data["tile_carousel"]["height"]:
                    if not building.demo_mode and building.selected_tile != 0 and not building.multi_place: # cant discard of the "demo" tile, so force you to press the button to disable it instead, also made it so that holding shift means that you dont discard of it
                        sounds.sound.ui_sounds["bin_tile"].play()
                        building.selected_tile = 0 # 0 is 'none'/empty tile
                        building.multi_place = False
                else:
                    if building.place_tile(mouse_pos, renderer.camera_main):
                        sounds.sound.ui_sounds["place_tile"].play()

                    if not (building.multi_place or building.demo_mode): # not holding shift to place multiple
                        building.selected_tile = 0

                building.drag_placing = False
                renderer.building_ui.element_data["grid"]["moved_since_last_frame"] = True
                renderer.grid_map.changed_since_last_frame = True

    def resolve_right_click_down(self):
        if building.build_mode: # right clicking cancels what ur doing
            building.selected_tile = 0 # 0 is 'none'/empty tile
            building.multi_place = False
            building.drag_placing = False
            building.demo_mode = False
            sounds.sound.ui_sounds["bin_tile"].play()
            renderer.building_ui.element_data["grid"]["moved_since_last_frame"] = True

    def resolve_mouse_down(self, ev):
        button = ev.dict["button"]
        if button == 1:
            self.resolve_left_click_down()
        elif button == 3:
            self.resolve_right_click_down()
        elif button == 5 or button == 4:
            self.resolve_scolling(button)
        else:
            pass # 2 is middle mouse down, 6 and 7 (stfu) is the undo and redo side buttons
        
    def resolve_mouse_up(self, ev):
        button = ev.dict["button"]
        if button == 1:
            self.resolve_left_click_up()

    def resolve_motion(self, ev):
        mouse_pos = p.mouse.get_pos()
        if building.build_mode and building.selected_tile != 0:
            renderer.building_ui.element_data["grid"]["moved_since_last_frame"] = True

            if building.drag_placing:
                if building.place_tile(mouse_pos, renderer.camera_main):
                    sounds.sound.ui_sounds["place_tile"].play()
                    renderer.grid_map.changed_since_last_frame = True
        
        if galaxy.galaxy_map.map_visible:
            renderer.galaxy_map.info_changed_since_last_frame = True



Key_Events = Key_Events_Class()
Mouse_Events = Mouse_Events_Class()



print("\nLoading success!\n")



def handle_events():
    global running
    for ev in p.event.get():
        if ev.type == p.DROPFILE:
            print(ev.file)
        if ev.type == p.QUIT:
            running = pause_menu.quit(running)
        elif ev.type == p.KEYDOWN:
            Key_Events.key_down_handling(ev)
        elif ev.type == p.KEYUP:
            Key_Events.key_up_handling(ev)
        elif ev.type == p.MOUSEBUTTONDOWN:
            Mouse_Events.resolve_mouse_down(ev)
        elif ev.type == p.MOUSEBUTTONUP:
            Mouse_Events.resolve_mouse_up(ev)
        elif ev.type == p.MOUSEMOTION:
            Mouse_Events.resolve_motion(ev)


crashed = False

import random

while running:
    #try: # uncomment this and the except block for when not debugging
        dt = clock.tick(60) / 1000
        fps = clock.get_fps()
        
        handle_events()

        renderer.render_tick(building.build_mode, dt, save_game.current_save, fps)

        save_game.autosave(dt)
    #except Exception as e:
        #save_game.autosave(0, crash_exception=e, forced=True) # the game crashed, so save whatever the current state is rn as a seperate "crash_save" to try recover progress or at the least give the senario that the game crashed in
        #crashed = True
        #p.event.post(p.QUIT)

if not crashed:
    save_game.autosave(0, forced=True)

p.quit()