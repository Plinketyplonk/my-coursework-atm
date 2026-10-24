"""
Used to generate the map and store the data related to links between stations
And also handle movement checks
"""

import galaxy.stations, random, render, math, building, sounds, global_vars
import pygame as p
import numpy as np

current_station = 0 # where the player is rn

map_visible = False

class Generate_New_Map:
    num_rows = 20
    num_columns = 20


    def connect_stations(station_1, station_2):
        galaxy.stations.station_links[station_1].append(station_2)
        galaxy.stations.station_links[station_2].append(station_1)



    def dfs_for_unconnected(current = 0, visited = None): # depth first search to check if there are any unconnected nodes
        visited.append(current) # mark the current node as visited

        for connection in galaxy.stations.station_links[current]: # check each connection to the node

            if connection not in visited: # if the connected node hasnt been visited yet
                visited = Generate_New_Map.dfs_for_unconnected(connection, visited) # then repeat from there

        return visited



    def generate_map(seed):
        print(f"Generating map connections with seed {seed}")
        num_rows = Generate_New_Map.num_rows
        num_columns = Generate_New_Map.num_columns

        map_seed = seed
        complete = False

        galaxy.stations.station_links = {}
        galaxy.stations.stations = []
        
        
        galaxy.stations.create_stations(num_columns, num_rows) # creates all the unconnected stations


        random.seed(map_seed)

        for row in range(num_rows):# give an empty list of connections for unconnected nodes
            for column in range(num_columns):
                station_id = row * num_columns + column
                galaxy.stations.station_links[station_id] = []

        for row in range(num_rows):

            # connect stations
            already_connected = []
            if row != num_rows - 1: # 1st row has nothing to connect back to
                for i in range(random.randint(6,8)): # connect between next row
                    column = random.randint(0, num_columns - 1)
                    station_id = row * num_columns + column # chooses a new random station from the row

                    max_depth = 5
                    depth = 0
                    while station_id in already_connected and depth < max_depth: # if it randomly chose one already selected
                        column = column + 1
                        if column > num_columns - 1:
                            column = 0

                        station_id = row * num_columns + column # chooses a new random station from the row

                    connected_station_id = (row + 1) * num_columns + column

                    if column != 0 and column < num_columns - 1:
                        connected_station_id += random.randint(-1, 1)

                    
                    Generate_New_Map.connect_stations(station_id, connected_station_id)# and connects it to the respective one behind it
                    already_connected.append(station_id)
                    already_connected.append(connected_station_id)

                    # connect neibours
                    if column > 0:
                        Generate_New_Map.connect_stations(station_id, station_id - 1)
                        already_connected.append(station_id - 1)
                    if column < num_columns - 1:
                        Generate_New_Map.connect_stations(station_id, station_id + 1)
                        already_connected.append(station_id + 1)
                    

            for column in range(num_columns):
                station_id = row * num_columns + column

                if (not station_id + 1 in already_connected) and column < num_columns - 1: # if the next row down is not connected and not final col
                    Generate_New_Map.connect_stations(station_id, station_id + 1)
                    already_connected.append(station_id)
                    already_connected.append(station_id + 1)
                

        visited = Generate_New_Map.dfs_for_unconnected(visited=[])
        max_search_depth = 2

        while len(visited) != num_columns * num_rows and max_search_depth > 0:
            max_search_depth -= 1
            # connect the unconnected ones
            for station_id in range(0, num_columns * num_rows):
                if station_id not in visited:
                    if station_id < num_columns: # if its on the first column connect forward
                        connected_station_id = station_id + num_columns
                        Generate_New_Map.connect_stations(station_id, connected_station_id)

                    else: # else connect backwards
                        connected_station_id = station_id - num_columns
                        Generate_New_Map.connect_stations(station_id, connected_station_id)

                    print(f"Connected {station_id} to {connected_station_id} (forced)")

                    visited = Generate_New_Map.dfs_for_unconnected(visited=[]) # recheck if all nodes are connected
        
        if max_search_depth == 0:
            raise BaseException(f"Error in the map generation, the seed {map_seed} generated an impossible map somehow. Might wanna look into that...\n\nIf you're an end user wondering what to do, just use a different seed (and pls send a report ;P)!")
                    
        print("Map Done :D")



