import xml.parsers.expat
import re
import inspect

import pygame 

import interface_classes, interface_widgets, command_line, terminal_display

container_types = ["layout","row","column","border_box"]

element_mappings = {
	"layout":interface_classes.Root,
	"row":interface_classes.Row,
	"column":interface_classes.Column,
	"filler":interface_classes.Filler,
	"terminal_display":terminal_display.TerminalDisplay,
	"command_line":command_line.CommandLine,
	"border_box":interface_classes.BorderBox,
	"button":interface_widgets.Button,
	"meter":interface_widgets.Meter,
	"label":interface_widgets.Label,
	"image":interface_widgets.Image,
	}

nesting_stack = []
root_objects = []
root_rect = None

def start_element(element_type, element_attributes):
	global container_types, element_mappings, nesting_stack, root_objects, root_rect
	
	if element_type not in element_mappings:
		raise Exception("Unknown element type: %s" % element_type)
	
	args = {}
	for key, val in element_attributes.items():
		if key == "ratio": val = [int(x) for x in val.split(",")]
		elif key.endswith("_color"): val = [int(x,16) for x in val.split(",")]
		args[str(key)] = val
	
	if len(nesting_stack) > 0:
		rect = nesting_stack[-1].get_next_rect()
		element_object = element_mappings[element_type](rect=rect, **args)
		nesting_stack[-1].add(element_object)
	else:
		element_object = element_mappings[element_type](rect=root_rect, **args)
		root_objects.append(element_object)
	
	if element_type in container_types:
		nesting_stack.append(element_object)

def end_element(element_type):
	global container_types, nesting_stack
	
	if element_type in container_types:
		nesting_stack.pop()


def load_interface_from_file_with_initial_rect(filename, rect):
	parser = xml.parsers.expat.ParserCreate("ASCII")
	
	parser.StartElementHandler = start_element
	parser.EndElementHandler = end_element

	global nesting_stack, root_objects, root_rect
	nesting_stack = []
	root_objects = []
	root_rect = rect
	
	parser.StartElementHandler = start_element
	parser.EndElementHandler = end_element

	xml_file = open(filename)
	parser.ParseFile(xml_file)
	xml_file.close()
	
	return root_objects


