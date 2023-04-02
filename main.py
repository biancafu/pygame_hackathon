import pygame
import os
import time
import random
from os import listdir
from os.path import isfile, join

pygame.display.set_caption("pygame hackathon")
#window dimension
WIN_WIDTH = 980
WIN_HEIGHT = 720
FPS = 60
PLAYER_VEL = 5

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.jpg")))

window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

class Player(pygame.sprite.Sprite): #inheriting from sprite for pixel accurate collision (use their methods)
    COLOR = (255, 0, 0)
    GRAVITY = 1 #33:33
    
    def __init__(self, x, y, width, height) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None

        #for showing animation later
        self.direction = "left" 
        self.animation_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y +=dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps):
        self.move(self.x_vel, self.y_vel)

    def draw(self, window):
        pygame.draw.rect(window, self.COLOR, self.rect)



def draw(window, player):
    #draw background
    window.blit(BG_IMG, (0,0)) #position 0,0 (top left)
    player.draw(window)

    pygame.display.update()

def handle_move(player):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0 #so player doesn't move when key is lifted
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)


def main(window):
    clock = pygame.time.Clock()

    player = Player(100, 500, 50, 50)
    
    run = True
    while run:
        clock.tick(FPS) #running 60 frame/second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        player.loop(FPS)
        handle_move(player)
        draw(window, player)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)