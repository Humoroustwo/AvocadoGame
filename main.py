try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import time, math

current_time = time.time()*1000
last_pressed = current_time+100

#CONSTANTS
WIDTH = 1280
HEIGHT = 720
GAMESPEED = 1
#SPRITE CONSTANTS
SP_SIZE = [64, 64]
SP_CENTER = [32, 32]


#IMAGES
test_player_image = simplegui._load_local_image("sprite.png")
test_wall_image = simplegui._load_local_image("block.png")
#VARIABLES


# ----------------------------------------------------------------------------------------------------------
# BUTTON INPUT
# ----------------------------------------------------------------------------------------------------------

class Key:
    def __init__(self, key_name, action):
        self.name = key_name
        self.pressed = False
        self.inp = action

    def check_down(self, key_code):
        if key_code == simplegui.KEY_MAP[self.name]:
            self.pressed = True

    def check_up(self, key_code):
        if key_code == simplegui.KEY_MAP[self.name]:
            self.pressed = False

keys = [Key('a', "1l"),
        Key('d', "1r"),
        Key('w', "1j"),
        Key('left', "2l"),
        Key('right', "2r"),
        Key('up', "2j"),
        Key('e', "1sr"),
        Key('q', "1sl")]

def key_down(key_code):
    for k in keys:
        k.check_down(key_code)

def key_up(key_code):
    for k in keys:
        k.check_up(key_code)

# ----------------------------------------------------------------------------------------------------------
# MOUSE INPUT
# ----------------------------------------------------------------------------------------------------------

mouse_click_pos = (0,0)
mouse_click = False
def mouse_handler(position):
    global mouse_click_pos, mouse_click
    mouse_click = True
    mouse_click_pos = position

# ----------------------------------------------------------------------------------------------------------
# VECTOR CLASS
# ----------------------------------------------------------------------------------------------------------

class Vector:
    def __init__(self):
        self.x_vec = 0 #Vector, not pos
        self.y_vec = 0 #Vector, not pos

    def accelerate(self, max_speed, acc, dir):
        self.x_vec += acc*dir
        if self.x_vec > max_speed:
            self.x_vec = max_speed
        elif self.x_vec < -max_speed:
            self.x_vec = -max_speed

    def decelerate(self, acc):
        if self.x_vec < 0:
            self.x_vec += acc / 2
        elif self.x_vec > 0:
            self.x_vec += -acc / 2
        if (-acc / 3 < self.x_vec < acc / 3):
            self.x_vec = 0

# ----------------------------------------------------------------------------------------------------------
# ENTITY
# ----------------------------------------------------------------------------------------------------------

class Entity(Vector):
    def __init__(self, x, y):
        Vector.__init__(self)
        self.x = x
        self.y = y

# ----------------------------------------------------------------------------------------------------------
# PROJECTILES
# ----------------------------------------------------------------------------------------------------------

class Projectile:
    def __init__(self, tx, ty, sx, sy):
        self.x = sx
        self.y = sy
        self.speed = 1
        self.angle = self.getAngle(tx,ty,sx,sy)

    def getAngle(self, tx, ty, sx, sy):
        ang = math.atan2((sy-ty), (sx-tx))

        if (tx < sx and ty < sy) or (tx > sx and ty > sy):
            ang += math.pi

        return ang

    def draw(self, canvas):
        canvas.draw_circle((self.x,self.y), 10, 10, 'Green')

        self.y += (self.speed / math.cos(self.angle))
        self.x += (self.speed / math.sin(self.angle))

class xProjectile:
    def __init__(self, sx, sy, dir):
        self.x = sx
        self.y = sy
        self.speed = 15*dir

    def draw(self, canvas):
        canvas.draw_circle((self.x,self.y), 10, 15, 'Red')

        self.x += self.speed

# ----------------------------------------------------------------------------------------------------------
# ENEMIES
# ----------------------------------------------------------------------------------------------------------

class Soldier:

    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target



# ----------------------------------------------------------------------------------------------------------
# PLAYER
# ----------------------------------------------------------------------------------------------------------

myProjectiles = []

