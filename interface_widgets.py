import pygame

import interface_classes

class Button(interface_classes.Drawable):
	def __init__(
			self, rect, identifier=None, label=None, icon=None,
			bg_color=None, fg_color=(0xFF,0xFF,0xFF), glow_color=None,
			font_name="Droid Sans", font_size="24"):
		interface_classes.Drawable.__init__(self, rect, identifier)
		
		self.bg_color = bg_color
		self.fg_color = fg_color
		self.glow_color = glow_color
		
		self.mouse_hovering = False
		
		self.icon_surface = None
		if icon != None:
			self.icon_surface = pygame.image.load(icon)
		
		self.function = None

		self.label=label
		self.font = None
		self.label_surface = None
		if self.label != None:
			self.font = pygame.font.SysFont(font_name, int(font_size))
			self.label_surface = self.font.render(str(self.label), True, self.fg_color)
	
	def on_mouse_hover(self, pos):
		self.mouse_hovering = True
	
	def on_mouse_unhover(self, pos):
		self.mouse_hovering = False
	
	def on_mouse_leftclick(self, pos):
		if self.function != None:
			self.function()
	
	def draw_to_surface(self, surface):
		if self.mouse_hovering:
			if self.glow_color != None:
				surface.fill(self.glow_color, self.rect)
		else:
			if self.glow_color != None:
				surface.fill(self.bg_color, self.rect)
		
		if self.icon_surface != None:
			placement_rect = self.icon_surface.get_rect()
			placement_rect.center = self.rect.center
			surface.blit(self.icon_surface, placement_rect)
		
		if self.label_surface != None:
			placement_rect = self.label_surface.get_rect()
			placement_rect.center = self.rect.center
			surface.blit(self.label_surface, placement_rect)
			
	
	
	
