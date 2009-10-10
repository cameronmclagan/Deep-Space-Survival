import pickle

import event

import key_set
import command_line

terminal_search_dict = {}

class GameState(event.EventDispatcher):
	def __init__(self):
		self.key_set = key_set.KeySet()
		
		self.command_dict = {}
		
		self.marker_dict = {}
		
		
		self.focus_stack = []
		self.visible_marker_dict = {}
		
		global terminal_search_dict
		self.focus_object_argument = command_line.GameObjectArgumentHandler(search_dict=terminal_search_dict, filter_functions=(lambda x: (isinstance(x, FocusTarget) and x.focus_commands),))
		self.move_target_argument = command_line.GameObjectArgumentHandler(search_dict=terminal_search_dict, filter_functions=(lambda x: (hasattr(x, 'destination') and isinstance(x.destination, FocusTarget)),))


		self.focus_command = command_line.Command("focus", self.focus_on_marker, (self.focus_object_argument,))
		self.defocus_command = command_line.Command("defocus", self.defocus)
		self.move_command = command_line.Command("move", self.move_through_object, (self.move_target_argument,))
	
	def copy():
		state_copy = GameState()
		
		state_copy.key_set = self.key_set.copy()
		state_copy.command_dict = self.command_dict
		
	def save_to_file(self, filename):
		file = open(filename,'w')
		pickle.dump(self, file)
		
	def new_command_dict(self, command_dict):
		self.command_dict = command_dict
		
		if len(self.focus_object_argument.get_completions_starting_with("")) > 0 :
			self.command_dict["focus"] = self.focus_command
		
		if len(self.focus_stack) > 1:
			self.command_dict["defocus"] = self.defocus_command
		
		if len(self.move_target_argument.get_completions_starting_with("")) > 0 :
			self.command_dict["move"] = self.move_command
		
		self.dispatch_event('on_new_command_dict', command_dict)
	
	def get_marker_for_identifier(self, identifier):
		if identifier in self.marker_dict:
			return self.marker_dict[identifier]
		else:
			return self.new_marker_for_identifier(identifier)
		
	def new_marker_for_identifier(self, identifier, **kwargs):
		new_marker = GameMarker(identifier=identifier, **kwargs)
		self.marker_dict[identifier] = new_marker
		return new_marker
	
	def destroy_marker(self, identifier):
		if identifier in self.marker_dict:
			target_marker = self.marker_dict[identifier]
		
			self.marker_dict[identifier].move_to_marker(None)
			for marker in target_marker.marker_list:
				target_marker.move_to_marker(None)
		
			del self.marker_dict[identifier]
	
	def focus_on_marker(self, *args):
		target_marker = args[0]
		if (len(self.focus_stack) == 0) or (self.focus_stack[-1] != target_marker):
			self.focus_stack.append(target_marker)
		
		self.refresh_focus_info()
		
	def defocus(self, *args):
		if len(self.focus_stack) > 0:
			x = self.focus_stack.pop()
			x.on_defocus()
		
		self.refresh_focus_info()
	
	def refocus_on_marker(self, *args):
		self.defocus(*args)
		self.focus_on_marker(*args)
	
	def move_through_object(self, *args):
		object = args[0]
		self.refocus_on_marker(object.destination)
	
	def refresh_focus_info(self):
		global terminal_search_dict
		if len(self.focus_stack) > 0:
			self.focus_stack[-1].on_focus()
			visible_markers = self.focus_stack[-1].get_visible_markers()
		
			terminal_search_dict.clear()
			for marker in visible_markers:
				terminal_search_dict[marker.visible_name] = marker

			self.new_command_dict(self.focus_stack[-1].focus_commands)
		else:
			terminal_search_dict.clear()
			self.new_command_dict({})

	
		

#GameState.register_event_type('on_location_change')
#GameState.register_event_type('on_location_change')
GameState.register_event_type('on_new_command_dict')

current_state = GameState()

def load_game_state_from_file(filename):
	file = open(filename, 'r')
	loaded_state = pickle.load(file)
	global current_state
	current_state = loaded_state

def save_game_state_to_file(filename):
	current_state.save_to_file(filename)

