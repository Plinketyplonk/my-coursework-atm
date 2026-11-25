import building


# this should be loaded from a json file but im not doing that on a phone
item_defs = {
	"Steel Plate" : {
	"max_hp" :  20,
	"value" : 5,
	"mass" : 4,
	"bulk" : 1,
	"display_name" : "#Items/steel_plate_1"
	}
}

class Item():
	def __init__(self, item_kind : int):
		self.item_kind = item_kind
		