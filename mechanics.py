import sys,re

#from types import ListType, TupleType

import message_center

import game_state

id_number = 0
def get_unique_id():
	global id_number
	id_number += 1
	return str(id_number)

######################################
# WEILDING EQUIPMENT
######################################

class WeildableObject:
	pass

######################################
# WEARING EQUIPMENT
######################################

humanoid_slot_locations = ("head","forehead","right_eye","left_eye","nose","left_cheek","right_cheek","mouth","chin","neck_front","neck_back","chest","stomach","upper_back","lower_back","ass","groin","right_shoulder","right_bicep","right_elbow","right_forearm","right_wrist","right_hand","right_thigh","right_knee","right_shin","right_ankle","right_foot","left_shoulder","left_bicep","left_elbow","left_forearm","left_wrist","left_hand","left_thigh","left_knee","left_shin","left_ankle","left_foot")

class SlotLocation:
	def __init__(self, layers = [],damage_reduction = 0.0):
		self.layers = layers
		self.damage_reduction = damage_reduction
		
class CannotWearItemException(Exception):
	pass

class EquipmentWearer:
	def __init__(self, slot_locations):
		self.worn_items = []
		self.slot_locations = {}
		for slot in slot_locations:
			self.slot_locations[slot] = SlotLocation()
	
	def is_wearing(self, item):
		if item in self.worn_items:
			return True
		else:
			return False

	def wear_item(self, item):
		if isinstance(item, WearableObject) == True:
			for slot in item.slot_coverage:
				if slot not in self.slot_locations :
					raise CannotWearItemException("Slot %s does not exist." % str(slot))
		
			if isinstance(item, Armor):
				for slot in item.slot_coverage:
					armor = 1
					hard_armor = 0
					if item.armor_type == "hard":
						hard_armor += 1
					
					for worn_item in self.slot_locations[slot].layers:
						if isinstance(worn_item, Armor):
							armor += 1
							if worn_item.armor_type == "hard":
								hard_armor += 1
							
					if armor > 2 or hard_armor > 1:
						raise CannotWearItemException("Too much armor on slot %s (and possibly others!)" % slot)
		
			self.worn_items.append(item)
			for slot in item.slot_coverage:
				self.slot_locations[slot].layers.append(item)
				if isinstance(item, Armor):
					self.slot_locations[slot].damage_reduction += item.damage_reduction

		else:
			raise CannotWearItemException("Unwearable item.")
	
	def unwear_item(self, item):
		if self.is_wearing(item):
			self.worn_items.remove(item)
			for slot in item.slot_coverage:
				self.slot_locations[slot].layers.remove(item)
				if isinstance(item, Armor):
					self.slot_locations[slot].damage_reduction -= item.damage_reduction

	def describe_worn_items(self):
		# "He/she is wearing... "
		if 0 < len(self.worn_items) < 2:
			return "only " + self.worn_items[0].name + "."
		elif len(self.worn_items) >= 2:
			return str(", ".join([item.name for item in self.worn_items[:-1]])) + " and " + self.worn_items[-1].name + "."
		else:
			return "nothing."

class WearableObject:
	def __init__(self, slot_coverage=(), concealment=1.0):
		self.concealment = concealment # 0-1 you can see through layers until full concealment is reached
		self.slot_coverage = slot_coverage

######################################
# ITEM MANAGEMENT & CLASSIFICATION
######################################

class TerminalTargetObject:
	def __init__(self, name):
		self.name = name
		self.formatted_name = name.lower().replace(" ", "_")
		self.formatted_name = re.sub(r"\W","",self.formatted_name)
		self.unique_name = self.formatted_name + "_" + str(get_unique_id())

class KeySpawnedObject:
	def __init__(self, keys_for_spawn = (), keys_for_despawn = ()):
		self.keys_for_spawn = keys_for_spawn
		self.keys_for_despawn = keys_for_despawn
	

class VisibleObject:
	def __init__(self, description = None):
		self.description = description
	
	def generate_description(self):
		if self.description == None:
			return (str(self.name).capitalize() + " is rather difficult to describe.",)
		else:
			return (self.name,self.description,)

class ConceptualObject:
	def __init__(self,explanation):
		self.explanation = explanation
	
######################################
# CONTAINERS & CONTAINMENT
######################################

