"""
Manages the states of all the different stations
"""

import json, galaxy.contracts
from resource_path import *
from random import randint

from math import sin

station_kinds = json.load(open(resource_path("config_jsons/stations.json")))

with open(resource_path("config_jsons/station_names.txt")) as f:
    station_names = f.readlines()
    for i in range(len(station_names)):
        station_names[i] = station_names[i][0:-1] + " " # take the new line character off

class Station:
    pos_offset = (300, 200)
    pos_distancing = 400 # ~how many units between each station
    pos_rnd = int(pos_distancing * 0.75)
    threat_level_difficulty = 0.5

    def __init__(self, station_id, row, column, name, kind = -1): # default of -1 to choose a random one
        if kind == -1:
            self.kind = randint(0, len(station_kinds) - 1)
        else:
            self.kind = kind
        
        self.name = name

        self.attached_contracts = []

        self.station_id = station_id


        x = row * Station.pos_distancing
        x = randint(x, x + Station.pos_rnd)

        y = column * Station.pos_distancing
        y = randint(y, y + Station.pos_rnd)

        self.threat_level = (0.5 * (2 * sin(x * 100/Station.pos_distancing) + 0.03 * x * 100/Station.pos_distancing) + (2 * sin(y * Station.pos_distancing/100) + 0.01 * y * Station.pos_distancing/100) + randint(-20, 20)) * Station.threat_level_difficulty # not how dangerous the station itself is, but rather used to average between two stations for the links threat level
        
        self.threat_level = min(100, max(10, self.threat_level)) # max level of 100, and a min of 10 (mainly so the debug colours work rn lol)

        self.pos = (x + Station.pos_offset[0], y + Station.pos_offset[1]) # the additions are an offset to centre the map in the UI ;)



stations = []
station_links = {}


def create_stations(num_columns, num_rows): # used when a new save is started, creates every station in the 2d grid
    unused_names = station_names.copy() # i know this is inefficent as anything but it works...
    times_names_wrapped = 0 # like how many times ive run out of unused names

    for row in range(num_rows):
        for column in range(0, num_columns):
            station_id = row * num_columns + column

            if len(unused_names) == 0:
                unused_names = station_names.copy()
                times_names_wrapped += 1
            index = randint(0, len(unused_names)-1)
            name = unused_names.pop(index)

            temp = times_names_wrapped
            while temp > 0: # turn temp into roman numerals (Max chacter of L) - REALLY unoptimised but it only gets ran when making a new save so meh
                if temp // 50 > 0:
                    name += "L"
                    temp -= 50
                elif temp // 40 > 0:
                    name += "XL"
                    temp -= 40
                elif temp // 10 > 0:
                    name += "X"
                    temp -= 10
                elif temp // 9 > 0:
                    name += "IX"
                    temp -= 9
                elif temp // 5 > 0:
                    name += "V"
                    temp -= 5
                elif temp // 4 > 0:
                    name += "IV"
                    temp -= 4
                elif temp // 1 > 0:
                    name += "I"
                    temp -= 1

            stations.append(Station(station_id, row, column, name))

    for row in range(num_rows):
        for column in range(0, num_columns): # add jobs after making them so they can look at ALL of the stations instead of just the current ones made
            station_id = row * num_columns + column
            max_contracts = station_kinds[stations[station_id].kind]["size"]

            for contract in range(0, max_contracts):
                stations[station_id].attached_contracts.append( # assign the contract ID to the station ID to link em
                    galaxy.contracts.create_new_contract(station_id, len(stations)) # create the contract and return its ID
                    )
    
