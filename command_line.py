import re

import pygame

import message_center

import text_object

message_center.add_channel("terminal_error")
message_center.add_channel("terminal_info")
## Arg type constants

ARG_OBJECT = 1
ARG_STRING = 2
ARG_NUMBER = 3
ARG_COMMAND = 4
ARG_LIST = 5

default_command_dict = {}

class ArgumentError(Exception):
	pass

class StandardCommandError(Exception):
	pass

class CommandLine():
	def __init__(self, rect, command_dict=default_command_dict, fg_color=(0x66,0xDD,0x66), bg_color=(0x0C,0x26,0x0C), font_name="Droid Sans Mono,Bitstream Vera Sans Mono,Courier", font_size=16):
		self.rect = pygame.Rect(rect)
		
		self.fg_color = fg_color
		self.bg_color = bg_color
		
		self.surface = pygame.Surface(self.rect.size)
		self.surface.fill(self.fg_color)
		self.surface.fill(self.bg_color, (2,2,self.surface.get_width()-4,self.surface.get_height()-4))
		
		self.inner_rect = pygame.Rect((7,7,self.surface.get_width()-14,self.surface.get_height()-14))
		self.text_subsurface = self.surface.subsurface(self.inner_rect)
		
		self.text_anchor = text_object.SurfaceAnchoredText(self.text_subsurface, fg_color=self.fg_color, bg_color=self.bg_color)
		
		self.command_dict=command_dict
		
		self.typing_buffer = []
		self.helper_text = ""
		self.output_buffer = []
		
		self.on_text_update()
		self.internal_redraw()

	def set_command_dict(self, command_dict):
		self.clear()
		self.command_dict=command_dict
		self.on_text_update()

	def get_line_end(self):
		try:
			return self.typing_buffer.index("\n")
		except ValueError:
			return -1

	def get_current_line(self):
		line_end = self.get_line_end()
		if line_end == -1:
			return self.filter_line(''.join(self.typing_buffer))
		else:
			return self.filter_line(''.join(self.typing_buffer[0:line_end]))
			
	def current_line_is_complete(self):
		line_end = self.get_line_end()
		if line_end == -1:
			return False
		else:
			return True

	def clear_current_line(self):
		line_end = self.get_line_end()
		if line_end == -1:
			self.typing_buffer = []
		else:
			self.typing_buffer = self.typing_buffer[line_end+1:]

	def replace_current_line(self, line):
		line_end = self.get_line_end()
		if line_end == -1:
			self.typing_buffer = list(line)
		else:
			self.typing_buffer = list(line) + self.typing_buffer[line_end+1:]

	def filter_line(self, line):
		space_collapsed_line = re.sub(r"\s+"," ", line)
		lower_case_line = space_collapsed_line.lower()
		acceptable_characters_line = re.sub(r"[^a-z0-9_. ()\"]","",lower_case_line)
		return acceptable_characters_line

	def parse_command_strings_from_line(self, line):
		# "(?:^|\b)([a-z0-9_.]+)(?:$|\b)"
		search_results = re.findall(r'\s*(\w+)(?:\s|$)', line)
		if line[-1:] == ' ': search_results.append("")
		return search_results
	
	def clear(self):
		self.typing_buffer = []
	
	def internal_redraw(self):
		self.text_anchor.replace_text((''.join(self.typing_buffer) or "\n") + "\n~~~\n" + self.helper_text)
		self.text_anchor.draw()

	def draw_to_surface(self, surface):
		surface.blit(self.surface, self.rect)

	def tab_complete_current_line(self):
		current_line = self.get_current_line()
		completed_line = self.tab_complete_and_return_line(current_line)
		self.replace_current_line(completed_line)
	
	def keydown_event(self, event):
		if event.key == pygame.K_BACKSPACE:
			if len(self.typing_buffer) > 0: self.typing_buffer.pop()
		elif event.key == pygame.K_RETURN:
			self.typing_buffer.append("\n")
		elif event.key == pygame.K_TAB:
			self.tab_complete_current_line()
		else:
			self.typing_buffer.append(event.unicode)
		self.on_text_update()
		self.internal_redraw()

	def on_text_update(self):
		command_dict = self.command_dict

		current_line = self.get_current_line()
		cmd_strings = self.parse_command_strings_from_line(current_line)
		
		self.helper_text = ""
		
		if self.current_line_is_complete():
			self.clear_current_line()

			message_center.add_message(" ")
			message_center.add_message(">>> " + current_line)
			
			if len(cmd_strings) == 0 : # User has entered blank command
				return
			
			command_string = cmd_strings.pop(0)
			
			try:
				if command_string not in command_dict:
					raise StandardCommandError("Unrecognized Command: " + command_string)
			
				command_object = command_dict[command_string]
			
				if len(command_object.arg_handlers) != len(cmd_strings):
					raise StandardCommandError("Wrong number of arguments for %s. Try 'help %s' for more information." % (command_string, command_string))
			
				arg_objects = []	
				for arg_string, arg_handler in zip(cmd_strings, command_object.arg_handlers):
					try:
						arg_objects.append(arg_handler.get_target_for_arg_string(arg_string))
					except ArgumentError, e:
						message_center.add_message("Invalid argument: %s " % str(e), "terminal_error")
						arg_objects.append(None)
				
				if None in arg_objects:
					raise StandardCommandError("Could not parse arguments; see previous errors. Try 'help %s' for command help." % command_string)
			
				### If we made it this far, we have a valid command object which accepts the argument objects we have retreived.
				command_object.execute(arg_objects)
			except StandardCommandError as e:
				message_center.add_message(str(e), "terminal_error")
				
			self.on_text_update()
		else:
			# Command line is not complete; this is where we do context help.
			if len(cmd_strings) == 0: # Nothing useful has been entered.
				self.helper_text = ", ".join(sorted(command_dict.keys()))
			elif len(cmd_strings) == 1: # Command completion
				command_in_progress = cmd_strings[0]
				possible_completions = [command  for command in command_dict.keys() if command.startswith(command_in_progress)]
				if len(possible_completions) > 0:
					self.helper_text = ", ".join(sorted(possible_completions))
				else:
					self.helper_text = "Unrecognized Command"
			else:
				command_string = cmd_strings.pop(0)
				if command_string not in command_dict:
					self.helper_text = "Unrecognized Command"
				else:
					command_object = command_dict[command_string]
										
					if len(cmd_strings) > len(command_object.arg_handlers):
						self.helper_text = "Too many arguments!"
					else:
						arg_number = len(cmd_strings)-1
						arg_string = cmd_strings[arg_number]
						
						self.helper_text = command_object.arg_handlers[arg_number].context_help_for_arg_string(arg_string)
		
	### END ON_TEXT_UPDATE

	def tab_complete_and_return_line(self, line):
		command_dict = self.command_dict
		cmd_strings = self.parse_command_strings_from_line(line)
		if len(cmd_strings) == 0: # Nothing useful has been entered.
				return line
		elif len(cmd_strings) == 1: # Command completion
			command_in_progress = cmd_strings[0]
			possible_completions = [command  for command in command_dict.keys() if command.startswith(command_in_progress)]
			if len(possible_completions) == 1:
				complete_command = possible_completions[0]
				cmd_strings[0] = complete_command
			elif len(possible_completions) > 1:
				names = possible_completions[:]
				sample_name = names.pop(0)
				matching_length = -1
				still_matching = True
				while still_matching:
					matching_length += 1
					for name in names:
						if name[:matching_length] != sample_name[:matching_length]:
							still_matching = False
							matching_length -= 1
							break
				
				if matching_length > len(cmd_strings[0]):
					cmd_strings[0] = sample_name[:matching_length]
		else:
			command_string = cmd_strings.pop(0)
			if command_string not in command_dict:
				return line
			else:
				command_object = command_dict[command_string]
				
				if len(cmd_strings) > len(command_object.arg_handlers):
					return line
				else:
					arg_number = len(cmd_strings)-1
					arg_string = cmd_strings[arg_number]
					
					cmd_strings[arg_number] = command_object.arg_handlers[arg_number].tab_complete_arg_string(arg_string)
					
					
			cmd_strings.insert(0, command_string)
				
		return " ".join(cmd_strings)

