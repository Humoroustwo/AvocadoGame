import pygame, os

class spritesheet:
    def __init__(self, sheet_name, number_of_sprites, sprites_per_row, sprite_width, sprite_height):
        self.sheet = pygame.image.load(os.path.join('data', sheet_name))
        self.current_sprite = 0
        self.number_of_sprites = number_of_sprites
        self.sprites_per_row = sprites_per_row
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

def rendersprite(self, surface):
    print("TODO")