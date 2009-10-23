
import pygame
import text_object
import interface_classes

class TerminalDisplay(interface_classes.Drawable):
	def __init__(self,
			rect,
			identifier=None,
			scroll_rate=200,
			fg_color=(0x66,0xDD,0x66),
			bg_color=(0x0C,0x26,0x0C),
			font_name="Droid Sans Mono,Bitstream Vera Sans Mono,Courier",
			font_size=16):
		interface_classes.Drawable.__init__(self, rect, identifier)
		self.scroll_rate = scroll_rate
		self.fg_color = fg_color
		self.bg_color = bg_color
		self.font_name = font_name
		self.font_size = font_size
		
		self.surface = pygame.Surface(self.rect.size)
		self.text_subsurface = self.surface
		
		self.text_object_queue = []
		self.unscrolled_pixels = 0
		
		self.add_message(" ")

	def add_message(self, text, **kwargs):
		kwargs.setdefault("font_color", self.fg_color)
		kwargs.setdefault("font_name", self.font_name)
		kwargs.setdefault("font_size", self.font_size)
		
		new_TO = text_object.TextObject(width=self.text_subsurface.get_width(), text=text, **kwargs)

		self.unscrolled_pixels += new_TO.finished_surface.get_height()
		self.text_object_queue.append(new_TO)

	def internal_redraw(self):
		self.text_subsurface.fill(self.bg_color)
		y_offset = (self.text_subsurface.get_height() + int(self.unscrolled_pixels))
		for t_ob in reversed(self.text_object_queue):
			surface = t_ob.finished_surface
			y_offset -= surface.get_height()
			if y_offset < self.text_subsurface.get_height():
				self.text_subsurface.blit(surface, (0,int(y_offset)))
		
		while y_offset < 0:
			y_offset += self.text_object_queue[0].finished_surface.get_height()
			if y_offset < 0:
				self.text_object_queue.pop(0)
 
	def scroll_by_milliseconds(self, ms):
		if self.unscrolled_pixels > 0:
			rate_fraction = float(ms)/1000.0
			pixels_scrolled = float(self.scroll_rate)*float(rate_fraction)
			self.unscrolled_pixels = float(self.unscrolled_pixels) - float(pixels_scrolled)
			if self.unscrolled_pixels < 0: self.unscrolled_pixels = 0
			self.internal_redraw()
			return pixels_scrolled
		else:
			return 0
	
	def draw_to_surface(self, surface):
		surface.blit(self.surface, self.rect)
		
