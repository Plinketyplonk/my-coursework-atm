"""
Saves and loads the current state of the game
"""

import pickle, os, galaxy.stations, galaxy.contracts, galaxy.galaxy_map, building
import numpy as np
from resource_path import *

version = [0, 0, 2] # only started doing versions about 3 months in but whatever?

current_save = ""

# ---------------------------------------------- SAVING ----------------------------------------------

max_autosaves = 5

autosave_timer = 0

autosave_interval = 600 # save every x seconds - default is 10 minutes



def generate_new_save(save_name): # used to create the directories in a save folder
    print("saved to",f"saves/{save_name}")
    try:
        directory_name = resource_path(f"saves/{save_name}")
        if not os.path.isdir(directory_name): # if the folder does not exist
            os.makedirs(directory_name)

    except PermissionError:
        print(f"Permission denied: Unable to create main save folder.")
    
    try:
        with open(resource_path(f"saves/{save_name}/version.dat"), "wt") as f:
            f.write(str(version))
    except PermissionError:
        print(f"Permission denied: Unable to save version.dat")

    folders_to_make = ["ships"] # currently only 1 folder because i cant think of anything else id need
    try:
        for folder in folders_to_make:
            directory_name = resource_path(f"saves/{save_name}/{folder}")
            if not os.path.isdir(directory_name): # if the folder does not exist
                os.makedirs(directory_name)

    except PermissionError:
        print(f"Permission denied: Unable to create sub-save folder'{directory_name}'.")



def save_ship(save_name):
    file_path = f"saves/{save_name}/ships/ship.pickle"
    with open(resource_path(file_path), "wb") as f:
        try:
            packed_arrays = building.tile_kind_map, building.tile_origin_map, building.tile_totals, building.ship_mass ,building.mass_limit ,building.thrust_limit ,building.thrust_used, building.fuel_limit, building.fuel_level
            pickle.dump(packed_arrays, f)
        except:
            print('Ship save error')


def save_stations(save_name):
    file_path = f"saves/{save_name}/stations.pickle"
    with open(resource_path(file_path), "wb") as f:
        try:
            packaged_data = galaxy.stations.stations, galaxy.stations.station_links, galaxy.galaxy_map.current_station
            pickle.dump(packaged_data, f)
        except:
            print('Station save error')


def save_contracts(save_name):
    file_path = f"saves/{save_name}/stations.pickle"
    with open(resource_path(file_path), "wb") as f:
        try:
            pickle.dump(galaxy.contracts.active_contracts, f)
        except:
            print('Contracts save error')

def log_crash(crash_exception, save_name): # only used on a crash obvs
    if crash_exception != "":
        file_path = f"saves/{save_name}/crash.txt"
        with open(resource_path(file_path), "wt") as f:
            try:
                f.write("This save is likely to be corrupted, I'd recomend reverting to an older save/autosave. Mb for the sloppy coding ig lol\n\nCrash caused by:\n")
                f.write(crash_exception)
            except:
                print('Crash save error (OH NO)')



def next_autosave():
    with open(resource_path("saves/next_autosave.dat"), "rt") as f: # find which autosave to use
        autosave_number = f.read()
        save_name = f"autosave_{autosave_number}"


    with open(resource_path("saves/next_autosave.dat"), "wt") as f: # increment the number (with wrap around) and store it for the next autosave
        next_number = str((int(autosave_number) + 1) % max_autosaves)

        f.write(next_number)
    
    return save_name



def save_game(crash_exception, save_name = ""):
    global current_save

    if save_name == "":
        if current_save == "":
            save_name = next_autosave()
        else:
            save_name = current_save

    generate_new_save(save_name)
    log_crash(crash_exception, save_name)
    save_ship(save_name)
    save_stations(save_name)
    #save_contracts()

    return True




def autosave(delta_time, crash_exception = "", forced = False): # create a save on the least recently accessed autosave (to maintain a few recent backups) - IF the timer is at the right interval unless forced autosave
    global autosave_timer

    if autosave_timer >= autosave_interval or forced:
        if crash_exception != "":
            save_name = "crash_save"
        else:
            save_name = next_autosave()

        save_game(crash_exception, save_name=save_name)

        autosave_timer = 0

    else:
        autosave_timer += delta_time # from main

# ---------------------------------------------- LOADING ----------------------------------------------

def load_ship(save_name):
    file_path = f"saves/{save_name}/ships/ship.pickle"
    with open(resource_path(file_path), "rb") as f:
        #try:
            loaded_kind, loaded_origin, loaded_tile_totals, building.ship_mass ,building.mass_limit ,building.thrust_limit ,building.thrust_used, building.fuel_limit, building.fuel_level = pickle.load(f) # loads literally everything i think
        
            building.tile_kind_map[:] = loaded_kind[:]
            building.tile_origin_map[:] = loaded_origin[:] # think i totally wasted time trying to do all this because the ship wasnt loading because i wasnt telling it to update the surface lmfao
            building.tile_totals[:] = loaded_tile_totals[:]
        #except:
            #print('Ship load error')


def load_stations(save_name):
    file_path = f"saves/{save_name}/stations.pickle"
    with open(resource_path(file_path), "rb") as f:
        #try:
        
            galaxy.stations.stations.clear()
            galaxy.stations.station_links.clear()

            loaded_stations, loaded_links, ld_crnt_stn = pickle.load(f)

            galaxy.stations.stations.extend(loaded_stations)
            galaxy.stations.station_links.update(loaded_links)
            galaxy.galaxy_map.current_station = ld_crnt_stn
        #except:
            #print('Station load error')

def load_save():
    global current_save
    save_name = current_save # kinda useless ngl

    directory_name = resource_path(f"saves/{save_name}")

    if os.path.isdir(directory_name): # if the save file exists
        print("Loading")

        load_ship(save_name)
        load_stations(save_name)
        return True
    else:
        print(f"No save file called {save_name} found.")
        return False