class ContainableObject:
	def __init__(self, volume=0.1, container=None):
		self.volume = float(volume)
		self.container = None
		self.move_to_container(container)
		
	def move_to_container(self, container):
		if container != None:
			container.add_item(self)
	
		if self.container != None:
			self.container.remove_item(self)
			
		self.container = container

class CannotContainObjectException(Exception):
	pass

class ContainerObject:
	def __init__(self, max_capacity=sys.maxint, contained_objects = [], object_filters = (), open = False):
		self.max_capacity = float(max_capacity)
		self.current_capacity = self.max_capacity
		self.object_filters = object_filters
		self.open = open
		
		self.contained_objects = []
		
		for object in contained_objects:
			object.move_to_container(self)	
		
	def add_item(self, item):
		if item is self:
			raise CannotContainObjectException("Container cannot contain itself.")
		
		if isinstance(item, ContainableObject):
			for filter in self.object_filters:
				if not filter(item):
					raise CannotContainObjectException("Wrong object type for this container.") 

			if self.current_capacity - item.volume < 0:
				if item.volume > self.max_capacity :
					raise CannotContainObjectException("Object is larger than container.")
				else:
					raise CannotContainObjectException("Not enough space left in container.")

			self.contained_objects.append(item)
			self.current_capacity -= item.volume
		else:
			raise CannotContainObjectException("Can't put that in a container!")

	def remove_item(self, item):
		if item in self.contained_objects:
			self.contained_objects.remove(item)
			self.current_capacity += item.volume
	
	def recursive_content_list(self):
		content_list = []
		containers_to_check = [self]
		
		while len(containers_to_check) > 0 :
			now_searching = containers_to_check.pop(0)
			for object in now_searching.contained_objects :
				content_list.append(object)
				if isinstance(object, ContainerObject):
					containers_to_check.append(object)
		
		return content_list
	
	def contains_object(self, object):
		recursive_content = self.recursive_content_list()
		if object in recursive_content:
			return True
		else:
			return False
	
	def describe_contained_objects(self):
		objects = self.recursive_content_list()
		
		if len(objects) == 0: return "nothing"
		if len(objects) == 1: return objects[0].name
		
		string = ", ".join([object.name for object in objects[:-1]])
		string += " and %s." % objects[-1].name
		return string

######################################
# GAME-LEVEL OBJECT TYPES
######################################

item_focus_dict = {}
class Item (VisibleObject, ContainableObject, TerminalTargetObject):
	def __init__(self, location=None, name=None, mass=1.0, volume=0.1, description=None):
		TerminalTargetObject.__init__(self, name)
		
		VisibleObject.__init__(self, description)
		ContainableObject.__init__(self, volume=volume, container=location)

		self.mass=float(mass)
		self.description=description
		
class Recipe (TerminalTargetObject, ContainableObject, ConceptualObject):
	def __init__(self, name=None, location=None, explanation=None, product=None, required_materials=None, required_tools=None, difficulty_rating=0):
		ContainableObject.__init__(self, volume=0, container=location)
		ConceptualObject.__init__(self, explanation=explanation)
		TerminalTargetObject.__init__(self, name=name)
		self.product = product
		self.required_materials = required_materials
		self.required_tools = required_tools
		self.difficulty_rating = difficulty_rating
		
class Book (Item, ContainerObject): #READ A BOOK, READ A BOOK, READ A MOTHER Approved BOOK!!!
	def __init__(self, location=None, name=None, mass=1.0, volume=0.02, description=None,contained_concepts=(),open = True):
		Item.__init__(self, location=location, name=name, mass=mass, volume=volume, description=description)
		ContainerObject.__init__(self, contained_objects = contained_concepts, object_filters = (conceptual_filter,), open = open) 
	
class Clothing (Item, WearableObject):
	def __init__(self, location=None, name=None, mass=1.0, volume=0.1, description=None, slot_coverage=(), concealment=1.0):
		Item.__init__(self, location=location, name=name, mass=mass, volume=volume, description=description)
		WearableObject.__init__(self, slot_coverage=slot_coverage, concealment=concealment)

class Armor (Item, WearableObject):
	def __init__(self, location=None, name=None, mass=1.0, volume=0.1, description=None, slot_coverage=(), concealment=1.0, armor_type="soft", mobility_penalty = 0, damage_reduction=0):
		Item.__init__(self, location=location, name=name, mass=mass, volume=volume, description=description)
		WearableObject.__init__(self, slot_coverage=slot_coverage, concealment=concealment)

		self.armor_type = str(armor_type).lower() # soft or hard
		self.mobility_penalty = float(mobility_penalty)
		self.damage_reduction = float(damage_reduction)

