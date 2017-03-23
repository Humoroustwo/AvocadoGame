try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import time
import random
import math


current_time = time.time() * 1000
last_pressed = current_time + 100

# CONSTANTS
WIDTH = 1280
HEIGHT = 720
# SPRITE CONSTANTS
SP_SIZE = [64, 64]
SP_CENTER = [32, 32]

# IMAGES
test_player_image = simplegui._load_local_image("data/images/sprite.png")
test_wall_image = simplegui._load_local_image("data/images/block.png")
player_sps = simplegui._load_local_image("data/images/character_sheet.png")
player_projectile = simplegui._load_local_image("data/images/PlayerProjectile.png")


# VARIABLES
game_speed = 1
projectile_list = []

# ----------------------------------------------------------------------------------------------------------
# SPRITE OBJECT
# ----------------------------------------------------------------------------------------------------------
#Yeah, I kinda forgot how simplegui handled sprites.
#It's easier to initially make a sprite object class and then place them into an array.

class Sprites():
    global SP_SIZE, SP_CENTER
    def __init__(self, src, pos):
        self.src = src
        self.center = [32 + (pos[0]*64), 32 + (pos[1]*64)]
        self.size = SP_SIZE

    def draw(self, canvas, pos, size):
        canvas.draw_image(self.src, self.center, self.size, pos, size)


# ----------------------------------------------------------------------------------------------------------
# SPRITES
# ----------------------------------------------------------------------------------------------------------
#Initialising sprites
player_one_sp = []
for i in range(0, 2):
    for j in range(0, 5):
        player_one_sp.append(Sprites(player_sps, (j, i)))
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
        global last_key_up
        last_key_up = time.time()
        if key_code == simplegui.KEY_MAP[self.name]:
            self.pressed = False



keys = [Key('a', "1l"),
        Key('d', "1r"),
        Key('w', "1j"),
        Key('g', "1s")]

last_key_press = 0.0


def key_down(key_code):
    for k in keys:
        k.check_down(key_code)


def key_up(key_code):
    global last_keyup
    last_keyup = time.time()

    for k in keys:
        k.check_up(key_code)


def is_key_pressed():
    for k in keys:
        if k.pressed:
            global last_key_pressed
            last_key_pressed = time.time()
            return True
    return False



# ----------------------------------------------------------------------------------------------------------
# MOUSE INPUT
# ----------------------------------------------------------------------------------------------------------

mouse_click_pos = (0, 0)
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
        self.x_vec = 0  # Vector, not pos
        self.y_vec = 0  # Vector, not pos

    def accelerate(self, max_speed, acc, dir):
        self.x_vec += acc * dir
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


class Jumper(Entity):
    def __init__(self):
        self.todo = 0


class Shooter(Entity):
    def __init__(self):
        self.todo = 0


class Soldier(Entity):
    def __init__(self):
        self.todo = 0

# ----------------------------------------------------------------------------------------------------------
# PROJECTILES
# ----------------------------------------------------------------------------------------------------------

class Projectile:
    def __init__(self, tx, ty, sx, sy):
        self.x = sx
        self.y = sy
        self.speed = 1
        self.angle = self.getAngle(tx, ty, sx, sy)

    def getAngle(self, tx, ty, sx, sy):
        ang = math.atan2((sy - ty), (sx - tx))

        if (tx < sx and ty < sy) or (tx > sx and ty > sy):
            ang += math.pi

        return ang

    def draw(self, canvas):
        canvas.draw_circle((self.x, self.y), 10, 10, 'Green')

        self.y += (self.speed / math.cos(self.angle))
        self.x += (self.speed / math.sin(self.angle))

class xProjectile:
    def __init__(self, sx, sy, dir):
        self.x = sx
        self.y = sy
        self.speed = 15 * dir

    def draw(self, canvas):
        #canvas.draw_circle((self.x, self.y), 10, 15, 'Red')
        canvas.draw_image(player_projectile, (259, 101), (518,202), (self.x, self.y), (32,32))
        self.x += self.speed

    def getX(self):
        return self.x

    def getY(self):
        return self.y


# ----------------------------------------------------------------------------------------------------------
# PLAYER
# ----------------------------------------------------------------------------------------------------------