class Command:
	def __init__(self, command_string, function, argument_handlers=[], command_dict=default_command_dict):
		self.string = command_string
		
		self.function = function
		
		self.arg_handlers = list(argument_handlers)
		
		command_dict[command_string] = self
	
	def execute(self, argument_items):
		self.function(argument_items)

class ArgumentHandler:
	def __init__(self, arg_type=ARG_STRING, filter_functions=None):
		self.type = arg_type

		if not getattr(filter_functions, '__iter__', False):
			filter_functions = (filter_functions,)

		self.filters = filter_functions
	
	def get_target_for_arg_string(self, arg_string):
		return arg_string
	
	def get_completions_starting_with(self, arg_string):
		return (arg_string,)
	
	def tab_complete_arg_string(self, arg_string):
		possible_completions = self.get_completions_starting_with(arg_string)

		if len(possible_completions) == 1:
			complete_arg = possible_completions[0]
			return complete_arg
			cmd_strings[0] = complete_command
		elif len(possible_completions) > 1:
			names = possible_completions[:]
			sample_name = names.pop(0)
			matching_length = -1
			still_matching = True
			while still_matching:
				matching_length += 1
				for name in names:
					if name[:matching_length] != sample_name[:matching_length]:
						still_matching = False
						matching_length -= 1
						break
			
			if matching_length > len(arg_string):
				return sample_name[:matching_length]
			else:
				return arg_string
		else:
			return arg_string
		
	
	def context_help_for_arg_string(self, arg_string):
		return """Enter some text that starts and ends with a double-quote (")."""
	
