import sys,re

#from types import ListType, TupleType

import message_center

for channel_name in ["heading","subheading","description","item","success","failure"]:
	message_center.add_channel(channel_name)

import game_state

id_number = 0
def get_unique_id():
	global id_number
	id_number += 1
	return str(id_number)

######################################
# ITEM MANAGEMENT & CLASSIFICATION
######################################
class MarkerBoundObject:
	def __init__(self, name, use_identifier=None, use_game_state=None, **kwargs):
		self.formatted_name = name.lower().replace(" ", "_")
		self.formatted_name = re.sub(r"\W","",self.formatted_name)
		self.unique_name = self.formatted_name + "_" + str(get_unique_id())
		
		if use_identifier == None: use_identifier = self.unique_name
		if use_game_state == None: use_game_state = game_state.current_state
		self.marker = use_game_state.new_marker_for_identifier(identifier=use_identifier, visible_name=self.formatted_name, object=self, **kwargs)

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
	def __init__(self, name, description=None, location=None):
		self.name = name

		if location != None and isinstance(location, MarkerBoundObject):
			marker_location = location.marker
		else:
			marker_location = None
		
		global item_commands
		MarkerBoundObject.__init__(self, self.name, focus_commands = item_commands, location = marker_location)
		VisibleObject.__init__(self, description)
		

class Area(MarkerBoundObject, VisibleObject):
	def __init__(self, name, area_identifier, description=None):
		self.name = name

		MarkerBoundObject.__init__(self, name, use_identifier=area_identifier)
		VisibleObject.__init__(self, description)
		
	def generate_description(self):
		lines = []
		message_center.add_message(channel="heading",message=self.name)
		if self.description != None:
			message_center.add_message(channel="default", message=" \n" + self.description + "\n")
		else:
			message_center.add_message(channel="default", message=" \n")
		message_center.add_message(channel="subheading",message="Things Here")
		message_center.add_message(channel="item", message="\n".join([m.object.name for m in self.marker.get_visible_markers() if hasattr(m.object, 'name')]))
		return lines

class ActionRecord:
	def __init__(self, duration=1, skills_trained=(), skills_studied=(),):
		pass
		

class PlayerCharacter:
	def __init__(self):
		pass

###############
### FILTERS ###
###############

def class_type_filter(type):
	return lambda x: isinstance(x.object, type)

from command_line import Command, GameObjectArgumentHandler

### COMMANDS ###
area_commands = {}
scenery_commands = {}
item_commands = {}

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
### AREA COMMANDS ###
#####################

### inventory ###
# Focus on the player's inventory marker.
def list_player_inventory(*args):
	the_player_marker = game_state.current_state.get_marker_for_identifier("the_player")

Command("inventory", list_player_inventory, command_dict=area_commands)

### area_description ###
# 
Command("area_description", describe_focus, command_dict=area_commands)

debug_commands = False

### key_list ###
def current_keys(*args):
	for key in game_state.current_state.key_set.dict.keys():
		message_center.add_message(str(key))
if debug_commands: Command("key_list", current_keys, command_dict=area_commands)

### marker_list ###
def current_markers(*args):
	for key in game_state.terminal_search_dict.keys():
		message_center.add_message(str(key))
if debug_commands: Command("marker_list", current_markers, command_dict=area_commands)

########################
### SCENERY COMMANDS ###
########################

### examine ###
Command("examine", describe_focus, command_dict = scenery_commands)

#####################
### ITEM COMMANDS ###
#####################

item_commands.update(scenery_commands)