class Player:
    def __init__(self, player_num, x, y, width, height, acc, max_speed, max_jump, terminal_velocity, health):
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
        self.health = health
        self.time_last_hurt = 0
        self.facing_dir = "right"

        self.last_frame_time = time.time() * 1000
        self.sps_pos = [0, 0]
        self.last_shot = time.time() * 1000
        self.counter = 0

    def draw(self, canvas): #Specific to simplegui
        global wall_array, test_player_image, enemy_list, player_one_sp
        canvas.draw_image(test_player_image, SP_CENTER, SP_SIZE, (self.x, self.y), SP_SIZE)
        self.sprite_handler(canvas)
        self.control()
        self.touch_enemy(enemy_list)
        self.collision_x(wall_array)
        self.gravity()
        self.collision_y(wall_array)
        self.put_back()

    def sprite_handler(self, canvas):
        if(self.on_ground):
            if(self.x_vel > 0):
                if(self.last_frame_time + 100 < time.time() * 1000):
                    self.last_frame_time = time.time() * 1000
                    self.sps_pos[0] += 1
                    self.sps_pos[1] = 0
            if(self.x_vel < 0):
                if(self.last_frame_time + 100 < time.time() * 1000):
                    self.last_frame_time = time.time() * 1000
                    self.sps_pos[0] += 1
                    self.sps_pos[1] = 1
            if(self.x_vel == 0):
                if(self.facing_dir == "left"):
                    self.sps_pos[0] = 0
                    self.sps_pos[1] = 1
                if(self.facing_dir == "right"):
                    self.sps_pos[0] = 0
                    self.sps_pos[1] = 0

            if (self.sps_pos[0] > 3):
                self.sps_pos[0] = 0
        else:
            self.sps_pos[0] = 4
            if(self.facing_dir == "left"):
                self.sps_pos[1] = 1
            if(self.facing_dir == "right"):
                self.sps_pos[1] = 0

        sp_array_pos = (self.sps_pos[0])+(self.sps_pos[1]*5)
        player_one_sp[sp_array_pos].draw(canvas, (self.x, self.y), (64, 64))

    def put_back(self):
        if(self.y > HEIGHT):
            self.y = HEIGHT / 2
            self.x = WIDTH / 2

    def shoot(self):
        global projectile_list
        if(self.facing_dir == "left"):
            projectile_list.append(xProjectile(self.x, self.y, -1))
        if(self.facing_dir == "right"):
            projectile_list.append(xProjectile(self.x, self.y, 1))

    def touch_enemy(self, enemy_list):
        for enemies in enemy_list:
            if(self.time_last_hurt + 2000 < time.time()*1000):
                if(enemies.x-self.width < self.x < enemies.x+self.width and
                    enemies.y-self.height < self.y < enemies.y+self.height):
                    self.time_last_hurt = time.time() * 1000
                    self.health -= 1
                    self.knockback(enemies)
                    print(self.health)

    def knockback(self, target):
        knock_x = 0
        if(self.x - target.x < 0):
            knock_x = -1
        else:
            knock_x = 1
        self.x_vel = knock_x * (self.max_speed*4)
        self.in_air = True
        self.on_ground = False
        self.y_vel = -self.max_jump/2

    def collision_x(self, wall_list):
        wall_x = 0
        wall_y = 0
        wall_w = 0
        for wall in wall_list:
            wall_x = wall.x
            wall_y = wall.y
            wall_w = wall.width
            if(wall_y + self.height >= self.y >= wall_y - self.height*1.4):
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
                and wall_y < self.y < wall_y + self.height*2):
                self.y = wall_y + self.height*2
                self.y_vel = 0

    def gravity(self):
        if (not self.on_ground):
            self.y_vel += self.grav
            if(self.y_vel > self.t_vel): #Terminal velocity
                self.y_vel = self.t_vel
            self.y += self.y_vel*game_speed

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

    ###
    ###
    def key_detection(self):
        for k in keys:
            if k.pressed:
                return k.inp

    def control_tmp(self):
        last_pressed = 0
        if(self.key_detection() == "1l"):
            self.accelerate(-1)
            self.facing_dir = "left"
            last_pressed = time.time() * 1000
        elif(self.key_detection() == "1r"):
            self.accelerate(1)
            self.facing_dir = "right"
            last_pressed = time.time() * 1000
        elif(self.key_detection() == "1j"):
            self.jump()
        else:
            if(last_pressed + 100 < time.time()*1000):
                self.decelerate()

        self.x += self.x_vel * game_speed
        self.y += self.y_vel * game_speed
    ###
    ###

    def control(self): #Specific to simplegui
        last_pressed = 0
        for k in keys:
            if k.pressed:
                if k.inp == "1l":
                    self.accelerate(-1)
                    self.facing_dir = "left"
                    last_pressed = time.time() * 1000
                elif k.inp == "1r":
                    self.accelerate(1)
                    self.facing_dir = "right"
                    last_pressed = time.time() * 1000
                elif k.inp == "1j":
                    self.jump()
                elif k.inp == "1s":
                    if(self.last_shot + 500 < time.time()*1000):
                        self.last_shot = time.time() * 1000
                        self.shoot()

            else:
                if (last_pressed + 100 < time.time() * 1000):
                    self.decelerate()

            self.x += self.x_vel*game_speed
            self.y += self.y_vel*game_speed