class GameObjectArgumentHandler(ArgumentHandler):
	def __init__(self, arg_type=ARG_OBJECT, filter_functions=[], search_dict=None, no_target_message="No targets available for this command; Try a different command."):
		ArgumentHandler.__init__(self, arg_type=arg_type, filter_functions=filter_functions)
		self.no_target_message = no_target_message
		self.search_dict = search_dict
	
	def get_target_for_arg_string(self, arg_string):
		if arg_string in self.search_dict:
			target = self.search_dict[arg_string]
			
			for filter_function in self.filters:
				if not filter_function(target):
					return None
			
			return target
		else:
			return None

	def get_completions_starting_with(self, arg_string):
		possible_completions = [string  for string in self.search_dict.keys() if string.startswith(arg_string)]
		for filter_function in self.filters:
			possible_completions = [name for name in possible_completions if filter_function(self.search_dict[name])]
		possible_completions.sort()
		return possible_completions
	
	def context_help_for_arg_string(self, arg_string):
		completions = self.get_completions_starting_with(arg_string)
		if len(completions) > 0 :
			return ", ".join(completions)
		else:
			return self.no_target_message


class StringArgumentHandler(ArgumentHandler):
	def __init__(self, arg_type=ARG_OBJECT, filter_functions=[], help_message="Enter a string."):
		ArgumentHandler.__init__(self, arg_type=arg_type, filter_functions=filter_functions)
		
		self.help_message = help_message

	def get_target_for_arg_string(self, arg_string):
		return arg_string
	
	def context_help_for_arg_string(self, arg_string):
		return self.help_message

class IntegerArgumentHandler(ArgumentHandler):
	def __init__(self, arg_type=ARG_OBJECT, filter_functions=[], help_message="Enter an integer."):
		ArgumentHandler.__init__(self, arg_type=arg_type, filter_functions=filter_functions)
		
		self.help_message = help_message

	def get_target_for_arg_string(self, arg_string):
		try:
			return int(arg_string)
		except ValueError:
			return None
	
	def context_help_for_arg_string(self, arg_string):
		return self.help_message

class MultipleChoiceArgumentHandler(ArgumentHandler):
	def __init__(self, arg_type=ARG_OBJECT, filter_functions=[], choices=["yes","no"]):
		ArgumentHandler.__init__(self, arg_type=arg_type, filter_functions=filter_functions)
		
		self.choices = choices
	
	def get_target_for_arg_string(self, arg_string):
		if arg_string in self.choices:
			return arg_string
		else:
			message_center.add_message(channel="error",message="'%s' is not a valid choice here." % arg_string)
			return None
	
	def context_help_for_arg_string(self, arg_string):
		return ", ".join(self.get_completions_starting_with(arg_string))

	def get_completions_starting_with(self, arg_string):
		possible_completions = [string  for string in self.choices if string.startswith(arg_string)]
		
		return possible_completions
