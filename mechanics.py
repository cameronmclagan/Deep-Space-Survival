import sys,re,math,string

#from types import ListType, TupleType

import message_center

for channel_name in ["heading","subheading","description","item","success","failure"]:
	message_center.add_channel(channel_name)

import game_state, command_line, xml_content_loader, inspect

id_number = 0
def get_unique_id():
	global id_number
	id_number += 1
	return str(id_number)

######################################
# ITEM MANAGEMENT & CLASSIFICATION
######################################
class MarkerBoundObject:
	def __init__(self, name, use_identifier=None, use_game_state=None):
		self.formatted_name = name.lower().replace(" ", "_")
		self.formatted_name = re.sub(r"\W","",self.formatted_name)
		self.unique_name = self.formatted_name + "_" + str(get_unique_id())

class VisibleObject:
	def __init__(self, description = None):
		self.description = description
	
	def generate_description(self):
		if self.description == None:
			message_center.add_message(str(self.name).capitalize() + " is rather difficult to describe.")
		else:
			message_center.add_message(channel="heading",message=self.name)
			message_center.add_message(" \n" + self.description)
	
	def on_focus(self):
		describe(self)

######################################
# GAME-LEVEL OBJECT TYPES
######################################

class Item(MarkerBoundObject, VisibleObject):
	focus_commands = {}

	def __init__(self, name, identifier, description=None):
		self.name = name
		self.identifier = identifier

		global item_commands
		MarkerBoundObject.__init__(self, self.name)
		VisibleObject.__init__(self, description)
		
	def generate_description(self):
		message_center.add_message(channel="heading",message=self.name)
		if self.description != None:
			message_center.add_message(channel="default", message=" \n" + self.description + "\n")
		else:
			message_center.add_message(channel="default", message=" \n")
		sub_markers = game_state.current_state.get_children_of(self.identifier)
		if len(sub_markers)> 0:
			message_center.add_message(channel="subheading",message="Looking inside, you find...")
			message_center.add_message(channel="item", message="\n".join(sub_markers))

class MobileItem(Item):
	focus_commands = {}

class Weapon(MobileItem):
	focus_commands = {}
	pass

class Magazine(MobileItem):
	focus_commands = {}
	pass

class StackableItem(MobileItem):
	focus_commands = {}

	def __init__(self, name, stack_size=1, description=None):
		self.original_name = name
		self.stack_size=stack_size
		MarkerBoundObject.__init__(self, name)
		VisibleObject.__init__(self, description)

	@property
	def name(self):
		return "{1} x{0}".format(str(self.stack_size),self.original_name)
	
	def split_stack(self, number):
		if stack_size < 2:
			pass

class Ammunition(StackableItem):
	focus_commands = {}

class Food(StackableItem):
	focus_commands = {}
	pass

class Container(MobileItem):
	focus_commands = {}
	pass

class Room(MarkerBoundObject, VisibleObject):
	focus_commands = {}
	def __init__(self, name, description=None, identifier=None):
		self.name = name
		self.identifier = identifier
		MarkerBoundObject.__init__(self, name)
		VisibleObject.__init__(self, description)
		
	def generate_description(self):
		lines = []
		message_center.add_message(channel="heading",message=self.name)
		if self.description != None:
			message_center.add_message(channel="default", message=" \n" + self.description + "\n")
		else:
			message_center.add_message(channel="default", message=" \n")
		message_center.add_message(channel="subheading",message="Looking around, you find...")
		message_center.add_message(channel="item", message="\n".join([o.name for o in [game_state.current_state.get_object(identifier) for identifier in game_state.current_state.get_children_of(self.identifier)]]))
		return lines

class ActionRecord:
	def __init__(self, duration=1, skills_trained=(), skills_studied=(),):
		pass

