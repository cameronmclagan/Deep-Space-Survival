import pickle

import event

import key_set
import command_line
import message_center

terminal_search_dict = {}

int_to_en =('zeroth', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth',
			'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth',
			'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth',
			'eighteenth', 'nineteenth', 'twentieth' )

class GameState(event.EventDispatcher):
	def __init__(self):
		self.key_set = key_set.KeySet()
		
		self.command_dict = {}
		self.marker_dict = {}
		self.template_dict = {}
		
		self.focus_stack = []
		
		global terminal_search_dict
		self.focus_object_argument = command_line.GameObjectArgumentHandler(search_dict=terminal_search_dict, filter_functions=(lambda x: hasattr(x,"focus_commands"),))

		self.focus_command = command_line.Command("focus", self.focus_on_marker, (self.focus_object_argument,))
		self.defocus_command = command_line.Command("defocus", self.defocus)
	
	def save_to_file(self, filename):
		"""Saves the entire GameState instance to a file using the standard
		pickle module. It is possible that a game could attach things to the
		state in such a way that they would not be saved correctly. It is also
		possible that attaching certain things to the state will cause saving
		to crash the program. This behaviour is poorly tested at the time of
		this writing."""
		save_file = open(filename,'w')
		pickle.dump(self.key_set, save_file)
		pickle.dump(self.marker_dict, save_file)
		pickle.dump(self.template_dict, save_file)
		pickle.dump(self.focus_stack, save_file)
		save_file.close()
		message_center.add_message("\nGame saved!\n")

	def load_from_file(self, filename):
		save_file = open(filename,'r')
		GameState.__init__(self)
		self.key_set = pickle.load(save_file)
		self.marker_dict = pickle.load(save_file)
		self.template_dict = pickle.load(save_file)
		self.focus_stack = pickle.load(save_file)
		save_file.close()
		message_center.add_message("="*10 + "\nGame loaded!\n")
		if len(self.focus_stack) > 0:
			self.focus_stack[-1].on_focus()
		self.__refresh_focus_info()
		
	def get_marker(self, identifier):
		"""Retreives the GameMarker instance associated with identifier. This
		is usually not what you want; use the get_object method to retreive the
		data that the marker represents."""
		return self.marker_dict[identifier]
	
	def get_object(self, identifier):
		"""Retreives the data represented by the GameMarker associated with
		identifier. This is preferred over get_marker since GameMarker instances
		should not generally be manipulated outside their originating GameState."""
		return self.marker_dict[identifier].object
	
	def get_children_of(self, identifier):
		"""Returns a list of identifiers for all the children of the GameMarker
		associated with identifier. These identifiers can then be used with
		get_object to get the actual data."""
		return [marker.identifier for marker in self.marker_dict[identifier].marker_list]
	
	def get_focus_identifier(self):
		"""Returns the identifier associated with the GameMarker at the top of
		the focus_stack."""
		if len(self.focus_stack) > 0:
			return self.focus_stack[-1].identifier
		else:
			return None
	
	def get_focus_object(self):
		"""Returns the data attached to the GameMarker at the top of the
		focus_stack."""
		if len(self.focus_stack) > 0:
			return self.focus_stack[-1].object
		else:
			return None
	
	def create_marker(self, identifier, game_object, location=None, **kwargs):
		"""Creates a new GameMarker instance named identifier to represent
		game_object. If location is omitted, the marker will be created outside
		of the game. If locations is specified, it should be the identifier of
		and existing marker which will be the parent of the new marker upon
		creation. Additional keyword arguments, if specified, will be passed
		directly to the new GameMarker upon creation; see the GameMarker
		documentation for details."""
		if location != None:
			location = self.marker_dict[location]
		new_marker = GameMarker(identifier=identifier, game_object=game_object, location=location, **kwargs)
		if identifier in self.marker_dict:
			self.destroy_marker(identifier)
		self.marker_dict[identifier] = new_marker
		self.__refresh_focus_info()
		return new_marker
	
	def destroy_marker(self, identifier):
		"""Destroys the identified marker by moving it outside the game and
		then deleting all references to it. If the destroyed marker has any
		children they are NOT DESTROYED and are moved to the destroyed marker's
		last location. This does not affect any of the data associated with
		the marker. This method is one of the reasons that markers should not
		generally be accessed outside the GameState; destroying a marker with
		this method will do nothing to clean up any outside references."""
		target_marker = self.marker_dict[identifier]

		for marker in target_marker.marker_list:
			marker.move_to_marker(target_marker.location)
		
		self.marker_dict[identifier].move_to_marker(None)
		del self.marker_dict[identifier]
		self.__refresh_focus_info()
	
	def move_marker(self, identifier, destination):
		"""Moves the GameMarker associated with identifier to the GameMarker
		associated with destination. This is the correct way to move markers
		around; do not use get_marker to retrieve and alter the markers directly."""
		if destination != None:
			self.marker_dict[identifier].move_to_marker(self.marker_dict[destination])
		else:
			self.marker_dict[identifier].move_to_marker(None)
		self.__refresh_focus_info()

	def focus_on_marker(self, identifier, *args):
		"""Pushes the GameMarker associated with identifier onto the focus_stack
		and updates the rest of the GameState accordingly."""
		if isinstance(identifier, GameMarker):
			target_marker = identifier
		else:
			target_marker = self.marker_dict[identifier]
		if (len(self.focus_stack) == 0) or (self.focus_stack[-1] != target_marker):
			self.focus_stack.append(target_marker)
		target_marker.on_focus()
		self.__refresh_focus_info()
		
	def defocus(self, *args):
		"""Pops the top GameMarker off of the focus_stack. This doesn't actually
		return any information about the removed marker."""
		if len(self.focus_stack) > 0:
			x = self.focus_stack.pop()
			x.on_defocus()
			self.__refresh_focus_info()
			if len(self.focus_stack) > 0:
				self.focus_stack[-1].on_focus()
			
	
	def refocus_on_marker(self, identifier, *args):
		"""Replaces the current top of the focus_stack with the GameMarker
		associated with identifier. This is equivalent to calling defocus()
		followed by focus_on_marker(identifier)."""
		self.defocus(*args)
		self.focus_on_marker(identifier, *args)

	def __new_command_dict(self, command_dict):
		self.command_dict = command_dict
		
		if len(self.focus_object_argument.get_completions_starting_with("")) > 0 :
			self.command_dict["focus"] = self.focus_command
		
		if len(self.focus_stack) > 1:
			self.command_dict["defocus"] = self.defocus_command
		
