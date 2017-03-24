try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import time, math, random

current_time = time.time()*1000
last_pressed = current_time+100

#CONSTANTS
WIDTH = 1280
HEIGHT = 720

#SPRITE CONSTANTS
SP_SIZE = [64, 64]
SP_CENTER = [32, 32]
CHARSIZE = [64, 96]
CHARCENTER = [32, 48]
CHARDIM = [16, 10]


#IMAGES
test_player_image = simplegui._load_local_image("data/images/sprite.png")
test_wall_image = simplegui._load_local_image("data/images/block.png")
player_sps = simplegui._load_local_image("data/images/character_sheet.png")
player_projectile = simplegui._load_local_image("data/images/PlayerProjectile.png")
char = simplegui._load_local_image("data/images/alpha.png")

#VARIABLES
game_speed = 1

# ----------------------------------------------------------------------------------------------------------
# Character class
# ----------------------------------------------------------------------------------------------------------

class Character:
    global WIDTH, HEIGHT, CHARSIZE, CHARCENTER, CHARDIM, char

    def __init__(self, pos):
        self.charSize = CHARSIZE
        self.charCenter = [(CHARSIZE[0] * (pos[0] + 1) - CHARCENTER[0]), (CHARSIZE[1] * (pos[1] + 1) - CHARCENTER[1])]
        self.charDim = CHARDIM

    def drawChar(self, canvas, pos, size):
        canvas.draw_image(char, self.charCenter, self.charSize, pos, size)


# ----------------------------------------------------------------------------------------------------------
# Display string method
# ----------------------------------------------------------------------------------------------------------


def display_string(canvas, strn, pos, size):
    strList = list(strn)
    offset = size[0]/2
    for j in range(0, len(strList)):
        charPos = ord(strList[j]) - 65
        if charPos > 25:
            print(strn + ' is not a valid string, it must be all in capitals')
        elif -18 < charPos < -7:
            numsShad[charPos+17].drawChar(canvas, ((((-len(strList)*0.9*size[0])/2) + j*0.9*size[0] + pos[0] + offset+(size[0]/15)), pos[1]+(size[1]/15)), (size[0]*0.75,size[1]*0.75))
            nums[charPos+17].drawChar(canvas, ((((-len(strList)*0.9*size[0])/2) + j*0.9*size[0] + pos[0]+ offset), pos[1]), (size[0]*0.75, size[1]*0.75))
        elif charPos == -33:
            pass
        else:
            abcShad[charPos].drawChar(canvas,((((-len(strList)*0.9*size[0])/2) + j*0.9*size[0] + pos[0] + offset+(size[0]/15)), pos[1]+(size[1]/15)), size)
            abc[charPos].drawChar(canvas, ((((-len(strList)*0.9*size[0])/2) + j*0.9*size[0] + pos[0] + offset), pos[1]), size)


# Characters
nums = [Character((9, 0))]
numsShad = [Character((9, 1))]
for i in range(0, 10):
    nums.append(Character((i, 0)))
    numsShad.append(Character((i, 1)))

abc = []
abcShad = []
for i in range(0, 16):
    abc.append(Character((i, 2)))
    abcShad.append(Character((i, 4)))
for i in range(0, 10):
    abc.append(Character((i, 3)))
    abcShad.append(Character((i, 5)))