class Tool(Item, WeildableObject):
	pass

class Weapon(Item, WeildableObject):
	pass
	
class MobileContainer(Item, ContainerObject):
	pass

class WearableContainer(Clothing, ContainerObject):
	def __init__(self, location=None, name=None, mass=1.0, volume=0.1, description=None, slot_coverage=(), concealment=1.0, max_capacity=sys.maxint, contained_objects = [], object_filters = (), open = False):
		Clothing.__init__(self, location=location, name=name, mass=mass, volume=volume, description=description, slot_coverage=slot_coverage, concealment=concealment)
		ContainerObject.__init__(self, max_capacity=max_capacity, contained_objects = contained_objects, object_filters = object_filters, open = open)

class Scenery(ContainableObject, VisibleObject, TerminalTargetObject):
	def __init__(self, location=None, name=None, mass=100.0, volume=100.0, description=None):
		TerminalTargetObject.__init__(self, name)
		
		ContainableObject.__init__(self, container=location, volume=volume)
		VisibleObject.__init__(self, description)
		
		self.mass = mass

class FixedContainer(Scenery, ContainerObject):
	pass

class Area(VisibleObject, TerminalTargetObject, ContainerObject):
	def __init__(self, name=None, lighting=None, temperature=None, description=None):
		TerminalTargetObject.__init__(self, name)
		
		VisibleObject.__init__(self, description)
		
		self.lighting=lighting
		self.temperature=temperature
	
		ContainerObject.__init__(self)
		
	def generate_description(self):
		lines = []
		lines.append("{[ " + self.name + " ]}")
		lines.append("")
		if self.description != None: lines.append(self.description)
		lines.append("")
		if len(self.contained_objects) > 0 : lines.append("*> Exits: " + ", ".join([link.name for link in self.contained_objects if isinstance(link, Portal)]))
		if len(self.contained_objects) > 0 : lines.append("*> Items: " + ", ".join([str(item.name) for item in self.contained_objects if hasattr(item, 'name') and item is not the_player and not isinstance(item, Portal)]))
		lines.append("")
		return lines

class Portal(TerminalTargetObject, ContainableObject):
	def __init__(self, name=None, open=False, lock_object=None, location=None, destination=None):
		TerminalTargetObject.__init__(self, name)
		
		ContainableObject.__init__(self, volume=0, container=location)
		
		self.destination = destination

######################################
# CREATURE TYPES
######################################

class Humanoid(ContainableObject, VisibleObject, EquipmentWearer, TerminalTargetObject):
	def __init__(self, location=None, hand=None, name=None, skills={}, mass=65.0, description=None, pronoun="it"):
		TerminalTargetObject.__init__(self, name)

		ContainableObject.__init__(self, volume = mass, container = location) # volume = mass because mass is kg, volume is dm^2, and humans are density 1.
		
		global humanoid_slot_locations
		EquipmentWearer.__init__(self, humanoid_slot_locations)
		
		VisibleObject.__init__(self, description)
		
		self.container_list = []
		self.default_container = None
		
		self.hand = hand
		self.skills=skills
		self.mass = mass
		self.description=description
		self.pronoun = pronoun
		
		self.perception_dict = {}
		self.refresh_perception()

	def wear_item(self, item):
		EquipmentWearer.wear_item(self, item)

		if isinstance(item, ContainerObject) and item not in self.container_list:
			self.container_list.append(item)
			if len(self.container_list) == 1:
				self.default_container = item
				#message_center.add_message("%s is now your default container." % self.default_container.name)
	
	def unwear_item(self, item):
		EquipmentWearer.unwear_item(self, item)
		
		if item in self.container_list:
			self.container_list.remove(item)
			
			if self.default_container is item:
				if len(self.container_list) > 0:
					self.default_container = self.container_list[0]
					message_center.add_message("%s is now your default container." % self.default_container.name)
				else:
					self.default_container = None
					message_center.add_message("You no longer have a default container.")
	
	def refresh_perception(self):
		self.perception_dict.clear()

		if self.container == None:
			return
		
		#self.perception_dict[self.formatted_name] = self
		#self.perception_dict[self.container.formatted_name] = self.container
		
		the_list = []
		the_list += self.container.contained_objects
		the_list += self.worn_items
		for container in self.container_list :
			the_list += container.recursive_content_list()
		
		the_list = filter(lambda x: isinstance(x, TerminalTargetObject), the_list)
		
		for target in the_list :
			if target.formatted_name not in self.perception_dict:
				self.perception_dict[target.formatted_name] = target
			else:
				if self.perception_dict[target.formatted_name] is not target:
					self.perception_dict[target.unique_name] = target

	def generate_description(self):
		d = []
		d += [self.description]
		d += [self.pronoun.capitalize() + " is wearing " + self.describe_worn_items()]
		return d

