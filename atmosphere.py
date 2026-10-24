"""
All of the code relating to the pressure/air grid

NOT BEING USED AT ALL FOR PROTOTYPE ONE, MAYBE NOT TWO EITHER

"""

import numpy as np

class room():
    def __init__(self, identifier):
        self.pressure = 0
        self.connected_vents = []
        self.connected_rooms = []
        self.identifier = ""
    
    def generate_identifier(room_graph):
        # finds the largest ID number being used and sets the room to the next one up
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! NEED TO REMEMBER TO SET UP SOME KIND OF CLEANUP SO YOU DONT HAVE ROOM 1 TRILLION IF YOUVE BEEN PLAYING AGES! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        largest = 0
        for room in room_graph:
            largest = max(largest, room)

        room = largest + 1

class air_grid():
    def __init__(self, grid_size):
        self.pressure_array = np.zeros(grid_size, dtype="i") # creates the inital grid of points, all set to 0 to indicate they're in a vacuum

        self.room_graph = { # which vents are connected to each other
            # "1" : ["2", "3"], # just an e.g., showing that room 1 is connected to room 2 and 3 and thus exchanges pressure between them (and that 3 and 4 are exclusively connected)
            # "2" : ["1"], # this means that this room is connected to room 1 by a vent + duct (could either be connected to the one )
            # "3" : ["2", "4"], # this means that this room is connected to room 1 via a vent + duct and then room 4 by a seperate one (since 1 doesnt share room 4 with 3)
            # "4" : ["3"]
        }
    
    def check_pressurisation(self, start_pos, grid):
        max_depth = 10
        current_depth = 0

        visited = [] # a list of nodes already checked - prevents overlap (which would make the BFS run until the depth runs out even if the room was just like 2x1 lol)
        queue = [start_pos] # nodes to check

        while current_depth < max_depth:
            pos = queue[0]
            visited.append(pos)
            if grid[pos[0]][pos[1]] == "None":
                return 0 # This is just a vacuum, nothing special here
            else:
                # queue the tiles in all cardinal directions to visit, unless they've already been seen
                if not pos in visited:
                    queue.append(pos)