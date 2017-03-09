import math
import pygame
import sprites
import os
import level

#############################################
# main.py handles game logic and rendering  #
#############################################

WINDOWWIDTH = 1200
WINDOWHEIGHT = 600
FPSCAP = 60
FRAMEINTERVAL = 1000 / FPSCAP

# Init objects
window = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
timer = pygame.time.Clock()
pygame.font.init()
fontmodule = pygame.font.SysFont(None, 30)

###########
# METHODS #
###########

def main():



    players = list
    enemies = list
    projectiles = list


    # Init starting menu
    currentlevel = level.debug()

    current_state = 0

    while True:
        while current_state == 0: # Main Menu state
            render_main_menu(window)
            pygame.display.flip()
            wait_for_key_press()
            current_state = 1


        while current_state == 1: # 'Game' state
            timer.tick(FRAMEINTERVAL)

            update_players(players, timer)
            update_enemies(enemies, timer)
            update_projectiles(projectiles, timer)

            currentlevel.render_level(window)
            render_objects(players, enemies, projectiles)
            pygame.display.flip()

        while current_state == 3: # 'Game Over' state
            render_game_over_screen(window)
            pygame.display.flip()
            wait_for_key_press()
            current_state = 0 # TODO decide whether or not to retry the same level







def update_players(players, timer):
    print("TODO")

def update_enemies(enemies, timer):
    print("TODO")

def update_projectiles(projectiles, timer):
    print("TODO")


def render_objects(players, enemies, projectiles):
    print("TODO")

def render_main_menu(surface):
    surface.blit(fontmodule.render("Avocado Killer!", 8, (255,255,255), (0,0,0)), (200,200))




def render_game_over_screen(surface, score):
    print("TODO")






# Blocks thread until a key on the keyboard is pressed
def wait_for_key_press():
    events = pygame.event.get()
    keepwaiting = True
    while (keepwaiting):
        for i in events:
            if i.type == pygame.KEYUP:
                keepwaiting = False
        events = pygame.event.get()











main()