# ----------------------------------------------------------------------------------------------------------
# Display remaining enemies
# ----------------------------------------------------------------------------------------------------------
def display_renemies(canvas):
    display_string(canvas, 'REMAINING ENEMIES', (WIDTH / 2, 2 * HEIGHT / 5),
                  (300 * CHARSIZE[0] / HEIGHT, 300 * CHARSIZE[1] / HEIGHT))
    if global_enemy_counter > 9:
        numsShad[int(global_enemy_counter/10)].drawChar(canvas, (WIDTH/2-22, HEIGHT/2+10), CHARSIZE)
        nums[int(global_enemy_counter/10)].drawChar(canvas, (WIDTH/2-32, HEIGHT/2), CHARSIZE)
        numsShad[global_enemy_counter - (int(global_enemy_counter/10))*10].drawChar(canvas, (WIDTH/2+42, HEIGHT/2+10), CHARSIZE)
        nums[global_enemy_counter - (int(global_enemy_counter/10))*10].drawChar(canvas, (WIDTH/2+32, HEIGHT/2), CHARSIZE)
    else:
        numsShad[global_enemy_counter].drawChar(canvas, (WIDTH/2+10, HEIGHT/2+10), CHARSIZE)
        nums[global_enemy_counter].drawChar(canvas, (WIDTH/2, HEIGHT/2), CHARSIZE)

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
        if key_code == simplegui.KEY_MAP[self.name]:
            self.pressed = False

keys = [Key('a', "1l"),#Player 1 keys
        Key('d', "1r"),
        Key('w', "1j"),
        Key('g', "1s")]

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
last_click = 0
def mouse_handler(position):
    global mouse_click_pos, mouse_click, last_click
    if(last_click + 100 < time.time()*1000):
        last_click = time.time()*1000
        mouse_click = True
        mouse_click_pos = position

# ----------------------------------------------------------------------------------------------------------
# VECTOR CLASS
# ----------------------------------------------------------------------------------------------------------

class Vector:
    def __init__(self, acc, max_speed):
        self.x_vel = 0 #Vector, not pos
        self.y_vel = 0 #Vector, not pos
        self.acc = acc
        self.max_speed = max_speed

    def accelerate(self, dir):
        self.x_vel += self.acc*dir
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


# ----------------------------------------------------------------------------------------------------------
# ENTITY
# ----------------------------------------------------------------------------------------------------------

class Entity(Vector):
    def __init__(self, x, y, width, height, acc, max_speed):
        Vector.__init__(self, acc, max_speed)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

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

    def draw(self, canvas): #Specific to simplegui
        global wall_array, test_player_image, enemy_list
        canvas.draw_image(test_player_image, SP_CENTER, SP_SIZE, (self.x, self.y), SP_SIZE)
        self.control()
        self.sprite_handler(canvas)
        self.touch_enemy(enemy_list)
        self.collision_x(wall_array)
        self.gravity()
        self.collision_y(wall_array)
        self.put_back()


    def put_back(self):
        if(self.y > HEIGHT+2*self.height):
            self.y = -128
            self.x = WIDTH / 2
            self.x_vel = 1
        if(self.y < -self.height):
            if(self.y_vel < 0):
                self.y = HEIGHT + self.height
                self.x = WIDTH / 2

    def shoot(self):
        global player_projectile_list
        if(self.facing_dir == "left"):
            player_projectile_list.append(Player_Projectiles(self.x - self.width, self.y+self.height*0.3, -1))
        if(self.facing_dir == "right"):
            player_projectile_list.append(Player_Projectiles(self.x + self.width, self.y+self.height*0.3, 1))

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
            if(wall_y + self.height >= self.y >= wall_y - self.height):
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

    def put_back(self):
        if(self.y > HEIGHT+2*self.height):
            self.y = -128
            self.x = WIDTH / 2
        if(self.y < -self.height):
            if(self.y_vel < 0):
                self.y = HEIGHT + self.height
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

    def death(self):
        global player_projectile_list, enemy_list, global_enemy_counter
        for p_proj in player_projectile_list:
            if(self.x-self.width < p_proj.x < self.x+self.width and
                self.y - self.height < p_proj.y < self.y + self.height):
                player_projectile_list.remove(p_proj)
                enemy_list.remove(self)
                global_enemy_counter += -1

    def draw(self, canvas):
        global wall_array
        global test_player_image
        canvas.draw_image(test_wall_image, SP_CENTER, SP_SIZE, (self.x, self.y), SP_SIZE)
        self.gravity()
        self.basic_ai()
        self.put_back()
        self.death()
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

    def draw(self, canvas): #Specific to simplegui
        canvas.draw_image(self.sprite,
                          (self.width/2, self.height/2),
                          (self.width, self.height),
                          (self.x, self.y),
                          (self.width, self.height))

