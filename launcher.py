import re, sys, math

if sys.version_info[0] > 2:
	print "This program was written for python 2.6 and has not been tested with 3.0 or greater."
elif sys.version_info[0] < 2 or sys.version_info[1] < 6:
	sys.exit("This program was written for python 2.6 and will fail on any older version.")

try:
	import pygame
except ImportError:
	sys.exit("Can't find pygame. You won't get far without that! http://www.pygame.org/")

import terminal_display, command_line, message_center, game_state, event, resource_loader

pygame.init()

preferred_resolution_list = [
	(7680,4800),
	(5120,3200),
	(3840,2400),
	(2560,1600),
	(1920,1200),
	(1680,1050),
	(1440,900),
	(1280,800),
	(1152,720),
	(1024,640),
	(768,480),
	(640,400),]

def resize_screen(size):
	global raw_screen_surface, screen, scaled_resolution_rect, development_resolution_rect, root, fullscreen, native_display_resolution
	
	if fullscreen:
		raw_screen_surface = pygame.display.set_mode(size, pygame.FULLSCREEN)
	else:
		raw_screen_surface = pygame.display.set_mode(size, pygame.RESIZABLE)

	provided_resolution_rect = raw_screen_surface.get_rect()
	print provided_resolution_rect.size

	scaled_resolution_rect = development_resolution_rect.fit(provided_resolution_rect)
	scaled_resolution_rect.center = provided_resolution_rect.center

	screen = raw_screen_surface.subsurface(scaled_resolution_rect)

	resource_loader.font_scale = float(scaled_resolution_rect.height) / float(development_resolution_rect.height)
	resource_loader.previously_loaded_fonts = {}
	
	if root != None:
		root.set_rect(screen.get_rect())
	
def toggle_fullscreen():
	global fullscreen, windowed_resolution, root, raw_screen_surface, native_display_resolution
	button_label = root["fullscreen_button"]
	if fullscreen == True:
		fullscreen = False
		resize_screen(windowed_resolution)
		button_label.set_text("CLICK FOR FULLSCREEN")
	else:
		fullscreen = True
		windowed_resolution = raw_screen_surface.get_size()
		resize_screen(native_display_resolution)
		button_label.set_text("CLICK FOR WINDOWED")

screen = None
root = None
scaled_resolution_rect = None
fullscreen = False
windowed_resolution = None
development_resolution_rect = pygame.Rect((0,0,1680,1050))

display_info = pygame.display.Info()

native_display_resolution = (display_info.current_w, display_info.current_h)

raw_screen_surface = None
for resolution in preferred_resolution_list:
	this_width, this_height = resolution
	that_width, that_height = display_info.current_w, display_info.current_h
	if this_width < (that_width-100) and this_height < (that_height-100):
		raw_screen_surface = pygame.display.set_mode(resolution, pygame.RESIZABLE)
		break
if raw_screen_surface == None: pygame.display.set_mode((0,0), pygame.RESIZABLE)

resize_screen(raw_screen_surface.get_size())

import xml_interface_loader
root_interface_objects = xml_interface_loader.load_interface_from_file_with_initial_rect("interface_layout.xml", screen.get_rect())
root = root_interface_objects[0]
root.draw_to_surface(screen)

root["fullscreen_button"].function = toggle_fullscreen

main_terminal = root.search_for_identifier("main_terminal")

color_subs = {
	"green":"#55DD55#",
	"blue":"#729FFF#",
	"yellow":"#EDD400#",
	"orange":"#F57900#",
	"red":"#EF2929#",
	"white":"#FFFFFF#",
	"reset":"#XXXXXX#",
}

channel_styles =	{
	"default":{"font_color":(0xBA,0xBD,0xB6),"font_size":20,"font_name":"Droid Sans",},	
	"heading":{"font_color":(0xED,0xD4,0x00),"font_size":38,"font_name":"Alpha Echo","font_bold":False},
	"subheading":{"font_color":(0xED,0xD4,0x00),"font_size":30,"font_name":"Umbrage", "font_bold":False},
	"item":{"font_color":(0x62,0x8F,0xCF),"font_size":20,"font_name":"Droid Sans"},
	"fail":{"font_color":(0xf5,0x79,0x00),"font_size":20,"font_name":"Droid Sans"},
	}

for channel_name in channel_styles.keys():
	message_center.add_channel(channel_name)

main_command_line = root["main_command"]

def exit_func():
	global done
	done=True
exit_button = root["exit_button"]
exit_button.function = exit_func

def save_func():
	game_state.save_game_state_to_file("the_save_game")
save_button = root["save_button"]
save_button.function = save_func

