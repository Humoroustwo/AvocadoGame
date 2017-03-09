# Contains classes & methods for rendering and working with interactive objects

import os, math, pygame, spritesheet


# Vector object, with sprite
class SpriteObject:
    def __init__(self, x_coord, y_coord, x_speed, y_speed, sheet_name, number_of_sprites, sprites_per_row, sprite_width, sprite_height ):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.spritesheet = spritesheet(sheet_name, number_of_sprites, sprites_per_row, sprite_width, sprite_height)

    def __init__(self, x_coord, y_coord):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.x_speed = 0
        self.y_speed = 0


    def getdistance(self, other_object):
        return math.sqrt( math.pow(self.xcoord - other_object.xcoord, 2)*math.pow(self.ycoord - other_object.ycoord,2) )


class Entity(SpriteObject):
    def __init__(self, x_coord, y_coord, health):
        SpriteObject.__init__(self, x_coord, y_coord)
        self.health = health


class Enemy(Entity):
    def __init__(self, x_coord, y_coord):
        Entity.__init__(self, x_coord, y_coord)

class Jumper(Enemy):
    def __init__(self, x_coord, y_coord):
        print("TODO")

class Soldier(Enemy):
    def __init__(self):
        print("TODO")


class Player(Entity):
    def __init__(self, x_coord, y_coord, x_speed, y_speed):
        Entity.__init__(self, x_coord, y_coord)



#class Projectile(VectorObject):
#   def __init__(self):


#class Bullet(Projectile):
#   def __init__(self):
#        #

#class Missile(Projectile):
#    def __init__(self):
#        #
#class Bouncer(Projectile):
#    def __init__(self):
#        #
