import xml.parsers.expat
import re
import inspect

import mechanics

template_type_elements = ("room_template","item_template","door_template")
instance_type_elements = ("room_instance","item_instance","door_instance")
text_type_elements = ("description",)

top_level_container_elements = ("zone",) + template_type_elements
recursive_container_elements = instance_type_elements

element_relationship_dict = {
	None:("deep_space_survival_data",),
	"deep_space_survival_data":text_type_elements + top_level_container_elements,
	"description":(),
	"zone":("room_instance","map_room"),
	"room_template":("item_instance","door_instance"),
	"room_instance":("item_instance","door_instance"),
	"map_room":(),
	"item_instance":("item_instance",),
	"item_template":("item_instance",),
	"door_template":(),
	"door_instance":(),
}

class RawElement:
	def __init__(self, element_type, attributes):
		self.element_type = element_type
		self.instantiation_class = element_to_class_mappings[element_type]
		self.element_atts = {}
		for arg in inspect.getargspec(self.instantiation_class.__init__).args:
			if arg in attributes:
				self.element_atts[arg] = str(attributes[arg])
		self.children = []
	
	def add_child_element(self, raw_element):
		self.children.append(raw_element)
	
	def instantiate(self):
		instance = self.instantiation_class(**self.element_atts)
		for raw_element in self.children:
			instance.add_child_element(raw_element)
		return instance

class Zone:
	def __init__(self, identifier, name):
		global filling_game_state
		self.identifier=identifier
		filling_game_state.zone_dict[self.identifier] = self
		self.name = name
		self.child_elements = []
		self.child_instances = []
		
	def add_child_element(self, raw_element):
		self.child_elements.append(raw_element)
	
	def instantiate(self):
		for c in self.child_elements:
			instance = c.instantiate()
			self.child_instances.append(instance)
	
	def to_str(self, n):
		s = self.name
		for child in self.child_instances:
			s += "\n" + ("--"*n) + child.to_str(n+1)
		return s

class Template:
	def __init__(self, identifier):
		global filling_game_state
		self.identifier = identifier
		filling_game_state.template_dict[self.identifier] = self
		self.children = []
	
	def add_child_element(self, raw_element):
		self.children.append(raw_element)

class Instance:
	def __init__(self, identifier, template):
		global filling_game_state
		self.identifier = identifier
		self.template = filling_game_state.template_dict[template]
		self.name = self.template.name
		filling_game_state.instance_dict[self.identifier] = self
		self.marker = filling_game_state.new_marker_for_identifier(self.identifier)
		self.children = []
		for raw_element in self.template.children:
			self.add_child_element(raw_element)
	
	def add_child_element(self, raw_element):
		instance = raw_element.instantiate()
		self.children.append(instance)
		instance.marker.move_to_marker(self.marker)
	
	def to_str(self, n):
		s = self.name
		for child in self.children:
			s += "\n"  + ("--"*n) + child.to_str(n+1)
		return s

class RoomTemplate(Template):
	def __init__(self, identifier, name, size='5x5x4', desc_id=None, floor_type=None, wall_type=None, ceiling_type=None, integral_instances=()):
		Template.__init__(self, identifier)
		self.name = name
		self.desc_id = desc_id

class RoomInstance(Instance):
	def __init__(self, identifier, template, name=None, desc_id=None, network_path=None, utility_section=None, life_support_section=None):
		global filling_game_state
		Instance.__init__(self, identifier, template)
		if name != None: self.name = name

		self.desc_id = desc_id or self.template.desc_id
		
		if self.desc_id != None and self.desc_id in filling_game_state.text_storage["description"]:
			self.description = filling_game_state.text_storage["description"][self.desc_id]
		else:
			self.description = "Could not find description for area id %s." % self.identifier
			if self.desc_id != None:
				self.description += "\nNo description matched desc_id %s." % self.desc_id
			else:
				self.description += "\nNo desc_id was found."
		
		self.room = mechanics.Room(name=self.name, description=self.description)
		self.room.marker = self.marker
		self.marker.object = self.room
		self.marker.visible_name = self.room.formatted_name
		self.marker.focus_commands = mechanics.room_commands


class ItemTemplate(Template):
	def __init__(self, identifier, name, desc_id=None):
		Template.__init__(self, identifier)
		self.name = name
		self.desc_id = desc_id

class ItemInstance(Instance):
	def __init__(self, identifier, template, name=None, desc_id=None, stack_size=None):
		Instance.__init__(self, identifier, template)
		if name != None: self.name = name

		self.desc_id = desc_id or self.template.desc_id
		
		if self.desc_id != None and self.desc_id in filling_game_state.text_storage["description"]:
			self.description = filling_game_state.text_storage["description"][self.desc_id]
		else:
			self.description = "Could not find description for item id %s." % self.identifier
			if self.desc_id != None:
				self.description += "\nNo description matched desc_id %s." % self.desc_id
			else:
				self.description += "\nNo desc_id was found."
		
		self.item = mechanics.Item(name=self.name, description=self.description)
		self.item.marker = self.marker
		self.marker.object = self.item
		self.marker.visible_name = self.item.formatted_name
		self.marker.focus_commands = mechanics.item_commands
	
class DoorTemplate(Template):
	def __init__(self, identifier, name):
		Template.__init__(self, identifier)
		self.name = name

