import xml.parsers.expat
import re
import inspect

import game_state, mechanics

item_type_elements = ("item","door","container","weapon","magazine","ammunition","food","player_character","hand")
instance_type_elements = ("room",) + item_type_elements

element_relationship_dict = {
	None:("deep_space_survival_data",),
	"deep_space_survival_data":("template","text") + instance_type_elements,
	"text":(),
	"template":item_type_elements,
	"room":item_type_elements,
	"item":(),
	"container":item_type_elements,
	"weapon":("magazine",),
	"magazine":("ammunition",),
	"door":(),
	"player_character":item_type_elements,
	"hand":(),
}

class RawElement:
	"""The RawElement class records information about an element read from an
	XML document. It performs minimal transformations on that information."""
	def __init__(self, element_type, attributes):
		self.element_type = element_type
		self.element_atts = {}
		self.children = []
	
	def add_child_element(self, raw_element):
		self.children.append(raw_element)
	
	def instantiate(self):
		instance = self.instantiation_class(**self.element_atts)
		for raw_element in self.children:
			instance.add_child_element(raw_element)
		return instance

class Instance:
	def __init__(self, instance_type, creation_args, children=()):
		self.type = instance_type
		self.args = creation_args
		self.children = list(children[:])
	
	def add_child(self, child):
		if isinstance(child, Instance):
			self.children.append(child)
		else:
			raise Exception("Adding non-Instance as child of Instance.")

class Template:
	def __init__(self, identifier, creation_args, children=()):
		self.identifier = identifier
		self.args = creation_args
		self.children = list(children[:])
	
	def add_child(self, child):
		if isinstance(child, Instance):
			self.children.append(child)
		else:
			raise Exception("Adding non-Instance as child of Template.")

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
	global instance_type_elements, container_stack, top_level_container_list
	
	if element_type not in element_relationship_dict:
		raise Exception("Unknown element '" + element_type + "' at Line " + str(parser.CurrentLineNumber))
	
	parent = element_path_stack[-1]

	if parent in element_relationship_dict:
		allowable_children = element_relationship_dict[parent]
		if element_type not in allowable_children:
			raise Exception("Element '" + element_type + "' not allowed in '" + parent + "'. Error at line " + str(parser.CurrentLineNumber))

	element_path_stack.append(element_type)

	if "id" in attrs:
		attrs["identifier"] = attrs["id"]
		del attrs["id"]

	if element_type == "text":
		require_attribute("identifier", attrs)
		global current_text_id
		current_text_id = attrs["identifier"]
	elif element_type == "template":
		require_attribute("identifier", attrs)
		identifier = attrs["identifier"]
		del attrs["identifier"]
		tlc = Template(identifier, attrs)
		container_stack.append(tlc)
		top_level_container_list.append(tlc)
	elif element_type in instance_type_elements:
		if len(container_stack) == 0:
			require_attribute("identifier", attrs)
			tlc = Instance(element_type, attrs)
			container_stack.append(tlc)
			top_level_container_list.append(tlc)
		else:			
			if "identifier" in attrs:
				if "template" in element_path_stack:
					raise Exception("Instances must not have explicit identifiers when placed inside a template. Error at line " + str(parser.CurrentLineNumber))
			else: attrs["identifier"] = get_unique_instance_id()
			rc = Instance(element_type, attrs)
			container_stack[-1].add_child(rc)
			container_stack.append(rc)

def end_element(element_type):
	global element_path_stack, current_text_id, current_text_buffer, instance_type_elements
	dying_element_type = element_path_stack.pop()
	if dying_element_type == "text" and current_text_id != None:
		collapsed_whitespace = re.sub(r'\s+',' ',current_text_buffer).strip()
		manual_line_breaks = re.sub(r'\\n','\n',collapsed_whitespace)
		game_state.current_state.text_storage[current_text_id] = manual_line_breaks
		current_text_buffer = ""
		current_text_id = None
	elif dying_element_type in ("template",)+instance_type_elements:
		container_stack.pop()

def char_data(data):
	global element_path_stack, current_text_buffer, text_type_elements
	if element_path_stack[-1] == "text":
		current_text_buffer += data

def fill_current_state_from_file_list(file_list):
	global parser

	game_state.current_state.text_storage = {}

	game_state.current_state.door_list = []


	for filename in file_list:
		parser = xml.parsers.expat.ParserCreate("ASCII")
	
		parser.StartElementHandler = start_element
		parser.EndElementHandler = end_element
		parser.CharacterDataHandler = char_data

		xml_file = open(filename)
		parser.ParseFile(xml_file)
		xml_file.close()

	template_index = game_state.current_state.template_index = {}
	waiting_instances = []
	global top_level_container_list
	for container in top_level_container_list:
		if isinstance(container, Template):
			template_index[container.identifier] = container
		else:
			waiting_instances.append(container)
	
	for instance in waiting_instances:
		mechanics.create_object(object_type=instance.type, object_args=instance.args, object_children=instance.children, object_location = None)
		
			
	
	
	
	
	
	
	
	
	
	
	