class Player:


    def __init__(self, player_num, x, y, width, height, acc, max_speed, max_jump, terminal_velocity):
        self.x = x
        self.y = y
        self.x_vel = 1
        self.y_vel = 0
        self.width = width
        self.height =  height
        self.max_speed = max_speed
        self.acc = acc
        self.cur_speed = 0
        self.grav = 0.2
        self.in_air = True
        self.on_ground = False
        self.max_jump = max_jump
        self.t_vel = terminal_velocity
        self.last_shot = time.time()*1000

    def draw(self, canvas): #Specific to simplegui
        global wall_array
        global test_player_image
        global myProjectiles

        canvas.draw_image(test_player_image, SP_CENTER, SP_SIZE, (self.x, self.y), SP_SIZE)

        if myProjectiles:
            for p in myProjectiles:
                p.draw(canvas)

        self.control()
        self.collision_x(wall_array)
        self.gravity()
        self.collision_y(wall_array)
        self.put_back()

    def put_back(self):
        if(self.y > HEIGHT):
            self.y = HEIGHT / 2
            self.x = WIDTH / 2


    def collision_x(self, wall_list):
        wall_x = 0
        wall_y = 0
        wall_w = 0
        for wall in wall_list:
            wall_x = wall.x
            wall_y = wall.y
            wall_w = wall.width
            if(wall_y +self.height*1.9 >= self.y >= wall_y - self.height):
                if(wall_x+wall_w > self.x+self.x_vel > wall_x-wall_w):
                    self.x_vel = 0
                    if(self.x<wall_x):
                        self.x = wall_x-wall_w-1
                    if(self.x>wall_x):
                        self.x = wall_x+wall_w+1

    def collision_y(self, wall_list):
        if(self.y_vel != 0):
            self.in_air = True

        wall_x = 0
        wall_y = 0
        wall_w = 0
        wall_h = 0
        for wall in wall_list:
            if ((wall.x + wall.width + self.width >= self.x + self.width >= wall.x - wall.width / 2)
                and (wall.y + wall.height / 2 >= self.y + self.height >= wall.y - wall.height / 2)):
                wall_x = wall.x
                wall_y = wall.y
                wall_w = wall.width
                wall.h = wall.height
                if (self.in_air):
                    self.in_air = False
                    self.on_ground = True
                    self.y_vel = 0
                    self.y = wall_y - 2 * self.height
                break

        if ((wall_x - self.width*2) < self.x < (wall_x + self.width*2)) == False:
            self.on_ground = False

        for wall in wall_list:
            wall_x = wall.x
            wall_y = wall.y
            wall_w = wall.width
            wall.h = wall.height

            if (wall_x - self.width*2 <= self.x <= wall_x + self.width*2
                and wall_y < self.y < wall_y + self.height*2.1):
                self.y_vel = 0

    def gravity(self):
        if (not self.on_ground):
            self.y_vel += self.grav
            if(self.y_vel > self.t_vel): #Terminal velocity
                self.y_vel = self.t_vel
            self.y += self.y_vel*GAMESPEED

    def accelerate(self, move):
        self.x_vel += self.acc*move
        self.collision_x(wall_array)
        if self.x_vel > self.max_speed:
            self.x_vel = self.max_speed
        elif self.x_vel < -self.max_speed:
            self.x_vel = -self.max_speed


    def decelerate(self):
        if self.x_vel < 0:
            self.x_vel += self.acc / 2
        elif self.x_vel > 0:
            self.x_vel += -self.acc / 2
        if(-self.acc/3 < self.x_vel < self.acc/3):
            self.x_vel = 0
        self.collision_x(wall_array)

    def jump(self):
        if(self.on_ground):
            self.in_air = True
            self.on_ground = False
            self.y_vel -= self.max_jump

    def shoot(self, dir):
        global myProjectiles
        myProjectiles.append(xProjectile(self.x, self.y, dir))

    def control(self): #Specific to simplegui
        last_pressed = 0
        cur = time.time()*1000
        for k in keys:
            if k.pressed:
                i = 0
                if k.inp == "1l":
                    self.accelerate(-1)
                    last_pressed = time.time() * 1000
                elif k.inp == "1r":
                    self.accelerate(1)
                    last_pressed = time.time() * 1000
                elif k.inp == "1j":
                    self.jump()
                elif k.inp == "1sr" and cur - self.last_shot > 500:
                    self.shoot(1)
                    self.last_shot = cur
                elif k.inp == "1sl" and cur - self.last_shot > 500:
                    self.shoot(-1)
                    self.last_shot = cur
            else:
                if (last_pressed + 100 < time.time() * 1000):
                    self.decelerate()

            self.x += self.x_vel*GAMESPEED
            self.y += self.y_vel*GAMESPEED

    def getX(self):
        return self.x

    def getY(self):
        return self.y

# ----------------------------------------------------------------------------------------------------------
# GENERIC WALLS
# ----------------------------------------------------------------------------------------------------------

class Wall():

    def __init__(self, x, y, width, height, sprite):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = sprite

    def draw(self, canvas): #Specific to simplegui
        canvas.draw_image(self.sprite,
                          (self.width/2, self.height/2),
                          (self.width, self.height),
                          (self.x, self.y),
                          (self.width, self.height))

# ----------------------------------------------------------------------------------------------------------
# ENTITIES
# ----------------------------------------------------------------------------------------------------------

player_one = Player(1, WIDTH/2, HEIGHT/2, 32, 32, 0.2, 1.5, 5, 6)

wall_array = []
for i in range(0, int(WIDTH/64)+1):
    wall_array.append(Wall(i*64, HEIGHT, 64, 64, test_wall_image))

for i in range(0, int(WIDTH/64)+1):
    wall_array.append(Wall(i*64, 0, 64, 64, test_wall_image))

for i in range(0, int(HEIGHT/64)+1):
    wall_array.append(Wall(0, i*64, 64, 64, test_wall_image))

for i in range(0, int(HEIGHT/64)+1):
    wall_array.append(Wall(WIDTH, i*64, 64, 64, test_wall_image))

for i in range(0, 6):
    wall_array.append(Wall(i*64, HEIGHT/2, 64, 64, test_wall_image))

for i in range(0, 6):
    wall_array.append(Wall(WIDTH-(i*64), HEIGHT/2, 64, 64, test_wall_image))


# ----------------------------------------------------------------------------------------------------------
# GAME AND GAME RULES
# ----------------------------------------------------------------------------------------------------------

class Game:

    def __init__(self):
        self.game_speed = 1

    def draw(self, canvas): #Specific to simplegui
        player_one.draw(canvas)
        for wall in wall_array:
            wall.draw(canvas)

# ----------------------------------------------------------------------------------------------------------
# MAIN DISPLAY
# ----------------------------------------------------------------------------------------------------------
#p = Projectile(0,0, WIDTH, HEIGHT)
new_game = Game()
def display(canvas):
    global mouse_click_pos, mouse_click
    if mouse_click:
        mouse_click = False
    new_game.draw(canvas)


# ----------------------------------------------------------------------------------------------------------
# SIMPLE GUI FRAME
# ----------------------------------------------------------------------------------------------------------

frame = simplegui.create_frame('tmp', WIDTH, HEIGHT)

frame.set_canvas_background('rgb(12,50,120)')
frame._display_fps_average = True
frame.set_draw_handler(display)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
frame.set_mouseclick_handler(mouse_handler)

frame.start()