class Hand(MarkerBoundObject, VisibleObject):
	focus_commands = {}
	
	def __init__(self, identifier, name):
		self.identifier = identifier
		self.name = name
		MarkerBoundObject.__init__(self, self.name)
		
		self.formatted_name = self.formatted_name.replace("your","my")
		
		self.held_item = None
		self.max_held_size = 1
		self.max_held_weight = 1
	
	def try_to_hold_item(self, item):
		if not isinstance(item, Item):
			item = game_state.current_state.get_object(item)
		
		if self.held_item != None:
			message_center.add_message(channel="fail", message="{0} is already holding {1}.".format(self.name, self.held_item.name))
			return False
		
		if hasattr(item, "size") and item.size > self.max_held_size:
			message_center.add_message(channel="fail", message="{0} is too large for {1} to hold.".format(item.name, self.name))
			return False
		
		if hasattr(item, "weight") and item.weight > self.max_held_weight:
			message_center.add_message(channel="fail", message="{0} is too heavy for {1} to hold.".format(item.name, self.name))
			return False
		
		self.held_item = item
		game_state.current_state.move_marker(item.identifier, self.identifier)
		message_center.add_message(channel="default", message="{0} is now holding {1}.".format(self.name, self.held_item.name))
		return True
	
	def release_held_item(self):
		if self.held_item == None:
			message_center.add_message(channel="fail", message="{0} is not holding anything.".format(self.name))
			return None
		
		released_item = self.held_item
		game_state.current_state.move_marker(released_item.identifier, None)
		self.held_item = None
		message_center.add_message(channel="default", message="{0} is now empty.".format(self.name, self.held_item.name))
		return released_item
		
	@property
	def description(self):
		if self.held_item == None:
			return "This hand is not holding anything."
		else:
			return "This hand is holding {0}.".format(self.held_item.name)
		

class Pocket(MarkerBoundObject, VisibleObject):
	focus_commands = {}
	
	def __init__(self, identifier, name):
		self.identifier = identifier
		self.name = name
		MarkerBoundObject.__init__(self, self.name)
		
		self.capacity = 1
	
	def add_item(self, item):
		pass
	

damage_message_template = string.Template("{white}$name{reset} is $verbed for {red}$number damage{reset} - New HP Total: $hp_string")
healing_message_template = string.Template("{white}$name{reset} is $verbed for {green}$number healing{reset} - New HP Total: $hp_string")
class PlayerCharacter(MarkerBoundObject, VisibleObject):
	focus_commands = {}

	def __init__(self, identifier, name):
		self.identifier = identifier
		self.name = name
		self.colored_name = "#628FCF#" + self.name + "#XXXXXX#"
		MarkerBoundObject.__init__(self, self.name)
		self.max_hp = 50
		self.cur_hp = 13
		VisibleObject.__init__(self)
	
	def take_damage(self, amount, verbed="hit"):
		global damage_message_template
		sub_dict = {"name":self.name,"verbed":verbed}
		self.cur_hp -= amount
		if self.cur_hp >= 0:
			sub_dict["number"] = amount
			sub_dict["hp_string"] = self.generate_hp_string()
		else:
			overkill = 0 - self.cur_hp
			real_damage = amount-overkill
			self.cur_hp = 0
			sub_dict["number"] = real_damage
			sub_dict["hp_string"] = self.generate_hp_string()
#			message_center.add_message(channel="default",message="%s was #{f57900}#overkilled#{XXXXXX}#, wasting #{f57900}#%i#{XXXXXX}# damage!" % (self.colored_name, overkill))
		message_center.add_message(channel="default",message=damage_message_template.substitute(sub_dict))

	
	def be_healed(self, amount, verbed="hit"):
		global healing_message_template
		sub_dict = {"name":self.name,"verbed":verbed}
		self.cur_hp += amount
		if self.cur_hp <= self.max_hp:
			sub_dict["number"] = amount
			sub_dict["hp_string"] = self.generate_hp_string()
		else:
			overheal = self.cur_hp - self.max_hp
			real_heal = amount-overheal
			self.cur_hp = self.max_hp
			sub_dict["number"] = real_heal
			sub_dict["hp_string"] = self.generate_hp_string()
