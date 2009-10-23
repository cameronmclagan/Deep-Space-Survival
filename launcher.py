import re, sys, math

if sys.version_info[0] > 2:
	print "This program was written for python 2.6 and has not been tested with 3.0 or greater."
elif sys.version_info[0] < 2 or sys.version_info[1] < 6:
	sys.exit("This program was written for python 2.6 and will fail on any older version.")

try:
	import pygame
except ImportError:
	sys.exit("Can't find pygame. You won't get far without that! http://www.pygame.org/")

import terminal_display, command_line, message_center, game_state, event

pygame.init()

screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1440, 900))

import xml_interface_loader
root_interface_objects = xml_interface_loader.load_interface_from_file_with_initial_rect("interface_layout.xml", screen.get_rect())
root = root_interface_objects[0]
root.draw_to_surface(screen)
#main_terminal = terminal_display.TerminalDisplay((10,10,(screen.get_width()-30)/2,screen.get_height()-(150+30)), fg_color=(0xba,0xbd,0xb6), bg_color=(0x1E,0x24,0x26), font_size=20)
main_terminal = root.search_for_identifier("main_terminal")

channel_styles =	{
	"default":{"font_color":(0xBA,0xBD,0xB6),"font_name":"Droid Sans"},	
	"heading":{"font_color":(0xED,0xD4,0x00),"font_size":36,"font_name":"Alpha Echo","font_bold":False},
	"subheading":{"font_color":(0xED,0xD4,0x00),"font_size":28,"font_name":"Umbrage", "font_bold":False},
	"item":{"font_color":(0x62,0x8F,0xCF),"font_name":"Droid Sans"},
	"fail":{"font_color":(0xf5,0x79,0x00)},
	}

main_command_line = root["main_command"]

def exit_func():
	global done
	done=True
exit_button = root["exit_button"]
exit_button.function = exit_func

#rightbar_logo = pygame.image.load("DSS_Stolen_Logo_Big.png")
#screen.blit(rightbar_logo, (main_terminal.rect.width+20,10))

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
			main_terminal.add_message(message, **channel_style)
		else:
			break
		
fps_functions[FPS05].append(get_message_for_terminal)
fps_functions[FPS60].append(lambda ms: main_terminal.scroll_by_milliseconds(ms) and main_terminal.draw_to_surface(screen))

focus_list = []
def find_mouse_focus(*args):
	global focus_list, root
	old_list = focus_list
	pos = pygame.mouse.get_pos()
	focus_list = root.search_for_collision(pos)
	for x in old_list:
		if x not in focus_list: x.on_mouse_unhover(pos)
	for x in focus_list:
		if x not in old_list: x.on_mouse_hover(pos)
	

fps_functions[FPS15].append(find_mouse_focus)

fps_functions[FPS15].append(lambda ms: root.draw_to_surface(screen))


typing_buffer = []

done = False
while not done :
	for event in pygame.event.get():
		if event.type in fps_event_set:
			new_time = pygame.time.get_ticks()
			for function in fps_functions[event.type]:
				function(new_time - fps_last_calls[event.type])
			fps_last_calls[event.type] = new_time
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
			else:
				main_command_line.keydown_event(event)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				pos = pygame.mouse.get_pos()
				global focus_list
				for x in focus_list: x.on_mouse_leftclick(pos)
			elif event.button == 3:
				pos = pygame.mouse.get_pos()
				global focus_list
				for x in focus_list: x.on_mouse_rightclick(pos)
	
	main_command_line.draw_to_surface(screen)
	pygame.display.flip()
	pygame.time.wait(16)
	
	