# ----------------------------------------------------------------------------------------------------------
# ENEMIES
# ----------------------------------------------------------------------------------------------------------
#TEMPORARY UNTIL A PROPER ENEMY CLASS IS MADE

class Enemy:
    def __init__(self, x, y, width, height, acc, max_speed, max_jump):
        self.x = x
        self.y = y
        self.x_vel = 4
        self.y_vel = 0
        self.set_speed = 4
        self.width = width
        self.height =  height
        self.max_speed = max_speed
        self.acc = acc
        self.cur_speed = 0
        self.grav = 0.2
        self.in_air = True
        self.on_ground = False
        self.max_jump = max_jump
        self.time_last_col = 0

    def basic_ai(self):
        if(self.x_vel == 0):
            if(self.time_last_col + 1000 < time.time()*1000):
                self.time_last_col = time.time()*1000
                self.set_speed = -self.set_speed
                self.x_vel = self.set_speed*game_speed
        self.x += self.x_vel

    def collision_x(self, wall_list):
        wall_x = 0
        wall_y = 0
        wall_w = 0
        for wall in wall_list:
            wall_x = wall.x
            wall_y = wall.y
            wall_w = wall.width
            if(wall_y +self.height*1.9 >= self.y >= wall_y - self.height*1.2):
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
            wall.h = wall.height

            if (wall_x - self.width*2 <= self.x <= wall_x + self.width*2
                and wall_y < self.y < wall_y + self.height*2.01):
                self.y_vel = 0

    def gravity(self):
        if (not self.on_ground):
            self.y_vel += self.grav
            self.y += self.y_vel*game_speed

    def draw(self, canvas):
        global wall_array
        global test_player_image
        canvas.draw_image(test_wall_image, SP_CENTER, SP_SIZE, (self.x, self.y), SP_SIZE)
        self.gravity()
        self.basic_ai()
        self.collision_x(wall_array)
        self.collision_y(wall_array)


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

    def draw(self, canvas):  # Specific to simplegui
        canvas.draw_image(self.sprite,
                          (self.width / 2, self.height / 2),
                          (self.width, self.height),
                          (self.x, self.y),
                          (self.width, self.height))





# ----------------------------------------------------------------------------------------------------------
# GAME AND GAME RULES
# ----------------------------------------------------------------------------------------------------------

class Game:
    def __init__(self, levels):
        self.game_speed = 1
        self.current_level_index = 0
        self.levels = levels
        self.score = 0
        self.enemy_array = []

    def draw(self, canvas):  # Specific to simplegui

        canvas.draw_image(self.levels[self.current_level_index].background, (320, 180), (640,360), (640, 360), (1280,720))

        player_one.draw(canvas)
        for enemy in self.enemy_array:
            enemy.draw()

        for wall in self.levels[self.current_level_index].wall_array:
            wall.draw(canvas)

        if len(self.enemy_array) == 0 and len(self.levels[self.current_level_index].enemy_queue) == 0:
            # Display game over and score
            canvas.draw_text("Level complete!", (WIDTH/2, HEIGHT/2), 50, "white")
            canvas.draw_text("Score: " + str(self.score), (WIDTH / 2, (HEIGHT / 2) + 100), 50, "white")

            if is_key_pressed():
                if (self.current_level_index + 1) == len(self.levels):
                    print("game shouldchange")
                    global current_draw_handler
                    current_draw_handler = draw_game_complete_screen


# ----------------------------------------------------------------------------------------------------------
# Level
# ----------------------------------------------------------------------------------------------------------


