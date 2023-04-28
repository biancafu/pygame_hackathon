# MIT License

# Copyright (c) 2023 Bianca Fu
# Copyright (c) 2023 Tiffany Leong
# Copyright (c) 2023 Thy Nguyen

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

import pygame
import os
import time
import random
import math
import sys
from os import listdir
from os.path import isfile, join
from pygame import mixer

clock = pygame.time.Clock()
pygame.init()

pygame.display.set_caption("pygame hackathon")
#window dimension
WIN_WIDTH = 980
WIN_HEIGHT = 720
FPS = 60
PLAYER_VEL = 5
POLICE_VEL = 4


window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

# define font for the text
font = pygame.font.SysFont("Arial", 24)


BG_IMG = (pygame.image.load(os.path.join("imgs", "2.png")).convert_alpha())
BG_IMG1 = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.jpg")).convert_alpha())
BG_IMG2 = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "black.jpg")).convert_alpha())
BG_IMG3 = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "c.jpg")).convert_alpha())



#Instantiate mixer
mixer.init()

#Load audio file
mixer.music.load(os.path.join('assets', 'song.mp3'))

print("music started playing....")

#Set preferred volume
mixer.music.set_volume(0.2)

#Play the music
mixer.music.play(4)




################### IMG HANDLING #####################

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
    path = join("assets", "Terrain", "Test.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)  #96, 0 is position of the part we want (top left)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block2(size):
    path = join("assets", "Terrain", "test1.jpg")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)  #96, 0 is position of the part we want (top left)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block3(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(272, 63, size, size)  #192, 130
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

#######################################################
    
##################### USER/ENEMY #########################


class Player(pygame.sprite.Sprite): #inheriting from sprite for pixel accurate collision (use their methods)
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = [load_sprite_sheets("MainCharacters", "Unicorn", 32, 32, True), 
               load_sprite_sheets("MainCharacters", "Cat2", 32, 32, True), 
               load_sprite_sheets("MainCharacters", "Cat", 32, 32, True)]
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None #mapping of pixels exists in sprite (which pixel exists to perform perfect pixel collision)
        #for showing animation later
        self.direction = "right" 
        self.animation_count = 0
        #for gravity
        self.fall_count = 0
        #for jumping
        self.jump_count = 0
        #for hitting fire
        self.hit = False
        self.hit_count = 0
        #lives
        self.lives = 2
        #bullets
        self.bullets = 5
        #collectibles
        self.add_speed = False
        self.add_speed_count = 0

        #score
        self.score = 0

        self.decrease_speed = False
        self.decrease_speed_count = 0
        #level
        self.level = 1


    def jump(self):
        self.y_vel = -self.GRAVITY * 8 #speed of jump = 8 (can change)
        self.animation_count = 0
        self.jump_count += 1
        
        if self.jump_count == 1: #double jumping
            self.fall_count = 0 #remove gravity for second jump

    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        
    def minus_life(self):
        if self.lives > 0:
            self.lives -= 1
            # load audio file
            lose_life_sound = pygame.mixer.Sound(os.path.join("assets", "loselife1.mp3"))
            # play the sound
            lose_life_sound.play()

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
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        #hit for 2 seconds
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps*2:
            self.hit = False
            self.hit_count = 0
        
        #add speed for 1 seconds
        if self.add_speed:
            self.add_speed_count += 1
        if self.add_speed_count > fps*1:
            self.add_speed = False
            self.add_speed_count = 0
        #decrease speed for 1 second
        if self.decrease_speed:
            self.decrease_speed_count += 1
        if self.decrease_speed_count > fps*2:
            self.decrease_speed = False
            self.decrease_speed_count = 0



        self.fall_count += 1
        self.update_sprite()

    def landed(self): #need to reset gravity after landing
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        # self.count = 0 dunno what this does?
        self.y_vel *= -1 #creating bounce back effect


    def update_sprite(self):
        sprite_sheet = "idle" #default sprite
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0: #moving up
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2: #moving down (need certain amount to show fall animation)
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
            
        if self.level == 1:
            i = 0
        elif self.level == 2:
            i = 1
        elif self.level == 3:
            i = 2

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[i][sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self): #update rectangle according to sprite
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)  #sprite uses mask

    def draw(self, window, offset_x, offset_y):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

class Police(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "Police", 32, 32, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height, name="police"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None #mapping of pixels exists in sprite (which pixel exists to perform perfect pixel collision)
        #for showing animation later
        self.direction = "right" 
        self.animation_count = 0
        #for gravity
        self.fall_count = 0
        self.name = name
        #hit by bullet
        self.hit = False
        self.hit_count = 0

    def make_hit(self):
        self.hit = True
        self.hit_count = 0
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y +=dy
            
    def move_towards_player(self, player):
        if player.rect.x > 100:
            dx = player.rect.x - self.rect.x
            # self.x_vel = dx * 0.05
        else: dx = 0
        if self.hit:
            self.x_vel = 0
        elif dx > 19:
            self.direction = "right"
            self.x_vel = POLICE_VEL
        elif dx < -19:
            self.direction = "left"
            self.x_vel = -POLICE_VEL
        elif dx >=0 and dx <= 19:
            self.x_vel = 0

        # Move along this normalized vector towards the player at current speed.
        self.move(self.x_vel, self.y_vel)
        # self.move(dx * 0.05, self.y_vel)

    def loop(self, fps, player): #looping for each frame
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)

        #chasing
        self.move_towards_player(player)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps*2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self): #need to reset gravity after landing
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def update_sprite(self):
        sprite_sheet = "idle" #default sprite
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0: #moving up
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2: #moving down (need certain amount to show fall animation)
            sprite_sheet = "fall"
        elif self.x_vel != 0:
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

    def draw(self, window, offset_x, offset_y):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

###############################################################

