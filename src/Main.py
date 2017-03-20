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
GAMESPEED = 1
# SPRITE CONSTANTS
SP_SIZE = [64, 64]
SP_CENTER = [32, 32]

# IMAGES
test_player_image = simplegui._load_local_image("data/images/sprite.png")
test_wall_image = simplegui._load_local_image("data/images/block.png")


# VARIABLES


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
        Key('up', "2j")]


def key_down(key_code):
    for k in keys:
        k.check_down(key_code)


def key_up(key_code):
    for k in keys:
        k.check_up(key_code)


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
# PLAYER
# ----------------------------------------------------------------------------------------------------------

class Player:
    def __init__(self, player_num, x, y, width, height, acc, max_speed, max_jump, terminal_velocity):
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.width = width
        self.height = height
        self.max_speed = max_speed
        self.acc = acc
        self.cur_speed = 0
        self.grav = 0.2
        self.in_air = True
        self.on_ground = False
        self.max_jump = max_jump
        self.t_vel = terminal_velocity

    def draw(self, canvas):  # Specific to simplegui
        global wall_array
        global test_player_image
        canvas.draw_image(test_player_image, SP_CENTER, SP_SIZE, (self.x, self.y), SP_SIZE)
        self.control()
        self.collision_x(wall_array)
        self.gravity()
        self.collision_y(wall_array)
        self.put_back()

    def put_back(self):
        if (self.y > HEIGHT):
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
            if (wall_y + self.height * 1.9 >= self.y >= wall_y - self.height):
                if (wall_x + wall_w > self.x + self.x_vel > wall_x - wall_w):
                    self.x_vel = 0
                    if (self.x < wall_x):
                        self.x = wall_x - wall_w - 1
                    if (self.x > wall_x):
                        self.x = wall_x + wall_w + 1

    def collision_y(self, wall_list):
        if (self.y_vel != 0):
            self.in_air = True

        wall_x = 0
        wall_y = 0
        wall_w = 0
        wall_h = 0
        for wall in wall_list:
            if ((wall.x + wall.width + self.width >= self.x + self.width >= wall.x - wall.width / 2) and (wall.y + wall.height / 2 >= self.y + self.height >= wall.y - wall.height / 2)):
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

        if ((wall_x - self.width * 2) < self.x < (wall_x + self.width * 2)) == False:
            self.on_ground = False

        for wall in wall_list:
            wall_x = wall.x
            wall_y = wall.y
            wall_w = wall.width
            wall.h = wall.height

            if (wall_x - self.width * 2 <= self.x <= wall_x + self.width * 2
                and wall_y < self.y < wall_y + self.height * 2.1):
                self.y_vel = 0

    def gravity(self):
        if (not self.on_ground):
            self.y_vel += self.grav
            if (self.y_vel > self.t_vel):  # Terminal velocity
                self.y_vel = self.t_vel
            self.y += self.y_vel * GAMESPEED

    def accelerate(self, move):
        self.x_vel += self.acc * move
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
        if (-self.acc / 3 < self.x_vel < self.acc / 3):
            self.x_vel = 0
        self.collision_x(wall_array)

    def jump(self):
        if (self.on_ground):
            self.in_air = True
            self.on_ground = False
            self.y_vel -= self.max_jump

    def control(self):  # Specific to simplegui
        last_pressed = 0
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
            else:
                if (last_pressed + 100 < time.time() * 1000):
                    self.decelerate()

            self.x += self.x_vel * GAMESPEED
            self.y += self.y_vel * GAMESPEED


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
    def __init__(self):
        self.game_speed = 1



    def draw(self, canvas):  # Specific to simplegui
        player_one.draw(canvas)
        for enemy in enemy_array:
            enemy.draw()

        for wall in wall_array:
            wall.draw(canvas)


# ----------------------------------------------------------------------------------------------------------
# Level
# ----------------------------------------------------------------------------------------------------------


class Level:
    def __init__(self, level_file_path, wall_image_file_path):

        # Level Metadata
        self.raw_data = open("data/levels/" + level_file_path).readlines()
        self.level_name = self.get_level_file_field("name")
        # Loading textures
        self.background = simplegui.load_image(self.get_level_file_field("background_image"))


        #path = self.get_level_file_field("wall_image")    BUG PREVENTS THIS WORKING!
        self.wall_texture = simplegui._load_local_image(wall_image_file_path)





        # Enemy variable
        self.min_enemy_count = int(self.get_level_file_field("min_enemies"))
        self.max_enemy_count = int(self.get_level_file_field("max_enemies"))
        self.min_time_between_spawn = int(self.get_level_file_field("min_time_between_spawn"))
        self.max_time_between_spawn = int(self.get_level_file_field("max_time_between_spawn"))

        # Generating enemy queue
        self.proportion_shooters = float(self.get_level_file_field("proportion_shooters"))
        self.proportion_bouncers = float(self.get_level_file_field("proportion_bouncers"))
        self.proportion_soldiers = float(self.get_level_file_field("proportion_soldiers"))
        self.enemy_queue = None
        self.generate_enemies_queue()

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
            wall_output.append(Wall(i * 64, HEIGHT, 64, 64, test_wall_image))
        for i in range(0, int(WIDTH / 64) + 1):
            wall_output.append(Wall(i * 64, 0, 64, 64, test_wall_image))
        for i in range(0, int(HEIGHT / 64) + 1):
            wall_output.append(Wall(0, i * 64, 64, 64, test_wall_image))
        for i in range(0, int(HEIGHT / 64) + 1):
            wall_output.append(Wall(WIDTH, i * 64, 64, 64, test_wall_image))
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
            x = swap
        return enemies


# ----------------------------------------------------------------------------------------------------------
# MAIN DISPLAY
# ----------------------------------------------------------------------------------------------------------
new_game = Game()


def display(canvas):
    new_game.draw(canvas)


# ----------------------------------------------------------------------------------------------------------
# ENTITIES
# ----------------------------------------------------------------------------------------------------------

player_one = Player(1, WIDTH / 2, HEIGHT / 2, 32, 32, 0.2, 1.5, 5, 6)
current_level = Level("test.lvl", "data/images/block.png")
wall_array = current_level.generate_wall_array()
enemy_array = []

enemy_queue = []

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
