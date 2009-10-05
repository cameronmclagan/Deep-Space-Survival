import re, pygame

def make_line_break_events_based_on_text_width_and_font(text, width, font):
	break_list = []

	current_start = 0
	current_end = 0
	while current_start < len(text)-1 :
		# Grow slice until too long
		while(font.size(text[current_start:current_end])[0] < width):
			current_end += 1
			if current_end >= len(text) or text[current_end] == "\n":
				break
		
		if(current_end >= len(text)):
			# We hit the end of the string. Step back one and let it drop.
			current_end -= 1
		elif(text[current_end] == "\n"):
			# Stopped due to manual line break. Stay right where we are and let it drop.
			pass
		else:
			# Slice got too big before end of string. Rewind one letter first (since the last one is the one that doesn't fit!)
			current_end -= 1
			# Pull back to nearest space, but don't get trapped if there are no spaces!
			original_end = current_end
			while(text[current_end-1] != ' '):
				current_end -= 1
				if(current_end == current_start):
					# Must not be any spaces! If you can't break nicely, just break correctly!
					current_end = original_end
					break
		# After all that, current_start should be the beginning of a line and current_end
		# should be the end of that line, breaking at spaces if at all possible. We just
		# save these to the slice list, and bring the start point up to the end of this line.
		break_list.append(current_end)
		current_start = current_end
		
	# At this point current_start is equal to the length of the string, which means we're done slicing.
	# All that's left is returning the slice information so that some other code can use it.
	return break_list

def do_text_substitution_using_dictionary(text, dictionary):
	keyword_finder = re.compile(r"\%\{(\w+)\}\%")
	keyword_list = keyword_finder.findall(text)

	for keyword in keyword_list:
		temp_sub_re = re.compile( r"\%\{" + keyword + r"\}\%")
		try:
			text = temp_sub_re.sub(dictionary[keyword], text)
		except KeyError:
			print "Key", keyword, "not found! Substitution failed."

	return text

def make_color_change_events_for_text(text):
	color_change_list = []

	color_finder = re.compile(r"\#\{([0-9a-fA-F]{6,6})\}\#")

	match = color_finder.search(text)

	while match != None :
		color_string = match.group(1)
		red = int(color_string[0:2], 16)
		green = int(color_string[2:4], 16)
		blue = int(color_string[4:6], 16)
		color_change_list.append((match.start(), (red, green, blue)))
		text = color_finder.sub('', text, 1)
		match = color_finder.search(text)

	return text, color_change_list

pygame.font.init()

class TextObject:
	def __init__(self, text="", font_name="Droid Sans,Bitstream Vera Sans", font_size=16, sub_dict={}):
		self.original_text = text
		self.font = pygame.font.SysFont(font_name, font_size)
		self.sub_dict = sub_dict
		self.reset()

	def reset(self):
		self.text = self.original_text + " "
		self.text = do_text_substitution_using_dictionary(self.text, self.sub_dict)
		self.text, self.color_changes = make_color_change_events_for_text(self.text)
		self.line_breaks = []
	
	def replace_text(self, new_text):
		self.original_text = new_text
		self.reset()
	
	def add_text(self, new_text):
		self.replace_text(self.original_text + new_text)
	
	def break_for_width(self, width):
		self.line_breaks = make_line_break_events_based_on_text_width_and_font(self.text, width, self.font)

class SurfaceAnchoredText:
	def __init__(self, surface, text_object=None, fg_color=(0x00,0x00,0x00), bg_color=(0xFF,0xFF,0xFF)):
		self.surface = surface

		if text_object == None: text_object = TextObject()
		self.text_object = text_object
		
		self.fg_color = fg_color
		self.bg_color = bg_color
		
		self.make_line_surfaces()
	
	def replace_text(self, new_text):
		self.text_object.replace_text(new_text)
		self.make_line_surfaces()
	
	def add_text(self, new_text):
		self.text_object.add_text(new_text)
		self.make_line_surfaces()
	
	def make_line_surfaces(self):
		surface_list = []
		
		current_fg_color = self.fg_color
		
		current_break_index = 0
		current_color_index = 0

		self.text_object.break_for_width(self.surface.get_width())
		
		text = self.text_object.text
		font = self.text_object.font
		color_changes = self.text_object.color_changes
		line_breaks = self.text_object.line_breaks
		surface = self.surface
		
		color_changes.sort()
		line_breaks.sort()
		
		sub_line_list = []
		
		last_draw_end = 0
		
		n = 0
		while n < len(text) :
			if current_color_index < len(color_changes) and color_changes[current_color_index][0] == n :
				sub_line_list.append(font.render(text[last_draw_end:n].strip("\n"), True, current_fg_color))
				current_fg_color = color_changes[current_color_index][1]
				current_color_index += 1
				last_draw_end = n
			
			if current_break_index < len(line_breaks) and line_breaks[current_break_index] == n :
				sub_line_list.append(font.render(text[last_draw_end:n].strip("\n"), True, current_fg_color))
				temp_surface = pygame.Surface((surface.get_width(), sub_line_list[0].get_height())).convert_alpha()
				temp_surface.fill((0,0,0,0))
				x_offset = 0
				for s in sub_line_list :
					temp_surface.blit(s, (x_offset, 0))
					x_offset += s.get_width()
				surface_list.append(temp_surface)
				current_break_index += 1
				last_draw_end = n
				sub_line_list = []
			
			n += 1
		
		self.line_surfaces = surface_list
		
		total_height = 0
		for line_surface in self.line_surfaces:
			total_height += line_surface.get_height()
		
		if total_height <= self.surface.get_height():
			self.draw_from_bottom_up = False
		else:
			self.draw_from_bottom_up = True
	
	def draw(self):
		self.surface.fill(self.bg_color)
	
		if self.draw_from_bottom_up:
			y_offset = self.surface.get_height()
			for s in reversed(self.line_surfaces) :
				y_offset -= s.get_height()
				if y_offset < 0:
					break
				else:
					self.surface.blit(s, (0, y_offset))
		else:
			y_offset = 0
			for s in self.line_surfaces :
				if y_offset > self.surface.get_height():
					break
				else:
					self.surface.blit(s, (0, y_offset))
				y_offset += s.get_height()