class Level:
    def __init__(self, level_file_path):
        # Level Metadata
        self.raw_data = open("data/levels/" + level_file_path).read().splitlines()
        self.level_name = self.get_level_file_field("name")

        # Loading textures
        self.background = simplegui._load_local_image(self.get_level_file_field("background_image"))
        self.wall_texture = simplegui._load_local_image(self.get_level_file_field("wall_image"))
        self.wall_array = self.generate_wall_array()

        # Enemy variable
        self.min_enemy_count = int(self.get_level_file_field("min_enemies"))
        self.max_enemy_count = int(self.get_level_file_field("max_enemies"))
        self.min_time_between_spawn = int(self.get_level_file_field("min_time_between_spawn"))
        self.max_time_between_spawn = int(self.get_level_file_field("max_time_between_spawn"))

        # Generating enemy queue
        self.proportion_shooters = float(self.get_level_file_field("proportion_shooters"))
        self.proportion_bouncers = float(self.get_level_file_field("proportion_bouncers"))
        self.proportion_soldiers = float(self.get_level_file_field("proportion_soldiers"))
        self.enemy_queue = self.generate_enemies_queue()

    # Get all data from line with (argument) string name
    def get_level_file_field(self, field_name):
        for i in self.raw_data:
            line = i.split(":")
            if line[0] == field_name:
                return line[1]
        print ("Warning: Field \"" + field_name + "\" not found!")

    def generate_wall_array(self):
        walls = str.split(self.get_level_file_field("walls"), "|")
        wall_output = []
        for wall in walls:
            wall_params = str.split(wall, ",")
            wall_output.append(Wall(int(wall_params[0]), int(wall_params[1]), int(wall_params[2]), int(wall_params[3]), self.wall_texture))

        for i in range(0, int(WIDTH / 64) + 1):
            wall_output.append(Wall(i * 64, HEIGHT, 64, 64, self.wall_texture))
        for i in range(0, int(WIDTH / 64) + 1):
            wall_output.append(Wall(i * 64, 0, 64, 64, self.wall_texture))
        for i in range(0, int(HEIGHT / 64) + 1):
            wall_output.append(Wall(0, i * 64, 64, 64, self.wall_texture))
        for i in range(0, int(HEIGHT / 64) + 1):
            wall_output.append(Wall(WIDTH, i * 64, 64, 64, self.wall_texture))
        return wall_output

    def generate_enemies_queue(self):
        random.seed()
        enemy_count = math.ceil((self.max_enemy_count - self.min_enemy_count)) + self.min_enemy_count

        enemies = []
        # Filling list initially (for each enemy type)
        for _ in range(int(round(self.proportion_shooters * enemy_count))):
            enemies.append(Shooter())
        for _ in range(int(round(self.proportion_shooters * enemy_count))):
            enemies.append(Jumper())
        for _ in range(int(round(self.proportion_shooters * enemy_count))):
            enemies.append(Soldier())

        # Randomising List
        for x in enemies:
            j = int(round(random.random() * (len(enemies) - 1)))
            swap = x
            x = enemies[j]
            enemies[j] = swap
        return enemies


# ----------------------------------------------------------------------------------------------------------
# ENTITY DEFINITIONS
# ----------------------------------------------------------------------------------------------------------

player_one = Player(1, WIDTH / 2, HEIGHT / 2, 32, 32, 0.2, 1.5, 5, 3.5, 2)
current_level = Level("test.lvl")
wall_array = current_level.generate_wall_array()
enemy_list = []

# --------------------------------
# GAME DEFINITIONS
# --------------------------------


levels = []
levels.append(Level("outside.lvl"))
levels.append(Level("inside.lvl"))
levels.append(Level("room.lvl"))

game = Game(levels)

# ----------------------------------------------------------------------------------------------------------
# MAIN DISPLAY
# ----------------------------------------------------------------------------------------------------------


def game_renderer(canvas):
    game.draw(canvas)


def draw_splash_screen(canvas):
    global current_draw_handler
    canvas.draw_text("Welcome to AvocadoGame!", (WIDTH / 2, HEIGHT / 2), 50, "white")
    if is_key_pressed():
        current_draw_handler = game_renderer
        print("splash shouldchange")


def draw_game_over_screen(canvas):
    global current_draw_handler

    canvas.draw_text("You died! :(", (WIDTH / 2, HEIGHT / 2), 50, "white")
    #if is_key_pressed():
    #    current_draw_handler = draw_splash_screen


def draw_game_complete_screen(canvas):
    global current_draw_handler
    canvas.draw_text("Game complete!", (WIDTH / 2, HEIGHT / 2), 50, "white")
   # if is_key_pressed():
   #     current_draw_handler = draw_splash_screen


current_draw_handler = draw_splash_screen


def display(canvas):
    global current_draw_handler
    current_draw_handler(canvas)
    for projectile in projectile_list:
        projectile.draw(canvas)
        if(projectile.x < 0):
            projectile_list.remove(projectile)
        if(projectile.x > WIDTH):
            projectile_list.remove(projectile)

    print(len(projectile_list))




# ----------------------------------------------------------------------------------------------------------
# SIMPLE GUI FRAME
# ----------------------------------------------------------------------------------------------------------


frame = simplegui.create_frame('Avocado Game', WIDTH, HEIGHT)
frame.set_canvas_background('rgb(12,50,120)')
frame._display_fps_average = True
frame.set_draw_handler(display)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
frame.set_mouseclick_handler(mouse_handler)
frame.start()