def load_func():
	game_state.load_game_state_from_file("the_save_game")
load_button = root["load_button"]
load_button.function = load_func

@game_state.current_state.event
def on_new_command_dict(command_dict):
	main_command_line.set_command_dict(command_dict)

##################
# GAME SELECTION #
##################

import game_init as active_game

##################

FPS60 = pygame.USEREVENT+1
FPS30 = pygame.USEREVENT+2
FPS15 = pygame.USEREVENT+3
FPS10 = pygame.USEREVENT+4
FPS05 = pygame.USEREVENT+5
FPS01 = pygame.USEREVENT+6

pygame.time.set_timer(FPS60, 16)	# 60 fps
pygame.time.set_timer(FPS30, 32)	# 30 fps
pygame.time.set_timer(FPS15, 64)	# 15 fps
pygame.time.set_timer(FPS10, 100)	# 10 fps
pygame.time.set_timer(FPS05, 200)	# 05 fps
pygame.time.set_timer(FPS01, 1000)	# 01 fps

fps_event_set = (FPS60, FPS30, FPS15, FPS10, FPS05, FPS01)

fps_functions = {}
fps_last_calls = {}
for event in fps_event_set:
	fps_functions[event] = []
	fps_last_calls[event] = pygame.time.get_ticks()

def get_message_for_terminal(ms):
	while True:
		message, channel = message_center.get_message_with_channel()
		if message != None:
			channel_style = channel_styles.get(channel)
			if channel_style == None: channel_style = channel_styles.get('default')
			main_terminal.add_message(message, sub_dict=color_subs, **channel_style)
		else:
			break
		
fps_functions[FPS05].append(get_message_for_terminal)
fps_functions[FPS60].append(lambda ms: main_terminal.scroll_by_milliseconds(ms) and main_terminal.draw_to_surface(screen))

focus_list = []
def find_mouse_focus(*args):
	global focus_list, root, scaled_resolution_rect
	old_list = focus_list
	pos_x, pos_y = pygame.mouse.get_pos()
	pos_x -= scaled_resolution_rect.left
	pos_y -= scaled_resolution_rect.top
	pos = (pos_x, pos_y)
	focus_list = root.search_for_collision(pos)
	for x in old_list:
		if x not in focus_list: x.on_mouse_unhover(pos)
	for x in focus_list:
		if x not in old_list: x.on_mouse_hover(pos)
	

fps_functions[FPS15].append(find_mouse_focus)

health_bar = root.search_for_identifier("health_bar")
fps_functions[FPS60].append(health_bar.update_by_milliseconds)
fps_functions[FPS60].append(lambda ms: health_bar.draw_to_surface(screen))

import random
health_bar.max_value = 50
health_bar.current_value = 50
def meter_tester(ms):
	player_object = game_state.current_state.get_object("the_player")
	health_bar.max_value = player_object.max_hp
	health_bar.current_value = player_object.cur_hp
fps_functions[FPS05].append(meter_tester)


fps_functions[FPS15].append(lambda ms: root.draw_to_surface(screen))

left_hand_holding_label = root.search_for_identifier("left_hand_holding_label")
right_hand_holding_label = root.search_for_identifier("right_hand_holding_label")
def hand_status_updater(ms):
	global left_hand_holding_label, right_hand_holding_label
	
	left_hand = game_state.current_state.get_object("left_hand")
	right_hand = game_state.current_state.get_object("right_hand")
	
	if left_hand.held_item == None:
		left_hand_holding_label.set_text("Nothing")
	else:
		left_hand_holding_label.set_text(left_hand.held_item.name)
	
	if right_hand.held_item == None:
		right_hand_holding_label.set_text("Nothing")
	else:
		right_hand_holding_label.set_text(right_hand.held_item.name)

fps_functions[FPS01].append(hand_status_updater)	
	

typing_buffer = []

done = False
while not done :
	for event in pygame.event.get():
		if event.type in fps_event_set:
			new_time = pygame.time.get_ticks()
			for function in fps_functions[event.type]:
				function(new_time - fps_last_calls[event.type])
			fps_last_calls[event.type] = new_time
		elif event.type == pygame.VIDEORESIZE:
			resize_screen(event.size)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
			else:
				main_command_line.keydown_event(event)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				pos = pygame.mouse.get_pos()
				for x in focus_list: x.on_mouse_leftclick(pos)
			elif event.button == 3:
				pos = pygame.mouse.get_pos()
				for x in focus_list: x.on_mouse_rightclick(pos)
	
	main_command_line.draw_to_surface(screen)
	pygame.display.flip()
	pygame.time.wait(16)
	
