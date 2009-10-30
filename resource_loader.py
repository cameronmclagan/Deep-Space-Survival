import pygame

local_fonts = {
	"Droid Sans":"DroidSans.ttf",
	"Alpha Echo":"alpha_echo.ttf",
	"Umbrage":"umbrage.ttf"
}

font_scale = 1.0

previously_loaded_fonts = {}

def get_font(font_name, font_size, font_bold=False, font_italic=False):
	global local_fonts, font_scale, previously_loaded_fonts
	
	font_code = "{0}_{1}_{2}_{3}".format(str(font_name), str(font_size), str(font_bold), str(font_italic))
	if font_code in previously_loaded_fonts:
		return previously_loaded_fonts[font_code]
		
	font_size = int(round(float(font_size)*float(font_scale)))

	if font_name in local_fonts:
		font = pygame.font.Font(local_fonts[font_name], font_size)
	else:
		font_found = pygame.font.match_font(font_name, font_bold, font_italic)
		if font_found:
			font = pygame.font.Font(font_found, font_size)
		else:
			default = pygame.font.get_default_font()
			font = pygame.font.Font(default, font_size)
	previously_loaded_fonts[font_code] = font
	return font

previously_loaded_images = {}
def get_image(filename):
	global previously_loaded_images
	if filename in previously_loaded_images:
		return previously_loaded_images[filename]
	
	try:
		image_surface = pygame.image.load(filename)
	except:
		font = get_font("Droid Sans", 30)
		image_surface = font.render(filename,True,(0xFF,0x33,0x33))
	
	previously_loaded_images[filename] = image_surface
	return image_surface