class FocusTarget:
	def __init__(self, focus_commands, auto_focus=False, add_keys_on_focus=(), rem_keys_on_focus=(), have_keys_while_focus=()):
		self.focus_commands = focus_commands
		self.auto_focus = auto_focus
		
		self.add_keys_on_focus = add_keys_on_focus
		self.rem_keys_on_focus = rem_keys_on_focus
		self.have_keys_while_focus = have_keys_while_focus
	
	def on_focus(self):
		self.do_focus_keys()
		if hasattr(self, 'object') and hasattr(self.object, 'on_focus'):
			self.object.on_focus()
	
	def do_focus_keys(self):
		for key in self.add_keys_on_focus:
			current_state.key_set.add_key(key)
		
		for key in self.rem_keys_on_focus:
			current_state.key_set.rem_key(key)
		
		for key in self.have_keys_while_focus:
			current_state.key_set.add_key(key)
	
	def on_defocus(self):
		self.do_defocus_keys()
	
	def do_defocus_keys(self):
		for key in self.have_keys_while_focus:
			current_state.key_set.rem_key(key)

class GameMarker(FocusTarget):
	"""A class which represents any discrete game entity. Instances of this class can  and can be targetted by the player."""
	def __init__(self, identifier, visible_name=None, object=None, location=None, destination=None, keys_for_spawn=(), keys_for_despawn=(), focus_commands={}, auto_focus=False, add_keys_on_focus=(), rem_keys_on_focus=()):
		self.identifier = identifier
		if visible_name == None: visible_name = identifier
		self.visible_name = visible_name
		
		self.object = object
		
		self.location = None
		self.move_to_marker(location)
		
		self.destination = destination
		
		self.keys_for_spawn = keys_for_spawn
		self.keys_for_despawn = keys_for_despawn
		
		self.marker_list = []
		
		FocusTarget.__init__(self, focus_commands=focus_commands, auto_focus=auto_focus, add_keys_on_focus=add_keys_on_focus, rem_keys_on_focus=rem_keys_on_focus)
		
		self.map_name = None
		self.map_coordinates = None

	def move_to_marker(self, target_marker):
		"""This sets a new location for the marker, including updating both of the other markers involved as necessary. To move a marker out of the game, simply pass None as the target of this function; it will become inaccessible until moved back to a marker. To destroy a marker permanently, use GameInstance.destroy_marker(identifier)."""
		if self.location != None:
			self.location.rem_marker(self)
		
		self.location = target_marker
		
		if self.location != None:
			self.location.add_marker(self)
	
	def add_marker(self, marker):
		"""Adds a marker to this marker. Don't call this; use the move_to_marker method of the marker you want to add."""
		self.marker_list.append(marker)
		
	def rem_marker(self, marker):
		"""Removes a marker from this marker. Don't call this; use the move_to_marker method of the marker you want to remove."""
		try:
			self.marker_list.remove(marker)
		except ValueError:
			pass
	
	def is_spawned(self):
		"""Returns True if the marker should be active based on its spawn keys. Compares the keys_for_spawn and keys_for_despawn lists against the KeySet of the current GameState. In short: The marker is inactive until the player has all of the keys in the keys_for_spawn list. If that list is empty, the marker is active immediately when created. The marker will become inactive """
		
		for key in self.keys_for_spawn:
			if not game_state.current_state.key_set.has_key(key):
				return False # We are returning False (marker not visible) if the player is missing any of the spawn keys.
		
		# If we reach this point, the marker has spawned either because it has no spawn keys or because the player has them all.
		
		if len(self.keys_for_despawn) == 0 :
			return True # If there are no despawn keys, the marker can't despawn.
		
		for key in self.keys_for_despawn:
			if not game_state.current_state.key_set.has_key(key):
				return True # We are returning True (marker is visible) if the player is missing any of the despawn keys.
		
		return False # Finally, at this point we know the player has all the despawn keys so the marker is gone now. Return False.

	def get_visible_markers(self):
		"""Return a list of all markers attached to this one who should be visible to the player (the term 'visible' is used loosely; any marker that meets its own spawn conditions is considered visible)."""
		visible_markers = []
		for marker in self.marker_list:
			if marker.is_spawned():
				visible_markers.append(marker)
		return visible_markers
