import pygame

class Drawable:
	def __init__(self, rect, identifier=None):
		self.identifier = identifier
		self.rect = None
		self.set_rect(rect)

	def draw_to_surface(self, surface):
		pass
	
	def set_rect(self, rect):
		new_rect = pygame.Rect(rect)
		if self.rect != new_rect:
			self.rect = new_rect
			self.reset_for_new_rect()
	
	def reset_for_new_rect(self):
		pass
	
	def on_mouse_hover(self, pos):
		pass
	
	def on_mouse_unhover(self, pos):
		pass
	
	def on_mouse_leftclick(self, pos):
		pass
	
	def on_mouse_rightclick(self, pos):
		pass

class Filler(Drawable):
	pass
	
class Container(Drawable):
	def __init__(self, rect, identifier=None):
		self.contents = []

		Drawable.__init__(self, rect, identifier)
	
	def draw_to_surface(self, surface):
		for drawable in self.contents:
			drawable.draw_to_surface(surface)
	
	def add(self, drawable):
		if isinstance(drawable, Drawable):
			self.contents.append(drawable)
		else:
			raise Exception("Non-Drawable object added to Drawable container.")
	
	def search_for_identifier(self, identifier):
		if self.identifier == identifier:
			return self
		else:
			for drawable in self.contents:
				if isinstance(drawable, Container):
					search_val = drawable.search_for_identifier(identifier)
					if search_val != None: return search_val
				else:
					if drawable.identifier == identifier:
						return drawable
		return None
	
	def __getitem__(self, name):
		item = self.search_for_identifier(name)
		return item
	
	def search_for_collision(self, point):
		collide_list = []
		if self.rect.collidepoint(point):
			collide_list.append(self)
			for drawable in self.contents:
				if isinstance(drawable, Container):
					collide_list += drawable.search_for_collision(point)
				else:
					if drawable.rect.collidepoint(point):
						collide_list.append(drawable)
		return collide_list
			

class Root(Container):
	def add(self, drawable):
		Container.add(self, drawable)
		drawable.set_rect(self.rect)
	
	def reset_for_new_rect(self):
		for drawable in self.contents:
			drawable.set_rect(self.rect)
	
	def get_next_rect(self):
		return self.rect

class BorderBox(Container):
	def __init__(self, rect, identifier=None, margin=3, padding=5, border=2, bg_color=(0x00,0x00,0x00),fg_color=(0xFF,0xFF,0xFF)):
		self.margin=int(margin)
		self.border=int(border)
		self.padding=int(padding)
		self.bg_color = bg_color
		self.fg_color = fg_color
		self.fill_color = self.bg_color
		Container.__init__(self, rect, identifier)

	def add(self, drawable):
		Container.add(self, drawable)
		drawable.set_rect(self.content_rect)
	
	def reset_for_new_rect(self):
		self.border_rect = self.rect.inflate(self.margin*-2,self.margin*-2)
		self.back_rect = self.border_rect.inflate(self.border*-2, self.border*-2)
		self.content_rect = self.back_rect.inflate(self.padding*-2, self.padding*-2)
		for drawable in self.contents:
			drawable.set_rect(self.content_rect)
	
	def get_next_rect(self):
		return self.content_rect
	
	def draw_to_surface(self, surface):
		surface.fill(self.fg_color, self.border_rect)
		surface.fill(self.fill_color, self.back_rect)
		for drawable in self.contents:
			drawable.draw_to_surface(surface)

class LinearRatioContainer(Container):
	def __init__(self, rect, ratio=(1,1,1), identifier=None):
		self.ratio = ratio
		Container.__init__(self, rect, identifier)

	def set_length(self, length):
		self.cell_length_list = []
		
		ratio_total = 0
		for val in self.ratio:
			print val
			ratio_total += val
		
		length_total = 0
		for val in self.ratio:
			fraction = float(val)/float(ratio_total)
			self.cell_length_list.append(int(float(length)*float(fraction)))
			length_total += self.cell_length_list[-1]
		
		for x in xrange(length-length_total):
			self.cell_length_list[-1] += 1
		
		self.cell_offset_list = []
		
		offset = 0
		for l in self.cell_length_list:
			self.cell_offset_list.append(offset)
			offset += l
			
class Row(LinearRatioContainer):
	def add(self, drawable):
		rect = self.get_next_rect()

		Container.add(self, drawable)
		drawable.set_rect(rect)
	
	def reset_for_new_rect(self):
		length = self.rect.width
		self.set_length(length)
		contents_copy = self.contents
		self.contents = []
		for drawable in contents_copy:
			self.add(drawable)
		
	def get_next_rect(self):
		i = len(self.contents)
		i %= len(self.cell_length_list)
		x = self.rect.x + self.cell_offset_list[i]
		y = self.rect.y
		w = self.cell_length_list[i]
		h = self.rect.height
		return (x, y, w, h)				

class Column(LinearRatioContainer):
	def add(self, drawable):
		rect = self.get_next_rect()
		
		Container.add(self, drawable)
		drawable.set_rect(rect)
	
	def reset_for_new_rect(self):
		length = self.rect.height
		self.set_length(length)
		contents_copy = self.contents
		self.contents = []
		for drawable in contents_copy:
			self.add(drawable)

	def get_next_rect(self):
		i = len(self.contents)
		i %= len(self.cell_length_list)
		x = self.rect.x
		y = self.rect.y + self.cell_offset_list[i]
		w = self.rect.width
		h = self.cell_length_list[i]
		return (x, y, w, h)