the_player = Humanoid(name="self")

######################################
# SIGNAL OBJECTS
######################################

def default_event_function(args):
	message_center.add_message("Event triggered.")
	return True

class Event(ContainableObject):
	def __init__(self, location=None, function=default_event_function, args=None):
		ContainableObject.__init__(self, container=location)
		
		self.function = function
		self.args = args
	
	def trigger(self):
		self.should_be_destroyed = self.function(self.args)
	
	def should_be_destroyed(self):
		return self.should_be_destroyed
	
	def destroy(self):
		self.move_to_container(None)

### FILTERS ###

def class_type_filter(type):
	return lambda x: isinstance(x.object, type)
	
visible_filter = class_type_filter(VisibleObject)
weildable_filter = class_type_filter(WeildableObject)
wearable_filter = class_type_filter(WearableObject)
containable_filter = class_type_filter(ContainableObject)
container_filter = class_type_filter(ContainerObject)
portal_filter = class_type_filter(Portal)
container_filter = class_type_filter(ContainerObject)
item_filter = class_type_filter(Item)
conceptual_filter = class_type_filter(ConceptualObject)

def in_hand_filter(item):
	if the_player.hand == item:
		return True
	else:
		return False

def worn_item_filter(item):
	return the_player.is_wearing(item)

def unworn_item_filter(item):
	return not worn_item_filter(item)

def in_inventory_filter(item):
	for container in the_player.container_list:
		if container.contains_object(item) : return True
	
	if in_hand_filter(item) or worn_item_filter(item):
		return True
	else:
		return False

def in_area_filter(item):
	if the_player.container != None:
		if item in the_player.container.contained_objects or item is the_player.container:
			return True
	
	return False

def nearby_item_filter(item):
	if in_inventory_filter(item) or in_area_filter(item):
		return True
	else:
		return False

def adjacent_area_filter(area):
	if area in the_player.container.links:
		return True
	else:
		return False

def not_the_player_filter(item):
	if item is not the_player:
		return True
	else:
		return False

########### COMMANDS AND STUFF

from command_line import Command, ArgumentHandler, GameObjectArgumentHandler

### COMMANDS ###
area_commands = {}
scenery_commands = {}

### move ###
def move_through_portal(params):
	portal = params[0]
	
	message_center.add_message("Leaving %s" % str(game_state.current_state.focus_stack[-1].object.name))
	game_state.current_state.refocus_on_marker((portal.object.destination.marker,))
	message_center.add_message("Entering %s" %  str(game_state.current_state.focus_stack[-1].object.name))
	message_center.add_message(" ")
	area_description(None)

portal_arg = GameObjectArgumentHandler(search_dict=game_state.terminal_search_dict)# , filter_functions=(portal_filter,))

#Command("move", move_through_portal, (portal_arg,), command_dict=area_command_dict)

### inventory ###
def list_player_inventory(params):
	message_center.add_message("You are wearing: " + the_player.describe_worn_items())
	if len(the_player.container_list) == 0:
		message_center.add_message("You are carrying: nothing.")
	for container in the_player.container_list:
		message_center.add_message("In your %s you have: %s" % (container.name, container.describe_contained_objects()))

Command("inventory", list_player_inventory, command_dict=area_commands)

### area_description ###
def area_description(params):
	area = game_state.current_state.focus_stack[-1].object
	for line in area.generate_description():
		message_center.add_message(line)
Command("area_description", area_description, command_dict=area_commands)

### key_list ###
def current_keys(params):
	for key in game_state.current_state.key_set.dict.keys():
		message_center.add_message(str(key))
Command("key_list", current_keys, command_dict=area_commands)