#			message_center.add_message(channel="default",message="%s was #{f57900}#overhealed#{XXXXXX}#, wasting #{FFFF99}#%i#{XXXXXX}# healing!" % (self.colored_name, overheal))
		message_center.add_message(channel="default",message=healing_message_template.substitute(sub_dict))
			

	def generate_hp_string(self):
		fraction = float(self.cur_hp)/float(self.max_hp)
		colors = ("{red}","{orange}","{yellow}","{green}")
		index = int(round(fraction*float(len(colors)-1)))
		return "%s%i/%i (%i%%)" % (colors[index], self.cur_hp, self.max_hp, round(fraction*100.0))

	def generate_description(self):
		message_center.add_message(channel="heading",message="Your Inventory")
		message_center.add_message(channel="default", message="These are the items you have found in your mission so far.")
		message_center.add_message(channel="subheading",message="You are carrying...")
		id_list = game_state.current_state.get_children_of(self.identifier)
		if len(id_list) > 0:
			message_center.add_message(channel="item", message="\n".join([game_state.current_state.get_object(ident).name for ident in id_list]))
		else:
			message_center.add_message(channel="item", message="Nothing at all.")

class PlayerInventory:
	pass

################################################################################

create_object_type_mappings = {
	"item":Item,
	"room":Room,
	"door":Item,
	"weapon":Weapon,
	"container":Item,
	"player_character":PlayerCharacter,
	"hand":Hand,
}

def create_object(object_type, object_args, object_children, object_location):
	global create_object_type_mappings
	working_args = {}
	waiting_objects = list(object_children)
	if "template" in object_args:
		template = game_state.current_state.template_index[object_args["template"]]
		working_args.update(template.args)
		for child in template.children:
			waiting_objects.append(child)

	working_args.update(object_args)

	if "desc_id" in working_args:
		working_args["description"] = game_state.current_state.text_storage[working_args["desc_id"]]
	
	allowable_args = inspect.getargspec(create_object_type_mappings[object_type].__init__).args

	final_args = {}
	for key, val in working_args.items():
		if key in allowable_args:
			final_args[str(key)] = val
	
	game_object = create_object_type_mappings[object_type](**final_args)
	
	game_state.current_state.create_marker(identifier=final_args["identifier"], game_object=game_object, location=object_location)
	
	for o in waiting_objects:
		create_object(o.type, o.args, o.children, game_object.identifier)

################################################################################

###############
### FILTERS ###
###############

def class_type_filter(class_type):
	return lambda x: isinstance(x.object, class_type)

from command_line import Command, GameObjectArgumentHandler

### COMMANDS ###
room_commands = Room.focus_commands
scenery_commands = {}
item_commands = Item.focus_commands
mobile_item_commands = MobileItem.focus_commands
weapon_commands = Weapon.focus_commands
magazine_commands = Magazine.focus_commands
ammunition_commands = Ammunition.focus_commands

### describe ###
# Generate description for something
# This actually doesn't have it's own command; there are several
# essentially synonymous commands based on this function.
def describe(*args):
	for x in args:
		if hasattr(x,'generate_description'):
			x.generate_description()
		else:
			message_center.add_message(channel="failure", message="You can't actually see %s." % x.name)

def describe_focus(*args):
	target = game_state.current_state.focus_stack[-1].object
	describe(target)

#####################
### ROOM COMMANDS ###
#####################

### inventory ###
# Focus on the player's inventory marker.
def list_player_inventory(*args):
	game_state.current_state.focus_on_marker("the_player")

Command("inventory", list_player_inventory, command_dict=room_commands)

### status ###
# Display the player's status including hit points, nutrition, and stress level
def display_player_status(*args):
	the_player_marker = game_state.current_state.get_marker_for_identifier("the_player")
	po = the_player_marker.object
	message_center.add_message(channel="default",message="Current HP: %s" % po.generate_hp_string())

Command("status", display_player_status, command_dict=room_commands)

### area_description ###
# 
Command("area_description", describe_focus, command_dict=room_commands)

### get_item ###
# get_item command moves an item to the player inventory, skipping the focus
# step because getting items is really common and needs to not be tedious.
def get_that_item(*args):
	target_item_marker = args[0]
	hand = game_state.current_state.get_object("right_hand")
	success = hand.try_to_hold_item(target_item_marker.object)
	if not success:
		message_center.add_message(channel="default", message="You leave {0} where it is for now.".format(target_item_marker.object.name))

