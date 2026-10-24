"""
All of the code to do with rendering + some extra stuff
"""

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0) # this line is lowk stolen from stack overflow, but is used to make sure the program runs as a borderless fullscreen

import numpy as np
import pygame as p

loading_screen = p.display.set_mode((200,200)) # used so imports can load themselves

import building, sounds, pause_menu, main_menu, entities, global_vars
import galaxy.stations as glxy_stns
import galaxy.galaxy_map as glxy_map
from random import randint
from resource_path import *

class UI_Button():
    """
    Used to create simple buttons that can be blitted onto surfaces and interacted with accordingly
    """

    def __init__(self, abs_pos, surface_pos, command, icon_surface, icon_toggled_surface = None): # the 
        self.icon = icon_surface

        if icon_toggled_surface != None:
            self.icon_alt = icon_toggled_surface
        else:
            self.icon_alt = self.icon # if nothing is passed then that means this is obvs not a toggle button

        self.alt_state = False # whether or not the button has been toggled on/off for rendering it

        self.command = command

        self.abs_pos = abs_pos # where it is on the screen
        self.surface_pos = surface_pos # where it is on the surface

        # used to mark where the edges are
        self.bounds_X = [self.abs_pos[0], self.abs_pos[0] + self.icon.get_size()[0]]
        self.bounds_Y = [self.abs_pos[1], self.abs_pos[1] + self.icon.get_size()[1]]



    def check_if_interacted(self, mouse_pos):
        if ((mouse_pos[0] > self.bounds_X[0] and mouse_pos[0] < self.bounds_X[1]) # if the mouse lies on top of the button
        and
        (mouse_pos[1] > self.bounds_Y[0] and mouse_pos[1] < self.bounds_Y[1])):
            self.alt_state = self.command()

            return True # return true because worked
        return False # didnt do anything



    def render(self, surface):
        if not self.alt_state:
            surface.blit(self.icon, self.surface_pos) # blit the normal icon onto the provided surface
        else:
            surface.blit(self.icon_alt, self.surface_pos) # blit the alternative icon if it is toggled on



