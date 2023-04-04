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

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites] #true: flip x direction, false: don't flip y direction

def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() #transparent background

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)  #96, 0 is position of the part we want (top left)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)
    

class Player(pygame.sprite.Sprite): #inheriting from sprite for pixel accurate collision (use their methods)
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None #mapping of pixels exists in sprite (which pixel exists to perform perfect pixel collision)
        #for showing animation later
        self.direction = "left" 
        self.animation_count = 0
        #for gravity
        self.fall_count = 0

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
    
    def loop(self, fps): #looping for each frame
        # self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        sprite_sheet = "idle" #default sprite
        if self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self): #update rectangle according to sprite
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)  #sprite uses mask



    def draw(self, window):
        window.blit(self.sprite, (self.rect.x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  #srcalpha supports transparent images?
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)



def draw(window, player, objects):
    #draw background
    window.blit(BG_IMG, (0,0)) #position 0,0 (top left)

    for obj in objects:
        obj.draw(window)

    player.draw(window)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = [] #keep track of collided objects and add rules to it later (traps, fire, .. diff effects)
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj): #sprite class has collision method to detect collision
            if dy > 0: #if falling down
                player.rect.bottom = obj.top  #make bottom of player == top of object colliding
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom #so the player doesn't stay inside of the object (it will go below it)
                player.hit_head()
        
        collided_objects.append(obj) 
        
    return collided_objects()

def handle_move(player):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0 #so player doesn't move when key is lifted
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)


def main(window):
    clock = pygame.time.Clock()
    
    block_size = 96

    #instantiate objects
    player = Player(100, 500, 50, 50)
    floor = [Block(i * block_size, WIN_HEIGHT - block_size, block_size) for i in range(-WIN_WIDTH // block_size, (WIN_WIDTH * 2)// block_size)]


    run = True
    while run:
        clock.tick(FPS) #running 60 frame/second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        player.loop(FPS)
        handle_move(player)
        draw(window, player, floor)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)