# ----------------------------------------------------------------------------------------------------------
# PROJECTILES
# ----------------------------------------------------------------------------------------------------------

class Enemy_Projectile:
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

        self.y += (self.speed / math.cos(self.angle))*game_speed
        self.x += (self.speed / math.sin(self.angle))*game_speed

class Player_Projectiles:
    def __init__(self, sx, sy, dir):
        self.x = sx
        self.y = sy
        self.speed = 15 * dir

    def draw(self, canvas):
        #canvas.draw_circle((self.x, self.y), 10, 15, 'Red')
        canvas.draw_image(player_projectile, (259, 101), (518,202), (self.x, self.y), (32,16))
        self.death()
        self.x += self.speed*game_speed

    def death(self):
        global player_projectile_list
        if(self.x < -32 or self.x > WIDTH+32):
            player_projectile_list.remove(self)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

# ----------------------------------------------------------------------------------------------------------
# ENTITIES
# ----------------------------------------------------------------------------------------------------------

player_list = []
player_list.append(Player(1, WIDTH/2, HEIGHT/2, 32, 32, 0.2, 1.5, 5, 3.5, 3))

enemy_list = []
enemy_list.append(Enemy(WIDTH/2, 64, 32, 32, 0.2, 1.6, 10))


player_projectile_list = []

wall_array = []
for i in range(0, int((WIDTH/64)*0.4)):
    wall_array.append(Wall(i*64, HEIGHT, 64, 64, test_wall_image))
    wall_array.append(Wall(WIDTH - (i * 64), HEIGHT, 64, 64, test_wall_image))
    wall_array.append(Wall(i * 64, 0, 64, 64, test_wall_image))
    wall_array.append(Wall(WIDTH-(i*64), 0, 64, 64, test_wall_image))

for i in range(0, 7):
    wall_array.append(Wall(448+(i*64), HEIGHT/4, 64, 64, test_wall_image))
    wall_array.append(Wall(448+(i*64), (3*HEIGHT)/ 4, 64, 64, test_wall_image))

for i in range(0, int(HEIGHT/64)+1):
    wall_array.append(Wall(WIDTH, i*64, 64, 64, test_wall_image))
    wall_array.append(Wall(0, i*64, 64, 64, test_wall_image))

for i in range(0, 6):
    wall_array.append(Wall(i*64, HEIGHT/2, 64, 64, test_wall_image))
    wall_array.append(Wall(WIDTH - (i * 64), HEIGHT / 2, 64, 64, test_wall_image))


# ----------------------------------------------------------------------------------------------------------
# Button class
# ----------------------------------------------------------------------------------------------------------

class Btn:
    def __init__(self, btStr, pos, size, state):
        self.game_state = state
        self.hide = False
        self.initPos = pos
        self.pos = pos
        self.str = btStr
        self.size = size
        self.clicked = False

    def draw(self, canvas):
        global CHARSIZE
        topLeft = (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2)
        topRight = (self.pos[0] + self.size[0] / 2, self.pos[1] - self.size[1] / 2)
        botLeft = (self.pos[0] - self.size[0] / 2, self.pos[1] + self.size[1] / 2)
        botRight = (self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2)
        btnPos = (topLeft, topRight, botRight, botLeft)
        fit = (self.size[0]/CHARSIZE[0], self.size[1]/CHARSIZE[1])
        charScale = ((fit[0]/len(self.str))*CHARSIZE[0],((fit[0]/len(self.str))*CHARSIZE[1]))
        canvas.draw_polygon(btnPos, 4, 'White')
        display_string(canvas, self.str, self.pos, charScale)
        self.detectClick()

    def detectClick(self):
        global mouse_click_pos, mouse_click, game_state
        if mouse_click:
            right = self.pos[0] + self.size[0]/2
            left = self.pos[0] - self.size[0] / 2
            top = self.pos[1] - self.size[1] / 2
            bot = self.pos[1] + self.size[1] / 2
            if left < mouse_click_pos[0] < right and top < mouse_click_pos[1] < bot:
                mouseClick = False
                game_state = self.game_state