def fetch_hovered_connection(mouse_pos, camera):
    mouse_pos = (mouse_pos[0] - galaxy.stations.Station.pos_offset[0] - camera.pos[0], mouse_pos[1] - galaxy.stations.Station.pos_offset[1] - camera.pos[1]) # adjust the mouse pos by the offset
    ps_d = galaxy.stations.Station.pos_distancing

    station_id = (mouse_pos[0] // ps_d) * Generate_New_Map.num_columns + (mouse_pos[1] // ps_d) # calculate which stations 'tile' the mouse is in

    if station_id > len(galaxy.stations.stations) - 2: # if you go way over to the far right side of the screen, stops it from crashing out
        station_id = len(galaxy.stations.stations) - 1

    return int(station_id)


def calc_fuel_needed(station_id):
    distance = math.sqrt((galaxy.stations.stations[station_id].pos[0] - galaxy.stations.stations[current_station].pos[0]) **2 + (galaxy.stations.stations[station_id].pos[1] - galaxy.stations.stations[current_station].pos[1]) **2)

    fuel_needed = int(distance / (galaxy.stations.Station.pos_distancing // 10))
    fuel_needed = fuel_needed * building.fuel_multiplier() # more engines means more fuel used

    return fuel_needed



def gather_stats_for_info(mouse_pos, camera):
    station_id = fetch_hovered_connection(mouse_pos, camera)

    stn_obj = galaxy.stations.stations[station_id]

    pos = stn_obj.pos
    thrt_lvl = stn_obj.threat_level
    kind = f"Kind: {galaxy.stations.station_kinds[stn_obj.kind]['name']}"

    if station_id == current_station or not station_id in galaxy.stations.station_links[current_station]:
        fuel_needed = "Fuel: N/A"
    else:
        fuel_needed = calc_fuel_needed(station_id)
        if fuel_needed != 0:
            fuel_needed = f"Fuel: {fuel_needed}"
        else:
            fuel_needed = "Fuel: N/A"

    contract_count = f"Contract Count: {len(stn_obj.attached_contracts)}"

    name = stn_obj.name

    return pos, thrt_lvl, kind, fuel_needed, contract_count, name



def jump_to_new_station(mouse_pos, camera):
    global current_station

    print(mouse_pos)
    if p.Rect((1880,10),(30,30)).collidepoint(mouse_pos):
        return False, -1 # the player obvs just pressed the button so like don't make them try jump?

    error_ticker = -1

    station_id = fetch_hovered_connection(mouse_pos, camera)

    if station_id in galaxy.stations.station_links[current_station]:

        if building.mass_limit >= building.ship_mass and building.mass_limit != 0:
            if building.thrust_limit >= building.thrust_used:
                fuel_needed = calc_fuel_needed(station_id)

                if building.fuel_level >= fuel_needed: # check if your ship has enough fuel to make the jump
                    building.fuel_level -= fuel_needed # spend the fuel

                    current_station = station_id # move you
                    global_vars.camera_shake += 10
                    return True, error_ticker
                else:
                    print("not enough fuel", fuel_needed)
                    error_ticker = 0
            else:
                print("not enough engine power")
                error_ticker = 2
        else:
            print("too heavy")
            error_ticker = 1
    else:
        print("station out of range")
        error_ticker = 3
    
    sounds.sound.ui_sounds["generic_error"].play()
    return False, error_ticker



def toggle_map():
    global map_visible
    map_visible = not map_visible
    return map_visible


Generate_New_Map.generate_map(random.randint(0,999999))