class Building_UI():
        def __init__(self, display_resolution, gui_textures):
            def pre_load_fonts():
                """
                preloads the fonts and stores each one into the "pre_rendered_fonts"
                """
                print("loading fonts")
                pre_rendered_fonts = {}

                font_size = 20
                initial_font = p.font.Font(resource_path("assets/Pixel.ttf"), font_size) # set the starting font (means the loop doesnt have to constantly load it)
                for tile_id in building.tile_kinds:
                    tile = building.tile_kinds[tile_id]
                    text_surface = p.Surface((tile.size[0] * 60, 60 ), flags=p.SRCALPHA) # dynamically size the surface based on the size of the icon
                    text_surface.fill((0,0,0,0))

                    part_name = tile.name
                    pos = (5, 0) # where the text gets dumped onto the surface
                    name_font = initial_font
                    font_size = 20

                    while name_font.size(part_name)[0] > 60: # this while loop resizes the font until it is a good size
                        name_font = p.font.Font(resource_path("assets/Pixel.ttf"), font_size)
                        font_size -= 1

                    def blit_text_outline(rel_pos, pos, text_surface, name_font, part_name):
                        final_pos = (pos[0] + rel_pos[0], pos[1] + rel_pos[1])
                        text_surface.blit(name_font.render(part_name, True, (0,0,0)), final_pos)
                    blit_text_outline((1,1), pos, text_surface, name_font, part_name) # these 4 are for giving the text a black outline
                    blit_text_outline((-1,1), pos, text_surface, name_font, part_name)
                    blit_text_outline((1,-1), pos, text_surface, name_font, part_name)
                    blit_text_outline((-1,-1), pos, text_surface, name_font, part_name)
                    text_surface.blit(name_font.render(part_name, True, (255,255,255)), pos) # write the actual white part of the text
                    pre_rendered_fonts[tile.name] = text_surface.convert_alpha()
                return pre_rendered_fonts
            self.pre_rendered_fonts = pre_load_fonts() # used for the tile names

            self.limit_font = p.font.Font(resource_path("assets/Pixel.ttf"), 30)

            self.display_resolution = display_resolution


            temp = 0 # used for to find scroll max
            for tile_id in building.tile_kinds:
                tile = building.tile_kinds[tile_id]
                if tile.placeable:
                    temp += tile.size[0] * 64

            self.element_data = {
                "tile_carousel" : {
                    "scroll_pos" : 0,
                    "moved_since_last_frame" : True, # start true so it gets rendered on the first frame it will be shown
                    "height" : 150,
                    "scroll_speed" : 0,
                    "scroll_speed_add" : 10,
                    "scroll_max" : temp,
                    "tile_padding" : 20,
                    "sound_tick_default" : 30, # number of frames/ticks between each click sound when scolling, "sound_tick" is created after this dictionary
                    "buttons" : [
                        UI_Button((1660, 955), (1660, 25), building.Building_UI_Button_Functions.toggle_demo_mode, gui_textures["Bld_Demo"], icon_toggled_surface=gui_textures["Bld_Demo_Alt"])
                    ]
                },
                "grid" : {
                    "moved_since_last_frame" : True
                }
            }
            self.element_data["tile_carousel"]["sound_tick"] = self.element_data["tile_carousel"]["sound_tick_default"] # defined outside of the dictionary because it refers to a dictionary item :)

            self.pre_rendered_elements = {
                "tile_carousel" : p.Surface((1920, 150)),
                "grid" : p.Surface((1920, 930), p.SRCALPHA) # 930 because that where the tile carousel starts
            }



        def render_building_ui(self, screen, gui_textures, tile_ghost_textures, tile_caro_ghost_textures, camera):
            screen.blit(self.grid(camera, tile_ghost_textures), (0,0))
            screen.blit(self.tile_carousel(gui_textures, tile_caro_ghost_textures), (0, 930)) # need to add maths to the pos for screen rescaling

            # show the engine and mass limits (each one should be 32 apart)
            font_colour = (127, 168, 24)

            screen.blit(gui_textures["Bld_Engine"], (5, 5))
            screen.blit(self.limit_font.render(f"{building.thrust_used} / {building.thrust_limit}", True, font_colour), (37, 5))

            screen.blit(gui_textures["Bld_Mass"], (5, 37))
            screen.blit(self.limit_font.render(f"{building.ship_mass} / {building.mass_limit}", True, font_colour), (37, 37))



        def tile_carousel(self, gui_textures, tile_ghost_textures): # the bit at the bottom with all the tiles to choose from
            if self.element_data["tile_carousel"]["moved_since_last_frame"]:
                # moves the carousel along after scoll wheel moves
                self.element_data["tile_carousel"]["scroll_pos"] += int(self.element_data["tile_carousel"]["scroll_speed"])

                if self.element_data["tile_carousel"]["scroll_pos"] > self.element_data["tile_carousel"]["scroll_max"]: # border check
                    self.element_data["tile_carousel"]["scroll_speed"] = 0
                    self.element_data["tile_carousel"]["scroll_pos"] = self.element_data["tile_carousel"]["scroll_max"]

                elif self.element_data["tile_carousel"]["scroll_pos"] < 0:
                    self.element_data["tile_carousel"]["scroll_speed"] = 0
                    self.element_data["tile_carousel"]["scroll_pos"] = 0

                self.element_data["tile_carousel"]["scroll_speed"] = self.element_data["tile_carousel"]["scroll_speed"] * 0.8 # decay

                if abs(self.element_data["tile_carousel"]["scroll_speed"]) < 0.1 and self.element_data["tile_carousel"]["scroll_speed"] != 0: # clip at 0.1 so it no scroll mega slowly forever
                    self.element_data["tile_carousel"]["scroll_speed"] = 0
                    self.element_data["tile_carousel"]["sound_tick"] = self.element_data["tile_carousel"]["sound_tick_default"]
                    self.element_data["tile_carousel"]["moved_since_last_frame"] = False # might seem weird that this is here and not the end but trust
                # sound stuff
                elif self.element_data["tile_carousel"]["sound_tick"] < 0:
                    sounds.sound.ui_sounds["carousel_click"].play()
                    self.element_data["tile_carousel"]["sound_tick"] = self.element_data["tile_carousel"]["sound_tick_default"]
                else:
                    self.element_data["tile_carousel"]["sound_tick"] -= abs(int(self.element_data["tile_carousel"]["scroll_speed"]))
                # no more sound stuff

                # end movement logic

                carousel_surface = self.pre_rendered_elements["tile_carousel"] # just a ref
                carousel_surface.blit(gui_textures["Bld_Build_menu"], (0, 0))

                # blit all of the buttons

                for button in self.element_data["tile_carousel"]["buttons"]:
                    button.render(carousel_surface)

                y_pos = 20
                x_pos = self.element_data["tile_carousel"]["tile_padding"] + self.element_data["tile_carousel"]["scroll_pos"] # starting x
                half_padding = self.element_data["tile_carousel"]["tile_padding"] // 2
                # each tile
                for tile_id in building.tile_kinds:
                    tile = building.tile_kinds[tile_id]
                    if tile.placeable:
                        p.draw.line(carousel_surface, (27, 33, 13), (x_pos - half_padding, 15), (x_pos - half_padding, 135), 3)

                        carousel_surface.blit(tile_ghost_textures[tile.name], (x_pos, y_pos)) # blits the tiles icon to the carousel

                        text_pos = (x_pos+4, y_pos + 80)
                        carousel_surface.blit(self.pre_rendered_fonts[tile.name], text_pos) # blits the name of the part/tile under the tiles icon

                        x_pos += (tile.size[0] * 64 * (1 / tile.size[1])) + self.element_data["tile_carousel"]["tile_padding"] # set x pos for NEXT tile
                p.draw.line(carousel_surface, (27, 33, 13), (x_pos - half_padding, 15), (x_pos - half_padding, 135), 3)

                self.pre_rendered_elements["tile_carousel"] = carousel_surface.convert()
                return carousel_surface
            return self.pre_rendered_elements["tile_carousel"]



        def grid(self, camera, tile_ghost_textures):
            if self.element_data["grid"]["moved_since_last_frame"]:
                grid_surface = self.pre_rendered_elements["grid"] # creates a reference to the surface in the dict so i dont have to type as much
                grid_surface.fill((0,0,0,0))

                line_offset = (camera.pos[0] % 64, camera.pos[1] % 64)
                for x in range(0, self.display_resolution[0], 64):
                    if (camera.pos[0] - x < 63) and (camera.pos[0] - x > building.grid_map_size[0] * -64 + 63):
                        p.draw.line(grid_surface, (190, 255, 190, 100), (x + line_offset[0], camera.pos[1]), (x + line_offset[0], building.grid_map_size[1] * 64 + camera.pos[1] - 64))
                for y in range(0, self.display_resolution[1], 64):
                    if (camera.pos[1] - y < 63) and (camera.pos[1] - y > building.grid_map_size[1] * -64 + 63):
                        p.draw.line(grid_surface, (190, 255, 190, 100), (camera.pos[0], y + line_offset[1]), (building.grid_map_size[0] * 64 + camera.pos[0] - 64, y + line_offset[1]))

                # draw the selected tile's ghost onto the grid
                if building.tile_kinds[building.selected_tile].placeable:

                    snapped_pos = ((p.mouse.get_pos()[0] - camera.pos[0]) // 64 * 64 + camera.pos[0], (p.mouse.get_pos()[1] - camera.pos[1]) // 64 * 64 + camera.pos[1]) # this took WAY too long to figure out
                    grid_surface.blit(tile_ghost_textures[building.tile_kinds[building.selected_tile].name], snapped_pos)

                self.pre_rendered_elements["grid"] = grid_surface.convert_alpha()
                self.element_data["grid"]["moved_since_last_frame"] = False
                return grid_surface
            return self.pre_rendered_elements["grid"]



class GridMap_Renderer(): # renderers all the stuff from the ships tilemap/gridmap
    def __init__(self):
        self.changed_since_last_frame = True
        
        surface_size = (building.grid_map_size[0] * 64, building.grid_map_size[1] * 64)

        self.render_cache = p.surface.Surface(surface_size, p.SRCALPHA)
    

    def render(self, camera, tile_textures, screen):
        if self.changed_since_last_frame:
            self.render_cache.fill((0,0,0,0)) # clear for fresh render


            for x in range(len(building.tile_kind_map)):
                for y in range(len(building.tile_kind_map[x])):
                    if building.tile_kind_map[x, y] == 0:
                        pass
                    elif (x, y) == (building.tile_origin_map[x, y][0], building.tile_origin_map[x, y][1]):
                        self.render_cache.blit(tile_textures[
                            building.tile_kinds[building.tile_kind_map[x, y]].name
                        ], (x*64,y*64))

            self.changed_since_last_frame = False
        screen.blit(self.render_cache, camera.pos)



class Generic_UI():
    def __init__(self, gui_textures):
        self.changed_since_last_frame = True

        self.buttons = [UI_Button((1880, 10), (10, 10), glxy_map.toggle_map, gui_textures["Gnrc_Map"])]

        self.render_cache = p.surface.Surface((50, 150))


    def render(self, gui_textures):

        if self.changed_since_last_frame:
            # render fuel gauge level
            if building.fuel_limit > 0:
                fuel_percent = building.fuel_level / building.fuel_limit
            else:
                fuel_percent = 0
            self.render_cache.fill((10,5,4), p.Rect((6, 132), (40, 14)))
            self.render_cache.fill((50,20,4), p.Rect((6, 132), (40 * fuel_percent, 14)))

            self.render_cache.blit(gui_textures["Gnrc_Box"], (0,0))

            for button in self.buttons:
                button.render(self.render_cache)

        
            self.changed_since_last_frame = False 
        return self.render_cache



class Pause_Menu():
    def __init__(self):
        self.changed_since_last_frame = True

        self.render_cache = p.surface.Surface((300, 600)) # should probs use the size of the pause menu but dont plan on changing the texture size so whatever
    

    def render(self, gui_textures):
        if self.changed_since_last_frame:
            self.render_cache.blit(gui_textures["PM_Pause_Menu"], (0, 0))

            for button in pause_menu.buttons:
                self.render_cache.blit(gui_textures[button.texture_name], button.local_pos)

        return self.render_cache



class Ticker():
    """
    Stores a stack of numbers with a limited lifespan, used for predefined ingame (error) messages.
    It also handles all of its own rendering, so all you have to do is tell your frame to blit it at (x,y) using the render function (shock horror, render function renders!)
    """
    def __init__(self, size, lifespan, messages, font_size = 30):
        # the ticker is a stack, BUT every element is accessed not just the top
        self.size = size # the max number of error tickers that can exist at the same time before overflow
        self.top = 0
        self.tickers = np.full((self.size, 2), 0, dtype="i") # an array of type and then frames left, 0 for not enough fuel, 1 for too heavy, 2 for not enough engine power, 3 station not reachable
        self.lifespan = lifespan # in frames (so roughly x/60 seconds)
        self.font_size = font_size

        def render_ticker(text):
            surf_width = p.font.Font(resource_path("assets/Pixel.ttf"), self.font_size).render(text, False, (255, 255, 255)).get_width() + 10
            
            surf = p.Surface((surf_width, self.font_size + 10), p.SRCALPHA)

            surf.fill((150, 2, 1, 100))
            surf.blit(p.font.Font(resource_path("assets/Pixel.ttf"), self.font_size).render(text, False, (255, 255, 255)), (5, 5))

            return surf

        self.ticker_renders = []
        self.biggest_width = 0
        for message in messages:
            rendered_message = render_ticker(message)
            self.ticker_renders.append(rendered_message)
            self.biggest_width = max(self.biggest_width, render_ticker(message).get_width()) # find biggest width so that when rendering, every message fits on (without needing extra)

        self.surf = p.Surface((self.biggest_width, (self.font_size + 10) * self.size), p.SRCALPHA)

    def push_ticker(self, ticker_type):
        if self.top < self.size:
            self.tickers[self.top][0] = ticker_type
            self.tickers[self.top][1] = self.lifespan
            self.top += 1
        else:
            print("Ticker overflow")


    def pop_error_ticker(self): # brings them all down an index, which yea is inefficent BUT its like not many items and rarely soooooooo
        if self.top -1 > -1:
            self.top -= 1
            for ticker in range(self.top):
                self.tickers[ticker] = self.tickers[ticker + 1]
        else:
            print("Ticker underflow (WTF DID YOU DO?!?!?!?!)")


    def pass_frame(self): # decreases all living tickers lifes by a tick
        for ticker in range(self.top):
            self.tickers[ticker][1] -= 1
            if self.tickers[ticker][1] < 0:
                self.pop_error_ticker()

    def render(self):
        self.surf.fill((0,0,0,0)) # set blank + transparent

        if self.top > 0:
            for ticker in range(self.top):
                ticker_type = self.tickers[ticker][0]

                self.ticker_renders[ticker_type].set_alpha(self.tickers[ticker][1]/self.lifespan*255) # fadeout

                self.surf.blit(self.ticker_renders[ticker_type], (5, self.ticker_renders[0].get_height() * (self.top - ticker - 1)))
            self.pass_frame()
        
        return self.surf



class Galaxy_Map():

    steps_per_anim_frame = 10 # how many game frames between each animation frame change
    max_anim_frame = steps_per_anim_frame * 4 # theres 4 frames

    def __init__(self):
        self.changed_since_last_frame = True

        self.info_changed_since_last_frame = True
        self.info_pos = (0,0)

        self.anim_frame = 0

        self.render_cache = [
            p.surface.Surface((1920, 1080), p.SRCALPHA), # the actual map bit
            p.surface.Surface((300, 250), p.SRCALPHA) # the connection information bit
            ]
        
        self.fonts = {
            "header" : p.font.Font(resource_path("assets/Pixel.ttf"), 36),
            "header_small" : p.font.Font(resource_path("assets/Pixel.ttf"), 24),
            "info" : p.font.Font(resource_path("assets/Pixel.ttf"), 24)
        }
        
        self.ticker = Ticker(31, 240, ["Not enough fuel!", "Not enough thrusters!", "Not engine power!", "Station too far!"])


    def render_info(self, active_camera):
        if self.info_changed_since_last_frame:
            self.info_pos, thrt_lvl, kind, fuel, contract_count, name = glxy_map.gather_stats_for_info(p.mouse.get_pos(), active_camera)

            self.render_cache[1].fill((50, 40, 30)) # background


            header_render = self.fonts["header"].render(name, True, (240,240,240))
            if header_render.get_width() > self.render_cache[1].get_width() - 3:
                header_render = self.fonts["header_small"].render(name, True, (240,240,240))

            self.render_cache[1].blit(header_render, (3, 3))

            self.render_cache[1].blit(self.fonts["info"].render(fuel, True, (230,230,230)), (3, 45))
            self.render_cache[1].blit(self.fonts["info"].render(kind, True, (230,230,230)), (3, 75))
            self.render_cache[1].blit(self.fonts["info"].render(contract_count, True, (230,230,230)), (3, 105))


            self.render_cache[1].blit(self.fonts["info"].render("Threat Level: ", True, (230,230,230)), (3, 135))

            bar_start = self.fonts["info"].render("Threat Level: ", True, (230,230,230)).get_width() + 4
            self.render_cache[1].fill((200, 190, 180), p.Rect((bar_start-1, 134), (102, 24 + 2)))
            self.render_cache[1].fill((10, 10, 10), p.Rect((bar_start, 135), (100, 24)))
            self.render_cache[1].fill((255, 60, 50), p.Rect((bar_start, 135), (thrt_lvl, 24)))

            self.info_changed_since_last_frame = False

            self.render_cache[1].set_alpha(100)
        return self.render_cache[1]



    def render(self, active_camera, gui_textures, display_resolution):

        self.anim_frame += 1 # increase the anim frame step
        if self.anim_frame > Galaxy_Map.max_anim_frame: # clip it
            self.anim_frame = 0

        if self.changed_since_last_frame:
            self.render_cache[0].fill((30, 20, 10, 200)) # background tint

            ps_d = glxy_stns.Station.pos_distancing

            for node in glxy_stns.stations: # draw the debug tiles for the threat level
                break
                tile_pos = ((node.station_id // glxy_map.Generate_New_Map.num_columns) * ps_d + glxy_stns.Station.pos_offset[0] + active_camera.pos[0],
                            (node.station_id - (node.station_id // glxy_map.Generate_New_Map.num_columns) * glxy_map.Generate_New_Map.num_columns) * ps_d + glxy_stns.Station.pos_offset[1] + active_camera.pos[1])
                

                colour = (node.threat_level * 2.5, 255 - node.threat_level * 2.5, 0)
                self.render_cache[0].fill(colour, ((tile_pos), (ps_d, ps_d)))

            for node in glxy_stns.stations: # draw connecting lines
                for connection in glxy_stns.station_links[node.station_id]:
                    off_pos = (node.pos[0] + active_camera.pos[0], node.pos[1] + active_camera.pos[1]) #offset pos by camera pos

                    cnt_pos = glxy_stns.stations[connection].pos
                    cnt_pos = (cnt_pos[0] + active_camera.pos[0], cnt_pos[1] + active_camera.pos[1]) #offset again

                    rect_size = [off_pos[0] - cnt_pos[0], off_pos[1] - cnt_pos[1]]
                    if abs(rect_size[0]) < 1:
                        rect_size[0] = 1
                    if abs(rect_size[1]) < 1:
                        rect_size[1] = 1

                    if p.Rect(off_pos, rect_size).colliderect(p.Rect((0,0), display_resolution)):
                        if connection == glxy_map.current_station or node.station_id == glxy_map.current_station:
                            p.draw.line(self.render_cache[0], (127, 168, 24), off_pos, cnt_pos, 2) # a line for the connection
                        else:
                            p.draw.line(self.render_cache[0], (27, 33, 13), off_pos, cnt_pos, 2) # a line for the connection
            

            # choose which image to use for the animated ones

            if self.anim_frame < Galaxy_Map.steps_per_anim_frame: #1st frame
                anim_texture = gui_textures["Glxy_stn_on_frame0"]
            elif self.anim_frame < Galaxy_Map.steps_per_anim_frame * 2:
                anim_texture = gui_textures["Glxy_stn_on_frame1"]
            elif self.anim_frame < Galaxy_Map.steps_per_anim_frame * 3:
                anim_texture = gui_textures["Glxy_stn_on_frame2"]
            else:
                anim_texture = gui_textures["Glxy_stn_on_frame3"]

            for node in glxy_stns.stations:
                off_pos = (node.pos[0] + active_camera.pos[0] - 15, node.pos[1] + active_camera.pos[1] - 15) #offset pos by camera pos

                if node.station_id == glxy_map.current_station: # currently selected
                    off_pos = (max(0, min(off_pos[0], 1890)), max(0, min(off_pos[1], 1050))) # clamp the pos so that it's always on screen, like a minecraft locator map
                    self.render_cache[0].blit(gui_textures["Glxy_stn_current"], off_pos) 

                elif p.Rect(off_pos, (gui_textures["Glxy_stn_off"].get_size())).colliderect(p.Rect((0,0), display_resolution)): # only render it if it is onscreen
                    if node.station_id in glxy_stns.station_links[glxy_map.current_station]:
                        self.render_cache[0].blit(anim_texture, off_pos) # neigbours
                    else:
                        self.render_cache[0].blit(gui_textures["Glxy_stn_off"], off_pos) # far

            off_pos = (self.info_pos[0] + active_camera.pos[0], self.info_pos[1] + active_camera.pos[1])
            self.render_cache[0].blit(self.render_info(active_camera), off_pos)

            self.render_cache[0].blit(self.ticker.render(), (5,5))

            self.changed_since_last_frame = False

        return self.render_cache[0]
        


class Background():
    def create_star_layer(number_of_stars): # creates a transparent canvas of white dots to use for the background (for parallax effect)
            layer = p.surface.Surface((1920, 1080), p.SRCALPHA)

            for star in range(number_of_stars):
                brightness = randint(50, 250) - number_of_stars // 2

                size = int(max(brightness / 50, 1))

                layer.fill((brightness,brightness,brightness), p.Rect((randint(0, 1910), randint(0, 1070)), (size, size))) # place a star
            
            return layer
    

    def __init__(self, display_resolution):
        self.background_layers = [Background.create_star_layer(((i * 3) + 50)) for i in range(3)]

        self.changed_since_last_frame = True
        self.render_cache = p.surface.Surface((display_resolution[0], display_resolution[1]))


    def render(self, camera_pos, display_resolution):
        if self.changed_since_last_frame:
            self.render_cache.fill((0,0,0))


            for layerNo in range(len(self.background_layers)):
                offset = (int(camera_pos[0] / (layerNo + 3)) % display_resolution[0],
                          int(camera_pos[1] / (layerNo + 3)) % display_resolution[1])

                self.render_cache.blit(self.background_layers[layerNo], offset)

                # check in all directions to make sure the thing is seemless

                def blit_wrapped_around(wrap_side):
                    extra_offset = (offset[0] + wrap_side[0] * display_resolution[0],
                                    offset[1] + wrap_side[1] * display_resolution[1])

                    self.render_cache.blit(self.background_layers[layerNo], extra_offset)

                if offset[0] <= 0:
                    blit_wrapped_around((1, 0))
                    if offset[1] <= 0:
                        blit_wrapped_around((0, 1))
                        blit_wrapped_around((1, 1))
                    else:
                        blit_wrapped_around((0, -1))
                        blit_wrapped_around((1, -1))
                else:
                    blit_wrapped_around((-1, 0))
                    if offset[1] <= 0:
                        blit_wrapped_around((0, 1))
                        blit_wrapped_around((-1, 1))
                    else:
                        blit_wrapped_around((0, -1))
                        blit_wrapped_around((-1, -1))
        return self.render_cache



class Camera():
    def __init__(self):
        self.pos = [0,0]
        self.velocity = [0,0]
        self.zoom_level = 1 # unused rn - probably always will be (complicates things a lot)
        self.max_speed = 16

        self.player_movement = [[False, False], [False, False]] # [A, D], [W, S]

    def player_accelerate_camera(self, key):
        if key == "W":
            self.accelerate_camera(0, self.max_speed, True)
            self.player_movement[1][0] = True
            self.player_movement[1][1] = False
        elif key == "S":
            self.accelerate_camera(0, -self.max_speed, True)
            self.player_movement[1][1] = True
            self.player_movement[1][0] = False
        elif key == "A":
            self.accelerate_camera(self.max_speed, 0, True)
            self.player_movement[0][0] = True
            self.player_movement[0][1] = False
        elif key == "D":
            self.accelerate_camera(-self.max_speed, 0, True)
            self.player_movement[0][1] = True
            self.player_movement[0][0] = False
        else:
            raise Exception(f"Invalid movement key passed into active_camera.player_accelerate_camera(), idk how that happened but it did. Key was:\n{key}")

    def accelerate_camera(self, x, y, set_vel = False):
        if set_vel:
            if x != 0:
                self.velocity[0] = x
            if y != 0:
                self.velocity[1] = y
        else:
            self.velocity[0] += x
            self.velocity[1] += y
        
    def move_camera(self, renderer):
        keys = p.key.get_pressed()

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # camera drag
        if not (keys[p.K_a] or keys[p.K_d]):
            self.velocity[0] = self.velocity[0] * 0.85
        if not (keys[p.K_w] or keys[p.K_s]):
            self.velocity[1] = self.velocity[1] * 0.85
    
        # velocity clip
        if abs(self.velocity[0]) < 0.1:
            self.velocity[0] = 0
        if abs(self.velocity[1]) < 0.1:
            self.velocity[1] = 0

        # tell anything that should move with the camera that the camera has moved
        if building.build_mode:
            renderer.building_ui.element_data["grid"]["moved_since_last_frame"] = True
        elif glxy_map.map_visible:
            renderer.galaxy_map.changed_since_last_frame = True
        
        # will set the camera's velocity back to what it should be if the player is holding a corresponding movement key
        if self.player_movement[1][0]:
            self.accelerate_camera(0, self.max_speed, True)
        elif self.player_movement[1][1]:
            self.accelerate_camera(0, -self.max_speed, True)
        if self.player_movement[0][0]:
            self.accelerate_camera(self.max_speed, 0, True)
        elif self.player_movement[0][1]:
            self.accelerate_camera(-self.max_speed, 0, True)

    def shake_camera(self):
        if global_vars.camera_shake > 0:
            int_shk = int(global_vars.camera_shake*10)
            self.accelerate_camera(randint(-int_shk, int_shk)/10, randint(-int_shk, int_shk)/10)
            global_vars.camera_shake = global_vars.camera_shake * 0.9
        elif global_vars.camera_shake < 0.1:
            global_vars.camera_shake = 0

class Renderer():
    def __init__(self):
        self.display_resolution = (1920,1080) # this needs to be changed to fetch from settings

        self.screen = p.display.set_mode(self.display_resolution)

        p.display.set_icon(p.image.load(resource_path("assets/icon.png")))

        self.camera_main = Camera()

        self.camera_map = Camera()

        self.active_camera = self.camera_main

        # texture loading
        print("Loading textures")
        try:
            self.tile_textures = {
                "Floor" : p.image.load(resource_path("assets/textures/tiles/Empty_Floor.png")).convert(),
                "Vent" : p.image.load(resource_path("assets/textures/tiles/Vent_Floor.png")).convert(),
                "Engine" : p.image.load(resource_path("assets/textures/tiles/engine.png")).convert(),
                "Pillar" : p.image.load(resource_path("assets/textures/tiles/wall_pillar.png")).convert(),
                "Battery" : p.image.load(resource_path("assets/textures/tiles/Battery.png")).convert(),
                "Reactor" : p.image.load(resource_path("assets/textures/tiles/Reactor.png")).convert(),
                "Storage Box" : p.image.load(resource_path("assets/textures/tiles/Storage_Box.png")).convert(),
                "Fuel Cell" : p.image.load(resource_path("assets/textures/tiles/Fuel_Cell.png")).convert(),
                "Lil Thruster" : p.image.load(resource_path("assets/textures/tiles/Lil_Thruster.png")).convert()
                }
        except:
            raise BaseException("CRASSHHH, error trying to load the tiles textures.")

        try:

            tint_colour =(27,33,13)

            self.tile_ghost_textures = { # the ones that show up when dragging and dropping
                }
            
            for tile_id in building.tile_kinds:
                tile = building.tile_kinds[tile_id]
                if tile.placeable:
                    # create a transparent tile with a green tint
                    size = tile.size
                    size = (size[0] * 64, size[1] * 64)
                    
                    tint = p.Surface((size))
                    tint.set_alpha(150)
                    tint.fill(tint_colour)

                    tinted_tile = p.Surface((size))
                    tinted_tile.blit(self.tile_textures[tile.name], (0,0))
                    tinted_tile.blit(tint, (0,0))

                    self.tile_ghost_textures[tile.name] = tinted_tile.convert_alpha()
            # create a red transparent tile for using in demo mode       
            tinted_red = p.Surface((64, 64))
            tinted_red.set_alpha(180)
            tinted_red.fill((60,23,20))# red tint
            self.tile_ghost_textures["Demo"] = tinted_red.convert_alpha()



            self.tile_caro_ghost_textures = { # the ones that show up in the tile carousel
                }
            
            for tile_id in building.tile_kinds:
                tile = building.tile_kinds[tile_id]
                if tile.placeable:
                    # create a transparent tile with a green tint
                    size = tile.size

                    scale_factor = 1

                    if size[1] > 1:
                        scale_factor = 1 / size[1]

                    size = (size[0] * 64 * scale_factor, 64)
                    
                    tint = p.Surface((size))
                    tint.set_alpha(150)
                    tint.fill(tint_colour)

                    tinted_tile = p.Surface((size))
                    tinted_tile.blit(p.transform.scale(self.tile_textures[tile.name], (size)), (0,0))
                    tinted_tile.blit(tint, (0,0))

                    self.tile_caro_ghost_textures[tile.name] = tinted_tile.convert_alpha()
             
        except Exception as e:
            raise BaseException(f"Error creating tile ghost textures: {str(e)}")

        try:    
            self.gui_textures = {
                # building GUI
                "Bld_Build_menu" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Build_Menu.png")), (1920, 150)).convert(),
                "Bld_Demo" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Demo.png")), (28, 28)).convert(),
                "Bld_Demo_Alt" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Demo_Alt.png")), (28, 28)).convert(),
                "Bld_Build" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Build.png")), (28, 28)).convert(),
                "Bld_Vent" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Vent.png")), (28, 28)).convert(),
                "Bld_Power" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Power.png")), (28, 28)).convert(),
                "Bld_Load" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Load.png")), (28, 28)).convert(),
                "Bld_Save" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/Save.png")), (28, 28)).convert(),
                "Bld_Engine" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/engine.png")), (30, 30)).convert_alpha(),
                "Bld_Mass" : p.transform.scale(p.image.load(resource_path("assets/textures/UI/Building/mass.png")), (30, 30)).convert_alpha(),

                # pause menu GUI
                "PM_Pause_Menu" : p.image.load(resource_path("assets/textures/UI/Pause Menu/Pause_Menu.png")).convert(),
                "PM_Quit" : p.image.load(resource_path("assets/textures/UI/Pause Menu/Quit.png")).convert(),
                "PM_Save" : p.image.load(resource_path("assets/textures/UI/Pause Menu/Save.png")).convert(),
                "PM_Load" : p.image.load(resource_path("assets/textures/UI/Pause Menu/Load.png")).convert(),
                "PM_Settings" : p.image.load(resource_path("assets/textures/UI/Pause Menu/Settings.png")).convert(),

                # Generic GUI
                "Gnrc_Box" : p.image.load(resource_path("assets/textures/UI/Generic/frame.png")).convert_alpha(),
                "Gnrc_Map" : p.image.load(resource_path("assets/textures/UI/Generic/map.png")).convert(),

                # Galaxy Map GUI
                "Glxy_stn_off" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_off.png")).convert_alpha(),
                "Glxy_stn_current" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_current.png")).convert_alpha(),
                "Glxy_stn_on_frame0" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_frame0.png")).convert_alpha(),
                "Glxy_stn_on_frame1" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_frame1.png")).convert_alpha(),
                "Glxy_stn_on_frame2" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_frame2.png")).convert_alpha(),
                "Glxy_stn_on_frame3" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_frame3.png")).convert_alpha(),

                # Station GUI
                "Stn_Main" : p.image.load(resource_path("assets/textures/UI/Galaxy Map/station_UI/main.png")).convert()
                }

        except:
            raise BaseException("Error loading gui textures")
        # no more texture loading

        # Puts stars in the background
        self.background = Background(self.display_resolution)

        # What renders the ship itself
        self.grid_map = GridMap_Renderer()


        # What renders different bits of ui
        self.building_ui = Building_UI(self.display_resolution, self.gui_textures)

        self.pause_ui = Pause_Menu()

        self.generic_ui = Generic_UI(self.gui_textures)

        self.galaxy_map = Galaxy_Map()

        self.main_ticker = Ticker(31, 240, ["Game saved!", "Game loaded!", "Load failed, no file found."])

        # Small debug feature used to display the FPS and such
        self.debug_font = p.font.Font(resource_path("assets/Pixel.ttf"), 16)



    def standard_frame(self, build_mode):
        self.active_camera = self.camera_main

        self.screen.blit(self.background.render(self.active_camera.pos, self.display_resolution), (0,0))

        self.grid_map.render(self.active_camera, self.tile_textures, self.screen) # middle layer
        
        # ui layer
        if build_mode:
            self.building_ui.render_building_ui(self.screen, self.gui_textures, self.tile_ghost_textures, self.tile_caro_ghost_textures, self.active_camera)
        
        else:
            self.screen.blit(self.generic_ui.render(self.gui_textures), (1870, 0))
            
        self.screen.blit(self.main_ticker.render(), (5,5))

    

    def galaxy_map_frame(self):
        self.active_camera = self.camera_map

        self.screen.blit(self.background.render(self.active_camera.pos, self.display_resolution), (0,0))

        self.screen.blit(self.galaxy_map.render(self.active_camera, self.gui_textures, self.display_resolution), (0,0)) # map

        self.screen.blit(self.generic_ui.render(self.gui_textures), (1870, 0)) #ui




    def render_tick(self, build_mode, dt, save_name, fps): # render the current (next?) frame
        self.screen.fill((0,0,0))

        self.active_camera.shake_camera()
        self.active_camera.move_camera(self)

        if glxy_map.map_visible:
            self.galaxy_map_frame()
        else:
            self.standard_frame(build_mode)

        if pause_menu.paused: # pause menu should always be able to show up, and be on top
            self.screen.blit(self.pause_ui.render(self.gui_textures), (810, 240))


        #debug text
        self.screen.blit(self.debug_font.render(("FPS = " + str(round(fps))), True, (0,255,0)), (10,210))


        self.screen.blit(self.debug_font.render(("Save = "+save_name), True, (0,255,0)), (10,230))


        if pause_menu.typing_save_name:
            self.screen.blit(self.debug_font.render(("Typing save name..."), True, (0,255,0)), (10,250))
        
        self.screen.blit(self.debug_font.render(("Pressing E allows you to spawn in fuel via the terminal/console btw"), True, (0,255,0)), (10,270))


        p.display.flip()