# ----------------------------------------------------------------------------------------------------------
# GAME AND GAME RULES
# ----------------------------------------------------------------------------------------------------------

game_state = "start"
global_enemy_counter = 10

class Game:
    def __init__(self):
        self.btn_start = Btn('  START  ', (WIDTH / 2, 8*HEIGHT / 16), (WIDTH / 4, HEIGHT / 10), "game")
        self.btn_difficulty = Btn('DIFFICULTY', (WIDTH / 2, 11*HEIGHT / 16), (WIDTH / 4, HEIGHT / 10), "difficulty")
        self.btn_easy = Btn('   EASY   ', (WIDTH / 2, 6 * HEIGHT / 16), (WIDTH / 4, HEIGHT / 10), "easy")
        self.btn_med = Btn('  MEDIUM  ', (WIDTH / 2, 9 * HEIGHT / 16), (WIDTH / 4, HEIGHT / 10), "med")
        self.btn_hard = Btn('   HARD   ', (WIDTH / 2, 12 * HEIGHT / 16), (WIDTH / 4, HEIGHT / 10), "hard")
        self.enemy_counter = 0
        self.spawn_frequency = 0

    def start_screen(self, canvas):
        global enemy_list, global_enemy_counter
        display_string(canvas, "AVACADO GAME", (WIDTH/2, HEIGHT/4), CHARSIZE)
        self.btn_start.draw(canvas)
        self.btn_difficulty.draw(canvas)
        enemy_list[:] = []

    def difficulty(self, canvas):
        display_string(canvas, "DIFFUCULTY SETTINGS", (WIDTH / 2, HEIGHT / 6), CHARSIZE)
        self.btn_easy.draw(canvas)
        self.btn_med.draw(canvas)
        self.btn_hard.draw(canvas)

    def easy(self):
        global global_enemy_counter, game_state
        global_enemy_counter = 10
        self.enemy_counter = 10
        self.spawn_frequency = 6
        game_state = "start"

    def med(self):
        global global_enemy_counter, game_state
        global_enemy_counter = 20
        self.enemy_counter = 20
        self.spawn_frequency = 4
        game_state = "start"

    def hard(self):
        global global_enemy_counter, game_state
        global_enemy_counter = 30
        self.enemy_counter = 30
        self.spawn_frequency = 2
        game_state = "start"


    def game(self, canvas):
        global player_list, wall_array, enemy_list
        for players in player_list:
            players.draw(canvas)
        for wall in wall_array:
            wall.draw(canvas)
        random_delay = time.time()*1000 + random.randint(0,0)
        if(random_delay < time.time()*1000):
            if(self.enemy_counter > 0):
                self.enemy_counter += -1
                enemy_list.append(Enemy(WIDTH / 2, 64, 32, 32, 0.2, 1.6, 10))
        for enemy in enemy_list:
            enemy.draw(canvas)
        for p_proj in player_projectile_list:
            p_proj.draw(canvas)
        display_renemies(canvas)


    def draw(self, canvas): #Specific to simplegui
        if(game_state == "start"):
            self.start_screen(canvas)
        if (game_state == "difficulty"):
            self.difficulty(canvas)
        if(game_state == "easy"):
            self.easy()
        if(game_state == "med"):
            self.med()
        if(game_state == "hard"):
            self.hard()
        if(game_state == "game"):
            self.game(canvas)


# ----------------------------------------------------------------------------------------------------------
# MAIN DISPLAY
# ----------------------------------------------------------------------------------------------------------

new_game = Game()

def display(canvas):
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

