"""
All of the code regarding contracts
"""

import json, global_vars, entities
from resource_path import *
from random import randint



possible_contracts = json.load(open(resource_path("config_jsons/contracts.json")))

active_contracts = []



class Base_Contract:
    def __init__(self, contract_kind, station_issuing):
        """
        :param contract_kind: a number to reference the contract kind from possible_contracts
        """
        self.contract_kind = contract_kind # refernce to the possible_contracts list
        self.accepted = False
        self.station_issued_from = station_issuing # who gave da contract (number ID)



    def accept_contract(self):
        self.accepted = True
        global_vars.balance += self.strt_bonus



    def complete_contract(self):
        self.accepted = True
        global_vars.balance += self.finish_reward





class Delivery_Contract(Base_Contract):
    def __init__(self, contract_kind, station_issuing):

        self.itm_2_dlv = possible_contracts[contract_kind]["item"]

        itms_rnge = possible_contracts[contract_kind]["number_of_items"]
        self.no_itms_2_dlv = randint(itms_rnge[0], itms_rnge[1])

        self.strt_bonus = (possible_contracts[contract_kind]["upfront_multiplier"] 
                            * entities.Item_Types[possible_contracts[contract_kind]["item"]].credit_value
                            * self.no_itms_2_dlv) # multiply the value of the cargo by the multiplier
        
        self.finish_reward = (possible_contracts[contract_kind]["reward_multiplier"] 
                            * entities.Item_Types[possible_contracts[contract_kind]["item"]].credit_value
                            * self.no_itms_2_dlv) # multiply the value of the cargo by the OTher multiplier


        # find the destination to go to (can't be itself and needs to be a valid place)
        self.destination = -1

        Base_Contract.__init__(self, contract_kind, station_issuing) # inherit same stuff from the main class





def create_new_contract(station_issuing, stations_len):
    global active_contracts

    contract_kind_num = randint(0, len(possible_contracts) - 1)


    if possible_contracts[contract_kind_num]["type"] == "delivery":
        new_contract = Delivery_Contract(contract_kind_num, station_issuing)

    else:
        raise Exception("THERE ARE NO OTHER CONTRACT TYPES WDYMMMMMMMMMMMMMMMMMMMM")


    active_contracts.append(new_contract)
    
    contract_id = len(active_contracts) - 1
    
    return contract_id