#		if len(self.move_target_argument.get_completions_starting_with("")) > 0 :
#			self.command_dict["move"] = self.move_command
		
		self.dispatch_event('on_new_command_dict', command_dict)
	
	def __refresh_focus_info(self):
		if len(self.focus_stack) > 0:
			#self.focus_stack[-1].on_focus()
		
			self.__refresh_terminal_search_dict()
			
			self.__new_command_dict(self.focus_stack[-1].focus_commands)
		else:
			terminal_search_dict.clear()
			self.__new_command_dict({})

	def __refresh_terminal_search_dict(self):
		global terminal_search_dict, int_to_en
		visible_markers = self.focus_stack[-1].get_children()
		
		terminal_search_dict.clear()
		duplicate_target_counters = {}
		for marker in visible_markers:
			if marker.visible_name in duplicate_target_counters:
				duplicate_target_counters[marker.visible_name] += 1
				terminal_search_dict[int_to_en[duplicate_target_counters[marker.visible_name]] + "_" + marker.visible_name] = marker
			elif marker.visible_name in terminal_search_dict:
				terminal_search_dict[int_to_en[1] + "_" + marker.visible_name] = terminal_search_dict[marker.visible_name]
				terminal_search_dict[int_to_en[2] + "_" + marker.visible_name] = marker
				duplicate_target_counters[marker.visible_name] = 2
				del terminal_search_dict[marker.visible_name]
			else:
				terminal_search_dict[marker.visible_name] = marker
			
			#self.__new_command_dict(self.focus_stack[-1].focus_commands)
	
GameState.register_event_type('on_new_command_dict')

current_state = GameState()

def load_game_state_from_file(filename):
	current_state.load_from_file(filename)

def save_game_state_to_file(filename):
	current_state.save_to_file(filename)

class GameMarker:
	"""A class which represents any discrete game entity. Instances of this
	class can be targetted by the player. Instances of this class should be
	created by a GameState implementation, rather than directly by the game.
	Once created, they should also be manipulated by the GameState. In short,
	this class should never be used outside of GameState or some derivative
	implementation."""
	def __init__(self, identifier, game_object, location=None, destination=None, auto_focus=False):
		self.identifier = identifier
	
		self.object = game_object
		
		self.location = None
		self.move_to_marker(location)
		
		self.destination = destination
		
		self.marker_list = []
		
	@property
	def visible_name(self):
		if hasattr(self.object, "formatted_name"):
			return self.object.formatted_name
		else:
			return self.identifier
	
	@property
	def focus_commands(self):
		if hasattr(self.object, "focus_commands"):
			return self.object.focus_commands
		else:
			return None
		
	def move_to_marker(self, target_marker):
		"""This sets a new location for the marker, including updating both of
		the other markers involved as necessary. To move a marker out of the
		game, simply pass None as the target of this function; it will become
		inaccessible until moved back to a marker. To destroy a marker
		permanently, use GameInstance.destroy_marker(identifier)."""
		if self.location != None:
			self.location.rem_marker(self)
		
		self.location = target_marker
		
		if self.location != None:
			self.location.add_marker(self)
	
	def add_marker(self, marker):
		"""Adds a marker to this marker. Don't call this; use the move_to_marker
		method of the marker you want to add."""
		self.marker_list.append(marker)
		
	def rem_marker(self, marker):
		"""Removes a marker from this marker. Don't call this; use the
		move_to_marker method of the marker you want to remove."""
		try:
			self.marker_list.remove(marker)
		except ValueError:
			pass
	
	def get_children(self):
		"""Return a list of all markers directly attached to this one."""
		return self.marker_list[:]

	def on_focus(self):
		if hasattr(self.object, "on_focus"):
			self.object.on_focus()
	
	def on_defocus(self):
		if hasattr(self.object, "on_defocus"):
			self.object.on_defocus()

	
#	def is_spawned(self):
#		"""Returns True if the marker should be active based on its spawn keys. Compares the keys_for_spawn and keys_for_despawn lists against the KeySet of the current GameState. In short: The marker is inactive until the player has all of the keys in the keys_for_spawn list. If that list is empty, the marker is active immediately when created. The marker will become inactive """
#		
#		for key in self.keys_for_spawn:
#			if not game_state.current_state.key_set.has_key(key):
#				return False # We are returning False (marker not visible) if the player is missing any of the spawn keys.
#		
#		# If we reach this point, the marker has spawned either because it has no spawn keys or because the player has them all.
#		
#		if len(self.keys_for_despawn) == 0 :
#			return True # If there are no despawn keys, the marker can't despawn.
#		
#		for key in self.keys_for_despawn:
#			if not game_state.current_state.key_set.has_key(key):
#				return True # We are returning True (marker is visible) if the player is missing any of the despawn keys.
#		
#		return False # Finally, at this point we know the player has all the despawn keys so the marker is gone now. Return False.