### marker_list ###
def current_markers(params):
	for key in game_state.terminal_search_dict.keys():
		message_center.add_message(str(key))
Command("marker_list", current_markers, command_dict=area_commands)

### use ###
#def use_item(params):
#	item = params[0]
#	targets = params[1:]
#	
#	item.use_on_targets(targets)
#
#Command("use", use_item, ((usable_filter),(conceptual_filter),(container_filter)), command_dict=command_dict)


##############################################################
# Item focus commands
##############################################################

### done ###
def done_with_focus_object(params):
	global focus_stack
	focus_stack.pop()
	if len(focus_stack) > 0:
		game_state.current_state.new_command_dict(focus_stack[-1].focus_commands)
	else:
		game_state.current_state.new_command_dict(base_command_dict)

#Command("done", done_with_focus_object, command_dict=item_focus_dict)

### examine ###
def examine_focus(params):
	target = game_state.current_state.focus_stack[-1].object
	
	if hasattr(target,'generate_description'):
		for line in target.generate_description():
			message_center.add_message(line)
	else:
		message_center.add_message("You can't actually see %s." % target.name)

Command("examine", examine_focus, command_dict = scenery_commands)

### wear ###
def wear_focus(params):
	global focus_stack
	target = focus_stack[-1]

	if the_player.is_wearing(target):
		message_center.add_message("You are already wearing %s." % target.name)
	else:
		try:
			the_player.wear_item(target)
			target.move_to_container(None)
			message_center.add_message("You put on %s." % target.name)
		except CannotWearItemException, e:
			message_center.add_message("Cannot wear %s; %s" % (target.name, str(e)))

#Command("wear", wear_focus, command_dict=item_focus_dict)

### unwear ###
def unwear_focus(params):
	global focus_stack
	target = focus_stack[-1]

	if wearable_filter(target):
		if the_player.is_wearing(target):
			the_player.unwear_item(target)
			message_center.add_message("You take off %s." % target.name)
			put_item_in_container((target, the_player.default_container or the_player.container))
		else:
			message_center.add_message("You're not wearing %s in the first place." % target.name)
	else:
		message_center.add_message("Wearing %s would probably be uncomfortable..." % target.name)

#Command("unwear", unwear_focus, command_dict=item_focus_dict)

### get ###
def get_focus(params):
	global focus_stack
	target = focus_stack[-1]

	if the_player.default_container == None :
		message_center.add_message("You don't seem to have any container to put that in.")
	elif isinstance(target, ContainableObject):
		put_item_in_container((target, the_player.default_container))
	else:
		message_center.add_message("Cannot get %s; that won't fit in a container." % (str(target.name)))

#Command("get", get_focus, command_dict=item_focus_dict)

### drop ###
def drop_focus(params):
	global focus_stack
	target = focus_stack[-1]

	if target.container != the_player.container:
		if the_player.is_wearing(target):
			unwear_focus(params)
			
		if target.container != the_player.container:
			put_item_in_container((target, the_player.container))
	else:
		message_center.add_message("%s is already on the floor." % target.name)

#Command("drop", drop_focus, command_dict=item_focus_dict)

### put ###
def put_item_in_container(params):
	item, container = params[:2]

	if the_player.is_wearing(item):
		unwear_item((item,))

	try:
		item.move_to_container(container)
		if container is the_player.container:
			message_center.add_message("You have placed %s on the floor." % (str(item.name)))
		else:
			message_center.add_message("You have placed %s in %s." % (str(item.name), str(container.name)))
	except CannotContainObjectException, e:
		message_center.add_message("Could not move %s to %s; %s" % (str(item.name), str(container.name), e.message))
		if item.container == None:
			try:
				item.move_to_container(the_player.container)
				message_center.add_message("You have placed %s on the floor." % (str(item.name)))
			except CannotContainObjectException, ex:
				message_center.add_message("Cannot put %s in %s and cannot put %s on floor. %s is lost to the void." % (item.name, container.name, item.name, item.name))

#puttable_arg = GameObjectArgumentHandler(search_dict=the_player.perception_dict, filter_functions=(item_filter, unworn_item_filter))
#container_arg = GameObjectArgumentHandler(search_dict=the_player.perception_dict, filter_functions=(container_filter,))

#Command("put", put_item_in_container, (puttable_arg, container_arg), command_dict=base_command_dict)

