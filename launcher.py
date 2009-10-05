import re, sys

try:
	import pygame
except ImportError:
	sys.exit("Can't find pygame. You won't get far without that! http://www.pygame.org/")

import command_line, message_center, game_state, text_object, event

pygame.init()

screen = pygame.display.set_mode((1280, 720))

terminal_surface = screen.subsurface((10,10,800,540))
text_area = terminal_surface.subsurface((10,10,780,520))
terminal_surface.fill((0x0C,0x26,0x0C))

terminal_text_object = text_object.TextObject(font_size=20)
terminal_text_anchor = text_object.SurfaceAnchoredText(surface=text_area, text_object=terminal_text_object, fg_color=(0x66,0xDD,0x66), bg_color=(0x0C,0x26,0x0C))

line_size = terminal_text_object.font.get_linesize()
terminal_message_queue = []
terminal_max_history = 100 # Arbitrary default... 100 messages clearly won't fit on-screen, and even if they are very long won't take enough memory to matter.
terminal_visible_messages = int(float(screen.get_height())/float(line_size))

terminal_text_anchor.draw()

main_command_line = command_line.CommandLine((10,560,800,150))

@game_state.current_state.event
def on_new_command_dict(command_dict):
	main_command_line.set_command_dict(command_dict)

##################
# GAME SELECTION #
##################

import game_init as active_game

##################

pygame.time.set_timer(pygame.USEREVENT+1, 100)

def command_test(*args):
	message_center.add_message("Successful command execution!")
command_line.Command("test", command_test)

def get_message_for_terminal():
	global terminal_message_queue, terminal_text_anchor, terminal_max_lines, terminal_visible_messages
	message, channel = message_center.get_message_with_channel()
	if message != None:
		terminal_message_queue.append(message)
		while len(terminal_message_queue) > terminal_max_history: terminal_message_queue.pop(0)
		terminal_text_anchor.replace_text("\n".join(terminal_message_queue[-terminal_visible_messages:]))
		terminal_text_anchor.draw()
		
typing_buffer = []

done = False
while not done :
	for event in pygame.event.get():
		if event.type == pygame.USEREVENT+1:
			get_message_for_terminal()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
			else:
				main_command_line.keydown_event(event)
	
	main_command_line.draw_to_surface(screen)
	pygame.display.flip()
	pygame.time.wait(16)