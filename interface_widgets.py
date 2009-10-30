import pygame
import resource_loader

import interface_classes

class Label(interface_classes.Drawable):
	def __init__(
			self, rect, identifier=None, text=None,
			bg_color=None, fg_color=(0xFF,0xFF,0xFF), glow_color=None,
			font_name="Droid Sans", font_size="26"):
		
		self.bg_color = bg_color
		self.fg_color = fg_color
		self.glow_color = glow_color
		
		self.stored_text = text

		self.font_name = font_name
		self.font_size = int(font_size)

		interface_classes.Drawable.__init__(self, rect, identifier)
	
	def reset_for_new_rect(self):
		self.font = resource_loader.get_font(self.font_name, self.font_size)
		refresh_text = self.stored_text
		self.stored_text = None
		self.set_text(refresh_text)
	
	def get_text(self):
		return self.stored_text
	
	def set_text(self, new_text):
		if self.stored_text != new_text:
			self.stored_text = new_text
			if self.stored_text != None:
				self.label_surface = self.font.render(str(self.stored_text), True, self.fg_color)

	def draw_to_surface(self, surface):
		if self.bg_color != None:
			surface.fill(self.bg_color, self.rect)
		
		if self.stored_text != None:
			placement_rect = self.label_surface.get_rect()
			placement_rect.center = self.rect.center
#			placement_rect.right = self.rect.right
			surface.blit(self.label_surface, placement_rect)

class Image(interface_classes.Drawable):
	def __init__(self, rect, filename, identifier=None):
		self.filename = filename
		interface_classes.Drawable.__init__(self, rect, identifier)
	
	def draw_to_surface(self, surface):
		placement_rect = self.image_surface.get_rect()
		placement_rect.center = self.rect.center
		surface.blit(self.image_surface, placement_rect)

	def reset_for_new_rect(self):
		image_surface = resource_loader.get_image(self.filename)
		
		image_rect = image_surface.get_rect()
		
		if image_rect.width > self.rect.width or image_rect.height > self.rect.height:
			scaled_rect = image_rect.fit(self.rect)
			image_surface = pygame.transform.smoothscale(image_surface, scaled_rect.size)
		
		self.image_surface = image_surface
		

class MapImage(interface_classes.Drawable):
	def __init__(self, rect, filename, identifier):
		pass

class Button(interface_classes.Drawable):
	def __init__(
			self, rect, identifier=None, label=None,
			bg_color=None, fg_color=(0xFF,0xFF,0xFF), glow_color=None,
			font_name="Droid Sans", font_size="24"):
		
		self.bg_color = bg_color
		self.fg_color = fg_color
		self.glow_color = glow_color
		
		self.mouse_hovering = False
		
		self.function = None

		self.label=label
		self.font = None
		self.label_surface = None

		self.font_name = font_name
		self.font_size = font_size

		interface_classes.Drawable.__init__(self, rect, identifier)
	
	def reset_for_new_rect(self):
		if self.label != None:
			self.font = resource_loader.get_font(self.font_name, int(self.font_size))
			self.label_surface = self.font.render(str(self.label), True, self.fg_color)
	
	def on_mouse_hover(self, pos):
		self.mouse_hovering = True
	
	def on_mouse_unhover(self, pos):
		self.mouse_hovering = False
	
	def on_mouse_leftclick(self, pos):
		if self.function != None:
			self.function()
	
	def set_text(self, new_text):
		if self.label != new_text:
			self.label = new_text
			if self.label != None:
				self.label_surface = self.font.render(str(self.label), True, self.fg_color)

	def draw_to_surface(self, surface):
		if self.mouse_hovering:
			if self.glow_color != None:
				surface.fill(self.glow_color, self.rect)
		else:
			if self.glow_color != None:
				surface.fill(self.bg_color, self.rect)
		
		if self.label_surface != None:
			placement_rect = self.label_surface.get_rect()
			placement_rect.center = self.rect.center
			surface.blit(self.label_surface, placement_rect)
			
class Meter(interface_classes.Drawable):
	def __init__(self, rect, identifier=None, max_value=100, start_value=50,
				bg_color=(0x00,0x00,0x00),fg_color=(0xFF,0xFF,0xFF), fill_color=(0xAA,0xAA,0xAA),
				fill_rate=0.2):
		self.max_value = max_value
		self.current_value = start_value
		self.visible_value = start_value
		self.fill_rate = fill_rate
		
		self.bg_color = bg_color
		self.fg_color = fg_color
		self.fill_color = fill_color

		interface_classes.Drawable.__init__(self, rect, identifier)
		
	def reset_for_new_rect(self):
		self.meter_area = self.rect.inflate(-4,-4)
	
	def update_by_milliseconds(self, ms):
		if self.visible_value != self.current_value:
			fraction = (float(ms)/1000.0)*float(self.fill_rate)
			max_adjust = float(fraction) * float(self.max_value)
			current_difference = (self.visible_value - self.current_value)
			if abs(current_difference) < max_adjust:
				self.visible_value = self.current_value
			else:
				if current_difference < 0:
					self.visible_value += max_adjust
				else:
					self.visible_value -= max_adjust
	
	def draw_to_surface(self, surface):
		surface.fill(self.fg_color, self.rect)
		
		surface.fill(self.bg_color, self.meter_area)
		
		fill_area = self.meter_area.copy()
		fraction = float(self.visible_value)/float(self.max_value)
		fill_width = int(float(fraction)*float(fill_area.width))
		fill_area.width = fill_width
		surface.fill(self.fill_color, fill_area)
		fill_area.left = fill_area.right-2
		fill_area.width = 2
		surface.fill(self.fg_color, fill_area)

