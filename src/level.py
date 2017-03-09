import pygame, os, sprites, spritesheet



class level:
    def __init__(self, sheet_name, number_of_sprites, sprites_per_row, window_width, window_height):
        print("helloworld")

# Railroad level. Moving background (maybe with parralax background) with static train carriage foreground.
class railroad(level):
    def __init__(self, background_image_name):
        self.background = spritesheet()

# Static animated spritesheet background
class dungeon(level):
    def __init__(self):
        self.background = pygame.image.load(os.path.join('data', sheet_name))


# Debug level, solid colour background
class debug(level):
    def __init__(self, background_colour):
        self.background_colour = background_colour
    def __init__(self):
        self.background_colour = (0, 0, 0)

    def draw_level(self, surface):
        surface.fill(self.background_colour)