class DoorInstance(Instance):
	def __init__(self, identifier, template, destination, name=None):
		global filling_game_state
		Instance.__init__(self, identifier, template)
		if name != None:
			self.name = name
		self.item = mechanics.Item(name=self.name)
		self.item.marker = self.marker
		self.marker.object = self.item
		self.marker.visible_name = self.item.formatted_name
		self.marker.focus_commands = mechanics.item_commands
		self.destination_id = destination
		
		filling_game_state.door_list.append(self)
	
	def connect(self):
		global filling_game_state
		destination_marker = filling_game_state.instance_dict[self.destination_id].marker
		move_target_marker = filling_game_state.new_marker_for_identifier(self.marker.identifier + "_move_target")
		move_target_marker.destination = destination_marker
		move_target_marker.visible_name = destination_marker.object.formatted_name
		move_target_marker.move_to_marker(self.marker.location)

element_to_class_mappings={
	"room_template":RoomTemplate,
	"item_template":ItemTemplate,
	"door_template":DoorTemplate,
	"zone":Zone,
	"room_instance":RoomInstance,
	"item_instance":ItemInstance,
	"door_instance":DoorInstance
}

element_path_stack = [None]

current_text_id = ""
current_text_buffer = ""

container_stack = []
top_level_container_list = []

unique_instance_id_number = 0
def get_unique_instance_id():
	global unique_instance_id_number
	unique_instance_id_number += 1
	return "instance_" + str(unique_instance_id_number)

def require_attribute(attr_name, attr_dict):
	global element_path_stack, parser
	if attr_name not in attr_dict:
		raise Exception("Malformed Element Error: '%s' element must have '%s' attribute. Error at line %i" % (element_path_stack[-1], attr_name, parser.CurrentLineNumber))
		
def start_element(element_type, attrs):
	global element_path_stack, parser, element_relationship_dict
	global text_type_elements, template_type_elements, instance_type_elements
	
	if element_type not in element_relationship_dict:
		raise Exception("Unknown element '" + element_type + "' at Line " + str(parser.CurrentLineNumber))
	
	parent = element_path_stack[-1]

	#print "|   "*(len(element_path_stack)-1) + "|> " + str(element_type) + " in " + str(parent)
	
	if parent in element_relationship_dict:
		allowable_children = element_relationship_dict[parent]
		if element_type not in allowable_children:
			raise Exception("Element '" + element_type + "' not allowed in '" + parent + "'. Error at line " + str(parser.CurrentLineNumber))

	element_path_stack.append(element_type)

	if "id" in attrs:
		attrs["identifier"] = attrs["id"]
	
	if element_type in text_type_elements:
		require_attribute("identifier", attrs)
		global current_text_id
		current_text_id = attrs["identifier"]
	
	if element_type in top_level_container_elements:
		require_attribute("identifier", attrs)
		tlc = RawElement(element_type, attrs)
		container_stack.append(tlc)
		top_level_container_list.append(tlc)
	elif element_type in recursive_container_elements:
		if "identifier" in attrs:
			if element_path_stack[2] in template_type_elements:
				raise Exception("Instances must not have explicit identifiers when placed inside a template. Error at line " + str(parser.CurrentLineNumber))
		else: attrs["identifier"] = get_unique_instance_id()
		rc = RawElement(element_type, attrs)
		container_stack[-1].add_child_element(rc)
		container_stack.append(rc)

def end_element(element_type):
	global filling_game_state, element_path_stack, text_type_elements, current_text_id, current_text_buffer, text_storage
	dying_element_type = element_path_stack.pop()
	if dying_element_type in text_type_elements and current_text_id != None:
		collapsed_whitespace = re.sub(r'\s+',' ',current_text_buffer).strip()
		manual_line_breaks = re.sub(r'\\n','\n',collapsed_whitespace)
		filling_game_state.text_storage[dying_element_type][current_text_id] = manual_line_breaks
		current_text_buffer = ""
		current_text_id = None
	elif dying_element_type in top_level_container_elements + recursive_container_elements:
		container_stack.pop()

def char_data(data):
	global element_path_stack, current_text_buffer, text_type_elements
	if element_path_stack[-1] in text_type_elements:
		current_text_buffer += data

def fill_target_state_from_file_list(target_state, file_list):
	global filling_game_state
	filling_game_state = target_state

	filling_game_state.text_storage = {}
	for	text_type in text_type_elements:
		filling_game_state.text_storage[text_type] = {}

	filling_game_state.zone_dict = {}
	filling_game_state.template_dict = {}
	filling_game_state.instance_dict = {}
	
	filling_game_state.door_list = []

	parser = xml.parsers.expat.ParserCreate("ASCII")
	
	parser.StartElementHandler = start_element
	parser.EndElementHandler = end_element
	parser.CharacterDataHandler = char_data

	for filename in file_list:
		xml_file = open(filename)
		parser.ParseFile(xml_file)
		xml_file.close()

	for tlc in top_level_container_list:
		tlc.instantiate()

	for zone_id, zone_object in filling_game_state.zone_dict.items():
		zone_object.instantiate()
		
	for zone in filling_game_state.zone_dict.values():
		print zone.to_str(1)
	
	for door in filling_game_state.door_list:
		door.connect()
	