mobile_item_arg = command_line.GameObjectArgumentHandler(filter_functions=[class_type_filter(MobileItem)],search_dict=game_state.terminal_search_dict)
Command("get_item", get_that_item, (mobile_item_arg,), command_dict=room_commands)

### make_item ###
#
def make_item(*args):
	item_to_make = args[0]
	component_search_dict = game_state.terminal_search_dict
	recipes={
		"gun":(),
		"hat":("Cloth","Feather"),
		"pants":("Leather","Zipper"),
		"first_aid_kit":(),
	}
	results={
		"gun":("11mm_handgun",),
		"hat":("colorful_hat",),
		"pants":("cargo_pants",),
		"first_aid_kit":("first_aid_kit",)
	}
	if item_to_make in recipes:
		necessary_components = recipes[item_to_make]
		missing_components = list(necessary_components[:])
		consumed_components = []
		for component in component_search_dict.values():
			if isinstance(component.object, Item) and component.object.name in missing_components:
				missing_components.remove(component.object.name)
				consumed_components.append(component)
		if len(missing_components) > 0:
			message_center.add_message(channel="fail",message="Not enough components to make item {0}, missing: {1}".format(item_to_make, ", ".join(missing_components)))
		else:
			message_center.add_message(channel="default",message="Making item...".format(item_to_make))
			for component in consumed_components:
				game_state.current_state.destroy_marker(component.identifier)
			
			for product in results[item_to_make]:
				create_object("container", {"identifier":str(get_unique_id()), "template":product}, (), game_state.current_state.get_focus_identifier())

			
			
item_to_make_arg = command_line.MultipleChoiceArgumentHandler(choices=("gun","hat","pants","first_aid_kit"))
Command("make_item", make_item, (item_to_make_arg,), command_dict=room_commands)


debug_commands = True

### key_list ###
def current_keys(*args):
	for key in game_state.current_state.key_set.dict.keys():
		message_center.add_message(str(key))
if debug_commands: Command("key_list", current_keys, command_dict=room_commands)

### marker_list ###
def current_markers(*args):
	for key in game_state.terminal_search_dict.keys():
		message_center.add_message(str(key))
if debug_commands: Command("marker_list", current_markers, command_dict=room_commands)

### hurt_self ###
# Debug command for testing damage.
def damage_the_player(*args):
	the_player_object = game_state.current_state.get_object("the_player")
	damage_amount = int(args[0])
	the_player_object.take_damage(damage_amount)

damage_arg = command_line.IntegerArgumentHandler(help_message="How much damage?")
if debug_commands: Command("hurt_self", damage_the_player, (damage_arg,), command_dict=room_commands)

### heal_self ###
# Debug command for testing damage.
def heal_the_player(*args):
	the_player_object = game_state.current_state.get_object("the_player")
	damage_amount = int(args[0])
	the_player_object.be_healed(damage_amount)

if debug_commands: Command("heal_self", heal_the_player, (damage_arg,), command_dict=room_commands)

########################
### SCENERY COMMANDS ###
########################

### examine ###
Command("examine", describe_focus, command_dict = scenery_commands)

#####################
### ITEM COMMANDS ###
#####################

item_commands.update(scenery_commands)

############################
### MOBILE ITEM COMMANDS ###
############################

mobile_item_commands.update(item_commands)

### get_this_item ###
# Gets whatever item the player is focussed on. Basically just calls back
# to the 'get_item' command from the room commands.
def get_focus(*args):
	target_item = game_state.current_state.focus_stack[-1]
	get_that_item(target_item)

Command("get_this_item", get_focus, command_dict=mobile_item_commands)

#######################
### WEAPON COMMANDS ###
#######################

weapon_commands.update(mobile_item_commands)

#########################
### MAGAZINE COMMANDS ###
#########################

magazine_commands.update(mobile_item_commands)

###########################
### AMMUNITION COMMANDS ###
###########################

ammunition_commands.update(mobile_item_commands)