##################### OBJECTS/TRAPS/WEAPONS ###################

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  #srcalpha supports transparent images?
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, window, offset_x, offset_y):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block2(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block3(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Alien", 32, 32)
        self.image = self.fire["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"

    # def on(self):
    #     self.animation_name = "on"
    
    # def off(self):
    #     self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0 #since fire is static, we need to reset it this way

class Projectile(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, facing):
        super().__init__(x, y, width, height, "bullet")
        self.projectile = load_sprite_sheets("Traps", "Sand Mud Ice", 16, 16)
        self.image = self.projectile["Ice_Particle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.facing = facing
        self.vel = 8 * facing
        self.animation_count = 0
        self.animation_name = "Ice_Particle"
        self.projectile_sound = pygame.mixer.Sound(os.path.join("assets", "pew.mp3"))
        self.projectile_sound.set_volume(0.2)
        self.audio_played = False

    def move(self, dx):
        self.rect.x += dx

    def loop(self, fps): #looping for each frame
        self.move(self.vel)
        self.update_sprite()
        if not self.audio_played:
            self.projectile_sound.play()
            self.audio_played = True

    def update_sprite(self):
        sprites = self.projectile[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Monster(Object):
    ANIMATION_DELAY = 20

    def __init__(self, x, y, width, height, distance):
        super().__init__(x, y, width, height, "monster")
        self.moster = load_sprite_sheets("MainCharacters", "Monster", 24, 24, True)
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.start = x
        self.distance = distance
        self.vel = 2
        self.direction = 1
        self.animation_count = 0
        self.animation_name = "idle"

    def move(self, dx):
        self.rect.x += dx

    def loop(self): #looping for each frame 
        self.move(self.vel * self.direction)
        if self.rect.right > (self.start + self.distance) or self.rect.left < self.start:
            self.direction *= -1
            
        self.update_sprite()

    def update_sprite(self):
        if self.direction == 1:
            facing = "right"
        else:
            facing = "left"
        sprite_sheet_name = self.animation_name + "_" + facing
        sprites = self.moster[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Trap(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "trap")
        self.trap = load_sprite_sheets("Traps", "Banana", width, height)
        self.image = self.trap["Idle"][0]
    
    def change_image(self, state):
        self.image = self.trap[state][0] 
        # can change trap's image to any state in the sprite sheet
        # ie. trap.change_image("Active")


########################################################

##################### COLLECTIBLES ######################

class Heart(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "heart")
        self.heart = load_sprite_sheets("Items", "Lives", 16, 16)
        self.image = self.heart["dumpling"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "dumpling"


    def loop(self): #looping for each frame

        sprites = self.heart[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Speed(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "speed")
        self.speed = load_sprite_sheets("Items", "Potion", 32, 32)
        self.image = self.speed["bbt"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "bbt"

    def loop(self): #looping for each frame

        sprites = self.speed[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class CollectibleBullets(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "collectibles_bullets")
        self.speed = load_sprite_sheets("Items", "Potion", 24, 24)
        self.image = self.speed["gun"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "gun"

    def loop(self): #looping for each frame

        sprites = self.speed[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Pineapple(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "pineapple")
        self.heart = load_sprite_sheets("Items", "Treasures", 16, 16)
        self.image = self.heart["diamond"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "diamond"

    def loop(self): #looping for each frame

        sprites = self.heart[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

########################################################

##################### START/END ######################

class Destination(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "destination")
        self.speed = load_sprite_sheets("Items", "Destination", 32, 32)
        self.image = self.speed["idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "idle"

    def loop(self): #looping for each frame

        sprites = self.speed[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        #update
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  #sprite uses mask

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
########################################################

##################### MOVEMENTS ########################

def handle_vertical_collision(player, objects, dy):
    collided_objects = [] #keep track of collided objects and add rules to it later (traps, fire, .. diff effects)
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj): #sprite class has collision method to detect collision
            if dy > 0: #if falling down
                player.rect.bottom = obj.rect.top  #make bottom of player == top of object colliding
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom #so the player doesn't stay inside of the object (it will go below it)
                player.hit_head()
        
            collided_objects.append(obj) 

    return collided_objects

def collide(player, objects, dx):
    #preemptively checking if we will collide
    player.move(dx, 0) 
    player.update() #update mask before checking collision
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object  = obj
            break

    player.move(-dx, 0) #moving them back
    player.update() #update the mask back
    return collided_object


def handle_move(player, objects):
    
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0 #so player doesn't move when key is lifted
    collide_left = collide(player, objects, -PLAYER_VEL* 2)
    collide_right = collide(player, objects, PLAYER_VEL* 2)

    # audio for zoom
    speed_sound = pygame.mixer.Sound(os.path.join("assets", "zoom.mp3"))

    if player.add_speed:
        player_velocity = 15
        speed_sound.play()
    elif player.decrease_speed:
        player_velocity = 3
    else:
        player_velocity = PLAYER_VEL

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(player_velocity)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(player_velocity)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and (obj.name == "fire" or obj.name == "monster"):
            player.make_hit()
            player.minus_life()
            if player.lives > 0:
                #reset player position
                player.rect.x -= 150
                player.rect.y = 100
                break
        elif obj and obj.name == "trap":
            player.decrease_speed = True




def handle_police_move(police, objects, player, bullets):

    handle_vertical_collision(police, objects, police.y_vel)
    collide_player_left = collide(player, [police], -POLICE_VEL)
    collide_player_right = collide(player, [police], POLICE_VEL)
    collide_bullet_left = collide(police, bullets, -POLICE_VEL)
    collide_bullet_right = collide(police, bullets, POLICE_VEL)
    to_check = [collide_player_left, collide_player_right, collide_bullet_left, collide_bullet_right]

    for obj in to_check:
        if obj and obj.name == "police":
            player.make_hit()
            player.minus_life()
            if player.lives > 0:
                #reset police position
                police.rect.x = -100
                police.rect.y = 500
        if obj and obj.name == "bullet":
            police.make_hit()
            return obj
            

def game_over(window):
    font = pygame.font.SysFont("Arial", 32)
    
    text_surface = font.render("GAME OVER", True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 20))

    restart_text = font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 20))

    while True:
        # blit the text surfaces on the screen
        window.blit(text_surface, text_rect)
        window.blit(restart_text, restart_rect)
        # add a delay before showing the game over screen
        pygame.time.delay(500)
        # update the displaye to show the new text
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
              pygame.quit()
              quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                  return True


def level_transition(window, player):

    # load the audio file
    level_transition_sound = pygame.mixer.Sound(os.path.join("assets", "levelup.mp3"))
    level_transition_sound.set_volume(0.2)

    # Load the image that you want to use as the background
    bg_image = pygame.image.load(os.path.join("assets", "vortex.png"))

    # Scale the image to fit the window size
    bg_image = pygame.transform.scale(bg_image, (WIN_WIDTH, WIN_HEIGHT))

    # Blit the image onto the window surface
    window.blit(bg_image, (0, 0))

    # window.fill((0, 0, 0))
    level_text = font.render("Level {}".format(player.level), True, (255, 255, 255))
    level_rect = level_text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
    window.blit(level_text, level_rect)

    # play the audio
    if player.level != 1:
      level_transition_sound.play()

    pygame.display.update()
    # Wait for a moment
    pygame.time.wait(1500)

def ending_screen(window, player):

    # # load the audio file
    # level_transition_sound = pygame.mixer.Sound(os.path.join("assets", "levelup.mp3")
    # level_transition_sound.set_volume(0.2)

    window.fill((0, 0, 0))
    text = font.render("Congratulations! You have escaped the police!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2 - 40))
    score_text = font.render("And you snatched {} gems on the way".format(player.score), True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2+50))
    window.blit(text, text_rect)
    window.blit(score_text, score_rect)

    # play the audio
    # level_transition_sound.play()

    pygame.display.update()
    # Wait for a moment
    pygame.time.wait(8000)
    pygame.quit()
    sys.exit()


########################################################

def draw(window, player, objects, offset_x,offset_y, police, bullets, collectibles, destination):
    #draw background
    if player.level == 1:
        window.blit(BG_IMG1, (0,0))
    elif player.level == 2:
        window.blit(BG_IMG2, (0,0))
    elif player.level == 3:
        window.blit(BG_IMG3, (0,0))
    else:
        window.blit(BG_IMG2, (0,0)) #position 0,0 (top left)
    

    # create text for lives
    lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
    window.blit(lives_text, (10, 10))

    # create text for score
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
    window.blit(score_text, (250, 10))

    # create text for bullets
    bullets_text = font.render(f"Ammo: {player.bullets}", True, (255, 255, 255))
    window.blit(bullets_text, (125, 10))

    for obj in objects:
        obj.draw(window, offset_x, offset_y)
    
    for bullet in bullets:
        bullet.draw(window, offset_x, offset_y)

    for collectible in collectibles:
        collectible.draw(window, offset_x, offset_y)
    
    destination.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)
    police.draw(window, offset_x, offset_y)

    pygame.display.update()

def level_design(block_size):
    design = {}
    objects = []
    collectibles = []
    destinations = []
    for j in range(0,4):
        if j == 0:
            objects.append(0)
            collectibles.append(0)
            destinations.append(0)
        if j == 1:
            blocks = []
            traps = []
            heart1 = Heart(block_size * 7, WIN_HEIGHT - block_size * 4, 16, 16)
            heart2 = Heart(block_size * 18, WIN_HEIGHT - block_size * 6, 16, 16)
            heart3 = Heart(block_size * 32, WIN_HEIGHT - block_size * 4, 16, 16)
            heart4 = Heart(block_size * 21, WIN_HEIGHT - block_size * 2, 16, 16)
            heart5 = Heart(block_size * 25, WIN_HEIGHT - block_size * 4, 16, 16)
            heart6 = Heart(4700, WIN_HEIGHT - block_size * 2, 16, 16)
            heart7 = Heart(5350, WIN_HEIGHT - block_size * 2, 16, 16)

            pineapples = [
              Pineapple(block_size * 15, WIN_HEIGHT - block_size * 4, 12, 12),  
              Pineapple(block_size * 16, WIN_HEIGHT - block_size * 5, 12, 12),
              Pineapple(block_size * 17, WIN_HEIGHT - block_size * 6, 12, 12),
              Pineapple(block_size * 24, WIN_HEIGHT - block_size * 4, 12, 12),
              Pineapple(block_size * 31, WIN_HEIGHT - block_size * 4, 12, 12),
              Pineapple(4800, WIN_HEIGHT - block_size * 3, 12, 12),
              Pineapple(5000, WIN_HEIGHT - block_size * 2, 12, 12),
              Pineapple(5100, WIN_HEIGHT - block_size * 3, 12, 12),
            ]

            speed1 = Speed(block_size * 10, WIN_HEIGHT - block_size - 64, 32, 32)
            speed2 = Speed(3500, WIN_HEIGHT - block_size - 64, 32, 32)
            collectibles_bullets = CollectibleBullets(block_size * 28, WIN_HEIGHT - block_size - 64, 32, 32)
            #blocks and traps
            fire = Fire(4200, WIN_HEIGHT - block_size - 64, 16, 32)
            monster = Monster(block_size * 22, WIN_HEIGHT - block_size - 64, 16, 32, block_size * 2)
            floor = [Block(i * block_size, WIN_HEIGHT - block_size, block_size) for i in range(-WIN_WIDTH // block_size, (WIN_WIDTH * 20)// block_size)]

            placed_traps = set()  # set to keep track of placed trap coordinates
        
            for i in range(5):  # create 5 traps
                while True:
                    x = random.randint(block_size * 4, WIN_WIDTH * 5 - block_size * 4)  # generate a random x coordinate within a range
                    y = WIN_HEIGHT - block_size - 30  # set y-coordinate to floor level
                    # check if there's a block at this position
                    for block in blocks:
                        if block.x <= x <= block.x + block.width and block.y <= y <= block.y + block.height:
                            # there's a block at this position, adjust y-coordinate
                            y = block.y - 43
                            break  # stop iterating over blocks since we found one that overlaps
                    # check if the coordinates are already taken by another trap
                    if (x,y) not in placed_traps:        
                    # add the trap to the list and add its coordinates to the placed set
                        trap = Trap(x, y, 16, 32)
                        trap.change_image("Idle")
                        traps.append(trap)
                        placed_traps.add((x, y))
                        break # found an available coordinate, break out of the loop
            #design
            objects.append([*floor, 
                        Block(0, WIN_HEIGHT - block_size * 2, block_size), 
                        Block(block_size * 3, WIN_HEIGHT - block_size * 4, block_size),
                        Block(block_size * 5, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 6, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 7, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 14, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 15, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 16, WIN_HEIGHT - block_size * 4, block_size),
                        Block(block_size * 17, WIN_HEIGHT - block_size * 5, block_size),
                        Block(block_size * 24, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 25, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 30, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 31, WIN_HEIGHT - block_size * 3, block_size),
                        Block(block_size * 32, WIN_HEIGHT - block_size * 3, block_size),
                        *traps, fire, monster])
            destinations.append(Destination(5500, WIN_HEIGHT - block_size - 128, 32, 32))
            collectibles.append([heart1, heart2, heart3, heart4, heart5, heart6, heart7, speed1, speed2, collectibles_bullets, *pineapples])
        if j == 2:
            blocks = []
            traps = []
            heart1 = Heart(block_size * 13, WIN_HEIGHT - block_size * 5, 16, 16)
            heart2 = Heart(block_size * 17, WIN_HEIGHT - block_size * 8, 16, 16)
            heart3 = Heart(block_size * 20, WIN_HEIGHT - block_size * 17, 16, 16)
            heart4 = Heart(block_size * 25, WIN_HEIGHT - block_size * 10, 16, 16)
            speed = Speed(900, WIN_HEIGHT - block_size - 64, 32, 32)
            speed1 = Speed(block_size * 19, WIN_HEIGHT - block_size * 7 - 64, 32, 32)
            collectibles_bullets = CollectibleBullets(1100, WIN_HEIGHT - block_size - 64, 32, 32)
            #blocks and traps
            fire = Fire(700, WIN_HEIGHT - block_size - 64, 16, 32)
            # fire.on()
            floor = [Block2(i * block_size, WIN_HEIGHT - block_size, block_size) for i in range(-WIN_WIDTH // block_size, (WIN_WIDTH * 20)// block_size)]

            placed_traps = set()  # set to keep track of placed trap coordinates
        
            for i in range(5):  # create 5 traps
                while True:
                    x = random.randint(block_size * 4, WIN_WIDTH * 5 - block_size * 4)  # generate a random x coordinate within a range
                    y = WIN_HEIGHT - block_size - 30  # set y-coordinate to floor level
                    # check if there's a block at this position
                    for block in blocks:
                        if block.x <= x <= block.x + block.width and block.y <= y <= block.y + block.height:
                            # there's a block at this position, adjust y-coordinate
                            y = block.y - 43
                            break  # stop iterating over blocks since we found one that overlaps
                    # check if the coordinates are already taken by another trap
                    if (x,y) not in placed_traps:        
                    # add the trap to the list and add its coordinates to the placed set
                        trap = Trap(x, y, 16, 32)
                        trap.change_image("Idle")
                        traps.append(trap)
                        placed_traps.add((x, y))
                        break # found an available coordinate, break out of the loop
            #design
            pineapples = [
                Pineapple(block_size * 14, WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 14.5, WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 15, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 24, WIN_HEIGHT - block_size * 19, 16, 16),
                Pineapple(block_size * 24.5, WIN_HEIGHT - block_size * 19, 16, 16),
                Pineapple(block_size * 25, WIN_HEIGHT - block_size * 19, 16, 16),
                Pineapple(block_size * 24, WIN_HEIGHT - block_size * 19.5, 16, 16),
                Pineapple(block_size * 24.5, WIN_HEIGHT - block_size * 19.5, 16, 16),
                Pineapple(block_size * 25, WIN_HEIGHT - block_size * 19.5, 16, 16),
                Pineapple(block_size * 17, WIN_HEIGHT - block_size * 23, 16, 16),
                Pineapple(block_size * 16.5, WIN_HEIGHT - block_size * 23, 16, 16),
                Pineapple(block_size * 16, WIN_HEIGHT - block_size * 23, 16, 16),
                Pineapple(block_size * 23.5, WIN_HEIGHT - block_size * 9, 16, 16),
                Pineapple(block_size * 26, WIN_HEIGHT - block_size * 10, 16, 16),
                Pineapple(block_size * 27, WIN_HEIGHT - block_size * 11, 16, 16),
                Pineapple(block_size * 17, WIN_HEIGHT - block_size * 19, 16, 16),
                Pineapple(block_size * 17.5, WIN_HEIGHT - block_size * 19, 16, 16),
                Pineapple(block_size * 18, WIN_HEIGHT - block_size * 19, 16, 16),
            ]
            objects.append([*floor, 
                        Block2(10, WIN_HEIGHT - block_size * 2, block_size), 
                        Block2(block_size * 13, WIN_HEIGHT - block_size * 3, block_size),
                        Block2(block_size * 15, WIN_HEIGHT - block_size * 5, block_size),
                        Block2(block_size * 17, WIN_HEIGHT - block_size * 6, block_size),
                        Block2(block_size * 17, WIN_HEIGHT - block_size * 7, block_size),
                        Block2(block_size * 19, WIN_HEIGHT - block_size * 7, block_size),
                        Block2(block_size * 21, WIN_HEIGHT - block_size * 7, block_size),
                        Block2(block_size * 23, WIN_HEIGHT - block_size * 8, block_size),
                        Block2(block_size * 25, WIN_HEIGHT - block_size * 9, block_size),
                        Block2(block_size * 27, WIN_HEIGHT - block_size * 10, block_size),
                        Block2(block_size * 25, WIN_HEIGHT - block_size * 12, block_size),
                        Block2(block_size * 23, WIN_HEIGHT - block_size * 14, block_size),
                        Block2(block_size * 21, WIN_HEIGHT - block_size * 16, block_size),
                        Block2(block_size * 19, WIN_HEIGHT - block_size * 16, block_size),
                        Block2(block_size * 17, WIN_HEIGHT - block_size * 18, block_size),
                        Block2(block_size * 24, WIN_HEIGHT - block_size * 18, block_size),
                        Block2(block_size * 19, WIN_HEIGHT - block_size * 20, block_size),
                        Block2(block_size * 17, WIN_HEIGHT - block_size * 22, block_size),
                        Block2(block_size * 15, WIN_HEIGHT - block_size * 22, block_size),
                        Block2(block_size * 14, WIN_HEIGHT - block_size * 22, block_size),
                        Block2(block_size * 13, WIN_HEIGHT - block_size * 24, block_size),
                        *traps, fire])
            destinations.append(Destination(block_size * 12.5, WIN_HEIGHT - block_size * 24 - 128, 32, 32))
            collectibles.append([heart1, heart2, heart3,heart4, speed, speed1, collectibles_bullets, *pineapples])

        if j == 3:
            blocks = []
            traps = [
                Trap(1350, WIN_HEIGHT - block_size - 30, 16, 32),
                Trap(1450, WIN_HEIGHT - block_size - 30, 16, 32),
                Trap(3000, WIN_HEIGHT - block_size - 30, 16, 32),
                Trap(3600, WIN_HEIGHT - block_size*6.5 - 30, 16, 32),
                Trap(4350, WIN_HEIGHT - block_size - 30, 16, 32),
                Trap(5750, WIN_HEIGHT - block_size*3 - 30, 16, 32),
                Trap(5800, WIN_HEIGHT - block_size - 30, 16, 32),
                Trap(6000, WIN_HEIGHT - block_size - 30, 16, 32),
                Trap(7700 + block_size *7, WIN_HEIGHT - block_size*5 - 30, 16, 32),
                Trap(9000, WIN_HEIGHT - block_size - 30, 16, 32),
            ]
            heart1 = Heart(block_size * 5.2, WIN_HEIGHT - block_size * 6.5, 16, 16)
            heart2 = Heart(7200, WIN_HEIGHT - block_size * 5, 16, 16)
            heart3 = Heart(3560, WIN_HEIGHT - block_size * 5, 16, 16)
            heart4 = Heart(6900, WIN_HEIGHT - block_size*2.2, 16, 16)
            hearts = [heart1, heart2, heart3, heart4]
            speed1 = Speed(900, WIN_HEIGHT - block_size - 64, 32, 32)
            speed2 = Speed(4300, WIN_HEIGHT - block_size*6.5 - 64, 32, 32)
            speed3 = Speed(7500, WIN_HEIGHT - block_size - 64, 32, 32)
            speed4 = Speed(7500 + block_size *10, WIN_HEIGHT - block_size - 64, 32, 32)
            
            collectibles_bullets = [
                CollectibleBullets(3120, WIN_HEIGHT - block_size * 5.5, 32, 32),
                CollectibleBullets(4000, WIN_HEIGHT - block_size * 1.5, 32, 32)
                                    ]
            #blocks and traps
            monster = Monster(block_size * 8 + 25, WIN_HEIGHT - block_size * 5.5, 24, 24, 200)
            monster2 = Monster(4000, WIN_HEIGHT - block_size * 7, 24, 24, 320)
            monster3 = Monster(4900, WIN_HEIGHT - block_size * 1.8, 24, 24, 320)
            monster4 = Monster(3000, WIN_HEIGHT - block_size * 1.8, 24, 24, 320)
            monster5 = Monster(6770, WIN_HEIGHT - block_size * 1.8, 24, 24, 400)
            monster6 = Monster(7550, WIN_HEIGHT - block_size * 1.8, 24, 24, 500)
            monster7 = Monster(8000, WIN_HEIGHT - block_size * 1.8, 24, 24, 500)
            monsters = [monster, monster2, monster3, monster4, monster5, monster6, monster7]

            fires = [
                Fire(3900, WIN_HEIGHT - block_size - 64, 16, 32),
                Fire(3500, WIN_HEIGHT - block_size - 64, 16, 32),
                Fire(3650, WIN_HEIGHT - block_size - 64, 16, 32),
                Fire(5200, WIN_HEIGHT - block_size*6.5 - 64, 16, 32),
                Fire(5750, WIN_HEIGHT - block_size - 64, 16, 32),
            ]

            pineapples = [
                Pineapple(block_size * 3, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(block_size * 3.5, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(block_size * 4, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(block_size * 5.5, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(block_size * 6, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(block_size * 6.5, WIN_HEIGHT - block_size * 2, 16, 16),

                Pineapple(block_size * 8, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 9, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 10, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 17.5, WIN_HEIGHT - block_size * 4.2, 16, 16),
                Pineapple(block_size * 18, WIN_HEIGHT - block_size * 4.2, 16, 16),
                Pineapple(block_size * 18.5, WIN_HEIGHT - block_size * 4.2, 16, 16),
                Pineapple(block_size * 26, WIN_HEIGHT - block_size * 6.5, 16, 16),

                Pineapple(2200 + block_size *0.7, WIN_HEIGHT - block_size * 1.7, 16, 16),
                Pineapple(2200 + block_size *2.2, WIN_HEIGHT - block_size * 1.7, 16, 16),
                Pineapple(2200 + block_size *2.7, WIN_HEIGHT - block_size * 1.7, 16, 16),

                Pineapple(block_size * 19.5, WIN_HEIGHT - block_size * 1.7, 16, 16),
                Pineapple(block_size * 20, WIN_HEIGHT - block_size * 1.7, 16, 16),
                Pineapple(block_size * 20.5, WIN_HEIGHT - block_size * 1.7, 16, 16),

                Pineapple(2150, WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(2150, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(2150, WIN_HEIGHT - block_size * 6.5, 16, 16),

                Pineapple(2320, WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(2320, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(2320, WIN_HEIGHT - block_size * 6.5, 16, 16),


                Pineapple(2850, WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(2850, WIN_HEIGHT - block_size * 5.5, 16, 16),


                Pineapple(2850 + 150, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(2900 + 150, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(2950 + 150, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(3000 + 150, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(3050 + 150, WIN_HEIGHT - block_size * 2, 16, 16),
                Pineapple(2850 + 150, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(2900 + 150, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(2950 + 150, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(3000 + 150, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(3050 + 150, WIN_HEIGHT - block_size * 2.5, 16, 16),
                
                #upper
                Pineapple(3400, WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(3400 + block_size * 0.5, WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(3400 + block_size * 1, WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(3580 + block_size * 0.5, WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(3580 + block_size * 1, WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(3800, WIN_HEIGHT - block_size * 8, 16, 16),
                Pineapple(3800 + block_size * 0.5, WIN_HEIGHT - block_size * 8, 16, 16),
                Pineapple(3800 + block_size * 1, WIN_HEIGHT - block_size * 8, 16, 16),
                Pineapple(3800 + block_size * 2, WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(3800 + block_size * 2.5, WIN_HEIGHT - block_size * 7, 16, 16),

                #lower (thin blocks)
                Pineapple(3950, WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(4000, WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(4050, WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(3950, WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(4000, WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(4050, WIN_HEIGHT - block_size * 4, 16, 16),

                Pineapple(4340, WIN_HEIGHT - block_size * 1.8, 16, 16),
                Pineapple(4380, WIN_HEIGHT - block_size * 1.8, 16, 16),
                Pineapple(4420, WIN_HEIGHT - block_size * 1.8, 16, 16),
                Pineapple(4460, WIN_HEIGHT - block_size * 1.8, 16, 16),
                Pineapple(4500, WIN_HEIGHT - block_size * 1.8, 16, 16),

                #thickblock
                Pineapple(4650, WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(4700, WIN_HEIGHT - block_size * 4, 16, 16),

                Pineapple(4950, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(4990, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(5030, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(5070, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(5110, WIN_HEIGHT - block_size * 2.5, 16, 16),
                Pineapple(4950, WIN_HEIGHT - block_size * 3, 16, 16),
                Pineapple(4990, WIN_HEIGHT - block_size * 3, 16, 16),
                Pineapple(5030, WIN_HEIGHT - block_size * 3, 16, 16),
                Pineapple(5070, WIN_HEIGHT - block_size * 3, 16, 16),
                Pineapple(5110, WIN_HEIGHT - block_size * 3, 16, 16),

                Pineapple(5170, WIN_HEIGHT - block_size * 7.7, 16, 16),
                Pineapple(5210, WIN_HEIGHT - block_size * 7.7, 16, 16),
                Pineapple(5250, WIN_HEIGHT - block_size * 7.7, 16, 16),

                Pineapple(5700, WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(5740, WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(5810, WIN_HEIGHT - block_size * 6.5, 16, 16),


                Pineapple(5830 + block_size * 1, WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(5830 + block_size * 1,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(6130 + block_size * 1,WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(6130 + block_size * 1,WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(6170 + block_size * 1,WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(6270 + block_size * 1,WIN_HEIGHT - block_size * 6.5, 16, 16),

                Pineapple(6800 ,WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(6840 ,WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(6880 ,WIN_HEIGHT - block_size * 4, 16, 16),

                Pineapple(7300 ,WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(7300 + block_size * 0.5,WIN_HEIGHT - block_size * 4, 16, 16),

                #cheeto
                Pineapple(block_size * 68,WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 68.5,WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 69,WIN_HEIGHT - block_size * 5, 16, 16),

                Pineapple(block_size * 71.5,WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(block_size * 72,WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(block_size * 72.5,WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(block_size * 71.5,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 72,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 72.5,WIN_HEIGHT - block_size * 5.5, 16, 16),

                Pineapple(block_size * 74,WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(block_size * 74.5,WIN_HEIGHT - block_size * 6.5, 16, 16),

                #Hi
                Pineapple(block_size * 78.7,WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 78.7,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 78.7,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 79.2,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 79.7,WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 79.7,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 79.7,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 80.5,WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 80.5,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 80.5,WIN_HEIGHT - block_size * 6, 16, 16),

                #morecheeto
                Pineapple(block_size * 79,WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(block_size * 78.5,WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(block_size * 79,WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(block_size * 79.5,WIN_HEIGHT - block_size * 6.5, 16, 16),


                Pineapple(block_size * 85,WIN_HEIGHT - block_size * 7.5, 16, 16),
                Pineapple(block_size * 85.5,WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(block_size * 86,WIN_HEIGHT - block_size * 6.5, 16, 16),

                Pineapple(block_size * 89,WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(block_size * 89.5,WIN_HEIGHT - block_size * 7, 16, 16),

                Pineapple(block_size * 91.5,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 92,WIN_HEIGHT - block_size * 6, 16, 16),

                Pineapple(block_size * 94.5,WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(block_size * 94.5,WIN_HEIGHT - block_size * 4, 16, 16),
                Pineapple(block_size * 95,WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(block_size * 95,WIN_HEIGHT - block_size * 4, 16, 16),

                Pineapple(block_size * 96,WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(block_size * 96.5,WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(block_size * 97,WIN_HEIGHT - block_size * 7, 16, 16),
                Pineapple(block_size * 97.5,WIN_HEIGHT - block_size * 6.5, 16, 16),
                Pineapple(block_size * 98,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 98.5,WIN_HEIGHT - block_size * 5.5, 16, 16),
                Pineapple(block_size * 99,WIN_HEIGHT - block_size * 5, 16, 16),
                Pineapple(block_size * 99.5,WIN_HEIGHT - block_size * 4.5, 16, 16),
                Pineapple(block_size * 100,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 100.5,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 101,WIN_HEIGHT - block_size * 6, 16, 16),
                Pineapple(block_size * 101.5,WIN_HEIGHT - block_size * 6, 16, 16),
                

            ]
            floor = [Block3(i * block_size, WIN_HEIGHT - block_size, block_size) for i in range(-WIN_WIDTH // block_size, (WIN_WIDTH * 11)// block_size)]

            #design
            objects.append([*floor, 
                        Block3(0, WIN_HEIGHT - block_size * 2, block_size), 
                        Block3(block_size * 5, WIN_HEIGHT - block_size * 5.5, block_size), 
                        #small floating 
                        Block3(block_size * 8, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(block_size * 9, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(block_size * 10, WIN_HEIGHT - block_size * 5, block_size),

                        Block3(1200, WIN_HEIGHT - block_size * 2, block_size), 
                        Block3(1350, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(1700, WIN_HEIGHT - block_size * 3.5, block_size), 
                        Block3(1950, WIN_HEIGHT - block_size * 3.5, block_size), 

                        Block3(2200, WIN_HEIGHT - block_size * 3.5, block_size), 
                        Block3(2200 + block_size*3, WIN_HEIGHT - block_size * 3.5, block_size),
 
                        Block3(2470, WIN_HEIGHT - block_size * 6, block_size),
                        Block3(2470+block_size, WIN_HEIGHT - block_size * 6, block_size),

                        Block3(2850, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(2850, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(3100, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(3350, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(3350, WIN_HEIGHT - block_size * 3, block_size),

                        #upper level
                        Block3(3200 + block_size *1, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *2, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *3, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *4, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *5, WIN_HEIGHT - block_size * 6.5, block_size),
                        
                        Block3(3200 + block_size *8, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *9, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *10, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(3200 + block_size *11, WIN_HEIGHT - block_size * 6.5, block_size),

                        Block3(3000 + block_size *14, WIN_HEIGHT - block_size * 6.5, block_size),
                        #thin blocks
                        Block3(3750, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(3750, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(4170, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(4170, WIN_HEIGHT - block_size * 3, block_size),

                        
                        #thick blocks
                        Block3(4650, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(4650, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(4650 + block_size, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(4650 + block_size, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(5300, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(5300, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(5300 + block_size, WIN_HEIGHT - block_size * 2, block_size),
                        Block3(5300 + block_size, WIN_HEIGHT - block_size * 3, block_size),


                        Block3(5000 + block_size , WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(5000 + block_size *2, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(5000 + block_size *3, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(5000, WIN_HEIGHT - block_size * 5.5, block_size),

                        #steps
                        Block3(5600 + block_size, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(5500 + block_size, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(5800 + block_size, WIN_HEIGHT - block_size * 4.5, block_size),
                        Block3(6000 + block_size, WIN_HEIGHT - block_size * 6, block_size),
                        Block3(6100 + block_size, WIN_HEIGHT - block_size * 3.5, block_size),
                        Block3(6250 + block_size, WIN_HEIGHT - block_size * 6, block_size),
                        Block3(6450 + block_size, WIN_HEIGHT - block_size * 4, block_size),

                        #hidden
                        Block3(6800, WIN_HEIGHT - block_size * 3.5, block_size),
                        Block3(6800 + block_size, WIN_HEIGHT - block_size * 3.5, block_size),

                        Block3(7370, WIN_HEIGHT - block_size * 2, block_size),
                        
                        Block3(7300+ block_size * 3, WIN_HEIGHT - block_size * 4.5, block_size),
                        Block3(7300+ block_size * 4, WIN_HEIGHT - block_size * 4.5, block_size),
                        Block3(7300+ block_size * 5, WIN_HEIGHT - block_size * 5.5, block_size),

                        Block3(6870 + block_size *2, WIN_HEIGHT - block_size * 5.5, block_size),
                        Block3(7100 + block_size *2, WIN_HEIGHT - block_size * 6.5, block_size),
                        Block3(7100 + block_size *3, WIN_HEIGHT - block_size * 6.5, block_size),

                        Block3(7300 + block_size *2, WIN_HEIGHT - block_size * 3.5, block_size),
              
                        #big gap

                        Block3(7500 + block_size *7.5, WIN_HEIGHT - block_size * 6, block_size),
                        Block3(7500 + block_size *8.5, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(7500 + block_size *9.5, WIN_HEIGHT - block_size * 4, block_size),

                        Block3(9100, WIN_HEIGHT - block_size * 3.5, block_size),
                        Block3(8450 + block_size *3, WIN_HEIGHT - block_size * 4.8, block_size),
                        Block3(8450 + block_size *4, WIN_HEIGHT - block_size * 4.8, block_size),

                        Block3(8950 + block_size *3, WIN_HEIGHT - block_size * 6, block_size),
                        Block3(8950 + block_size *5, WIN_HEIGHT - block_size * 3, block_size),
                        Block3(8950 + block_size *7, WIN_HEIGHT - block_size * 5, block_size),
                        Block3(8950 + block_size *8, WIN_HEIGHT - block_size * 5, block_size),

                        Block3(9900, WIN_HEIGHT - block_size * 3.7, block_size),
                        Block3(9900 + block_size, WIN_HEIGHT - block_size * 3.7, block_size),







                        *traps, *fires, *monsters])
            destinations.append(Destination(10000, WIN_HEIGHT - block_size*4.5, 32, 32))
            collectibles.append([*hearts, speed1, speed2, speed3, speed4, *collectibles_bullets, *pineapples])

    design["objects"] = objects
    design["collectibles"] = collectibles
    design["destinations"] = destinations
    return design



def main_game(window): 
    
    block_size = 96

    #initialize score variable
    score = 0

    # load audio file for collectibles
    collect_item_sound = pygame.mixer.Sound(os.path.join("assets", "itemcollect.mp3"))

    # load audio file for game_over
    game_over_sound = pygame.mixer.Sound(os.path.join("assets", "gameover.mp3"))

    #instantiate objects (same for every level)

    player = Player(block_size * 3, WIN_HEIGHT - block_size * 4, 50, 50)
    police = Police(-200, 500, 50, 50)
    bullets = []

    design = level_design(block_size)
    all_objects = design["objects"]
    all_collectibles = design["collectibles"]
    all_destinations = design["destinations"]

    
    offset_x = 0
    scroll_area_width = 320
    #vertical scroll
    offset_y = 0
    scroll_area_height = 320
    run = True
    level_transition(window, player)
    while run:
        clock.tick(FPS) #running 60 frame/second

        if player.level < len(all_objects):
            objects = all_objects[player.level]
            collectibles = all_collectibles[player.level]
            destination = all_destinations[player.level]

            #monster
            for obj in objects:
                if obj.name == "monster" or obj.name == "fire":
                    obj.loop()
        else:
            #you win screen
            objects = []
            collectibles = []
            destination = all_destinations[1]

        if player.lives <= 0:
          # game over
          game_over_sound.play()
          if game_over(window):
            main_game(window)
          else:
            # exit the loop
            run = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN: #not putting in handle_move since for that u can hold down  key and continue movement
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    #resetting jump_count on landing, once landed, we can jump again
                    player.jump()
                elif event.key == pygame.K_s:
                    if player.direction == "left":
                        facing = -1
                    else:
                        facing = 1
                        
                    if player.bullets > 0: #only 5 bullets
                        bullets.append(Projectile(round(player.rect.x + player.rect.width //2), round(player.rect.y + player.rect.height//2), 6, 6, facing))
                        player.bullets -= 1
                elif event.key == pygame.K_ESCAPE:
                    run = False

        for bullet in bullets:
                bullet.x += bullet.vel
                bullet.loop(FPS)
        
        #collectibles detection
        for collectible in collectibles:
            collectible.loop()
            if player.rect.colliderect(collectible.rect):
                collectibles.remove(collectible)
                collect_item_sound.play()
                if collectible.name == "heart":
                    player.lives += 1
                elif collectible.name == "speed":
                    player.add_speed = True
                elif collectible.name == "collectibles_bullets":
                    player.bullets += 3
                elif collectible.name == "pineapple":
                    player.score += 1
                

        #level up: destination detection
        if player.rect.x > destination.rect.right and player.rect.bottom - 128 <= destination.rect.y:
            pygame.time.wait(500)
            player.level += 1
            offset_x = 0
            offset_y = 0

            #reset player position
            player.rect.x = 0
            player.rect.y = WIN_HEIGHT - block_size * 4
            #reset police position
            police.rect.x = -200
            police.rect.y = 500

            if player.level <= 3:
                level_transition(window, player)
            else:
                ending_screen(window, player)


        player.loop(FPS)
        police.loop(FPS, player)

        handle_move(player, objects)
        collided_bullet = handle_police_move(police, objects, player, bullets)
        #make bullet disappear after collision
        if collided_bullet:
            bullets.remove(collided_bullet)
        draw(window, player, objects, offset_x, offset_y, police, bullets, collectibles, destination)

        if ((player.rect.right - offset_x >= WIN_WIDTH - scroll_area_width) and player.x_vel > 0) or (#moving to the right, off the screen
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0): #moving to the left, off the screen
            offset_x += player.x_vel

        #vertical scroll
        if player.level == 2 and (((player.rect.bottom - offset_y >= WIN_HEIGHT - block_size + 5) and player.y_vel > 0) or (#moving downwards, off the screen
            (player.rect.top - offset_y <= scroll_area_height) and player.y_vel < 0)): #moving upwards, off the screen
            offset_y += player.y_vel
        elif (((player.rect.bottom - offset_y >= WIN_HEIGHT - 87) and player.y_vel > 0) or (#moving downwards, off the screen
            (player.rect.top - offset_y <= 15) and player.y_vel < 0)):
            offset_y += player.y_vel


    pygame.quit()
    quit()


def main(window):
    while True:
        window.blit(BG_IMG, (0,0))
        # instruction_image = pygame.image.load(os.path.join("assets", "keys.png")).convert_alpha()
        # window.blit(instruction_image, (10, 100))

        # Set up the font
        font = pygame.font.Font(None, 36)


        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(400, 590, 200, 50)
        # draw button rectangle
        pygame.draw.rect(window, (255, 255, 255), button_1)

        text_surface = font.render("Start Game", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_1.center)
        window.blit(text_surface, text_rect)

        if button_1.collidepoint((mx, my)):
            if click:
                main_game(window)
        
        pygame.display.update()

        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    
        pygame.display.update()


if __name__ == "__main__":
    main(window)
