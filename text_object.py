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
		text = temp_sub_re.sub(dictionary.get(keyword,""), text)

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
	def __init__(self, width, text="", font_name="Droid Sans,Bitstream Vera Sans", font_size=16, font_color=(0xFF,0xFF,0xFF), font_bold=False, font_italic=False, sub_dict={}):
		self.width = width
		self.original_text = text
		self.font = pygame.font.SysFont(font_name, font_size, font_bold, font_italic)
		self.font_color=font_color
		self.sub_dict = sub_dict
		self.reset()

	def reset(self):
		self.text = self.original_text + " "
		self.text = do_text_substitution_using_dictionary(self.text, self.sub_dict)
		self.text, self.color_changes = make_color_change_events_for_text(self.text)
		self.line_breaks = make_line_break_events_based_on_text_width_and_font(self.text, self.width, self.font)
		self.make_line_surfaces()
		self.make_finished_surface()
	
	def replace_text(self, new_text):
		self.original_text = new_text
		self.reset()
	
	def add_text(self, new_text):
		self.replace_text(self.original_text + new_text)
	
	def set_width(self, width):
		self.width = width
		self.reset()
	
	def make_line_surfaces(self):
		surface_list = []
		
		current_fg_color = self.font_color
		
		current_break_index = 0
		current_color_index = 0

		text = self.text
		font = self.font
		color_changes = self.color_changes
		line_breaks = self.line_breaks
		
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
				temp_surface = pygame.Surface((self.width, sub_line_list[0].get_height())).convert_alpha()
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
	
	def get_total_height(self):
		total_height = 0
		for surface in self.line_surfaces:
			total_height += surface.get_height()
		return total_height
	
	def make_finished_surface(self):
		height = self.get_total_height()
		finished_surface = pygame.Surface((self.width, height)).convert_alpha()
		finished_surface.fill((0,0,0,0))
		y_offset = 0
		for line_surface in self.line_surfaces:
			finished_surface.blit(line_surface,(0, y_offset))
			y_offset += line_surface.get_height()
		self.finished_surface = finished_surface
	
	def get_finished_surface(self):
		return self.finished_surface

class SurfaceAnchoredText:
	def __init__(self, surface, bg_color=(0xFF,0xFF,0xFF), text="", font_name="Droid Sans,Bitstream Vera Sans", font_size=16, font_color=(0xFF,0xFF,0xFF), sub_dict={}):
		self.surface = surface

		self.text_object = TextObject(width=self.surface.get_width(), text=text, font_name=font_name, font_size=font_size, font_color=font_color, sub_dict=sub_dict)
		
		self.bg_color = bg_color
		
	def replace_text(self, new_text):
		self.text_object.replace_text(new_text)
	
	def add_text(self, new_text):
		self.text_object.add_text(new_text)
	
	def draw(self):
		text_surface = self.text_object.finished_surface

		self.surface.fill(self.bg_color, text_surface.get_rect())
	
		if text_surface.get_height() < self.surface.get_height():
			self.surface.blit(text_surface,(0,0))
		else:
			self.surface.blit(text_surface, (0, self.surface.get_height()-text_surface.get_height()))
