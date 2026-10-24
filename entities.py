
# THIS MODULE IS NOT BEING USED MUCH FOR PROTOTYPE ONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""
Used to manage all the games entities, including items and NPCs
"""

import json
import pygame as p
from resource_path import *

class Animated_Texture():
    def __init__(self, animations):
        """
        The animation works by taking the current animation frame, then referencing the list
        if the item is an image, it will set the entity to render using that image, if it is
        "True" then the last fetched image will be used.

        EVERY single animated texture should include an "Idle" animation

        Example on how to format animations parameter:
        {
        "Idle" : [
            "assets/entities/example/idle/frame00",
            True,
            True,
            "assets/entities/example/idle/frame01",
            True,
            True,
            "assets/entities/example/idle/frame02",
            True,
            True
            ]
        }
        """

        def load_animation(animations):
            for animation in animations:
                for frame in animation:
                    if frame: # true means ignore
                        pass

        self.animations = load_animation(animations)



class Entity:
    def __init__(self, name, texture_to_use, animated = False):
        self.animated = animated
        self.frame = 0
        self.state = "idle" # default state
        self.name = name

        if not animated:
            self.texture = texture_to_use
        
        else:
            self.animation = Animated_Textures[texture_to_use]

    def start_animation(self, animation_name):
        if animation_name in Animated_Textures[self.texture].animations:
            self.current_animation = animation_name
            self.frame = 0
        else:
            print("Animation:",animation_name,"does not exist.")



class Item(Entity):

    def __init__(self, name, texture_to_use, credit_value = 0, animated = False):
        self.credit_value = credit_value

        Entity.__init__(self, name, texture_to_use, animated) # inherit same stuff from the main class



def load_entity_types():
    # ITEMS
    item_types = {} # using a dictionary despite having a numerical id since dictionaries use hashed values (which are O(1) supposedly)
    Animated_Textures = {}

    with open(resource_path("entities/items.json")) as f:
        json_from_file = json.loads(f.read()) # need to test this but should return the json data as python data types


    # put all the items into memory
    for item in json_from_file:
        
        if json_from_file[item]["animated"]: # if the item has an animated texture
            Animated_Textures[item] = json_from_file[item]["animations"]
            texture = item # just give the name used in the dictionary of animated textures
        
        else: # static texture
            texture = json_from_file[item]["texture"]
            p.image.load(open(resource_path(texture))).convert_alpha()

        item_types[item] = Item(
            name = item,              
            animated = json_from_file[item]["animated"],
            credit_value = json_from_file[item]["credit_value"],
            texture_to_use = texture # either a straight up png, OR the name of an animated texture object
            ) # should store the items relevent data as an object

    return item_types, Animated_Textures



Item_Types, Animated_Textures = load_entity_types()

max_floating_items = (100)
floating_items = [] # this is a list of all the items that are dropped

class Floating_Item:
    def __init__(self, item_type):
        self.item_type = item_type
        self.angle = 0
        self.texture = Item_Types[item_type].texture

        self.rect_center = self.texture.get_rect().center # used because this texture is rotated

    def generate_rotated_texture(self):
        original_texture = Item_Types[self.item_type].texture

        self.texture = p.transform.rotate(original_texture, self.angle)

        x, y = self.rect.center  # Save its current center.

        self.rect = self.texture.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def blit(camera, screen):
        screen.blit()