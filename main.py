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

import pygame
import os
import time
import random
import math
import sys
from os import listdir
from os.path import isfile, join

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

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.jpg")).convert_alpha())
BG_IMG2 = pygame.image.load(os.path.join("imgs", "a.jpg")).convert_alpha()


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

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"

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

    def move(self, dx):
        self.rect.x += dx

    def loop(self, fps): #looping for each frame
        self.move(self.vel)
        self.update_sprite()

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
        self.speed = load_sprite_sheets("Items", "Potion", 32, 32)
        self.image = self.speed["poison"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "poison"

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
        self.heart = load_sprite_sheets("Items", "Fruits", 16, 16)
        self.image = self.heart["Pineapple"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "Pineapple"

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
        self.speed = load_sprite_sheets("Items", "Destination", 64, 64)
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

    if player.add_speed:
        player_velocity = 15
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
        if obj and obj.name == "fire":
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

    window.fill((0, 0, 0))
    level_text = font.render("Level {}".format(player.level), True, (255, 255, 255))
    level_rect = level_text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
    window.blit(level_text, level_rect)

    pygame.display.update()
    # Wait for a moment
    pygame.time.wait(1500)


########################################################

def draw(window, player, objects, offset_x,offset_y, police, bullets, collectibles, destination):
    #draw background
    if player.level == 2:
        window.blit(BG_IMG2, (0,0))
    else:
        window.blit(BG_IMG, (0,0)) #position 0,0 (top left)
    

    # create text for lives
    lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
    window.blit(lives_text, (10, 10))

    # create text for score
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
    window.blit(score_text, (100, 10))

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
            heart1 = Heart(block_size * 3, WIN_HEIGHT - block_size * 5, 16, 16)
            heart2 = Heart(block_size * 7, WIN_HEIGHT - block_size * 5, 16, 16)
            pineapple = Pineapple(block_size * 4, WIN_HEIGHT - block_size * 5, 12, 12)

            speed = Speed(900, WIN_HEIGHT - block_size - 64, 32, 32)
            collectibles_bullets = CollectibleBullets(1100, WIN_HEIGHT - block_size - 64, 32, 32)
            #blocks and traps
            fire = Fire(700, WIN_HEIGHT - block_size - 64, 16, 32)
            fire.on()
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
                        Block(block_size * 4, WIN_HEIGHT - block_size * 4, block_size),
                        Block(block_size * 4, WIN_HEIGHT - block_size * 4, block_size),
                        Block(block_size * 5, WIN_HEIGHT - block_size * 5, block_size),
                        Block(block_size * 6, WIN_HEIGHT - block_size * 6, block_size),
                        # Block(block_size * 7, WIN_HEIGHT - block_size * 8, block_size),
                        # Block(block_size * 8, WIN_HEIGHT - block_size * 10, block_size),
                        # Block(block_size * 9, WIN_HEIGHT - block_size * 12, block_size),
                        # Block(block_size * 10, WIN_HEIGHT - block_size * 13, block_size),
                        # Block(block_size * 11, WIN_HEIGHT - block_size * 15, block_size),
                        # Block(block_size * 12, WIN_HEIGHT - block_size * 16, block_size),
                        # Block(block_size * 13, WIN_HEIGHT - block_size * 17, block_size),
                        # Block(block_size * 14, WIN_HEIGHT - block_size * 18, block_size),
                        *traps, fire])
            destinations.append(Destination(500, WIN_HEIGHT - block_size * 6 - 128, 32, 32))
            collectibles.append([heart1, heart2, speed, collectibles_bullets, pineapple])
        if j == 2:
            blocks = []
            traps = []
            heart1 = Heart(block_size * 3, WIN_HEIGHT - block_size * 5, 16, 16)
            heart2 = Heart(block_size * 7, WIN_HEIGHT - block_size * 5, 16, 16)
            speed = Speed(900, WIN_HEIGHT - block_size - 64, 32, 32)
            collectibles_bullets = CollectibleBullets(1100, WIN_HEIGHT - block_size - 64, 32, 32)
            #blocks and traps
            fire = Fire(700, WIN_HEIGHT - block_size - 64, 16, 32)
            fire.on()
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
                        Block(block_size * 4, WIN_HEIGHT - block_size * 4, block_size),
                        Block(block_size * 4, WIN_HEIGHT - block_size * 4, block_size),
                        Block(block_size * 5, WIN_HEIGHT - block_size * 5, block_size),
                        Block(block_size * 6, WIN_HEIGHT - block_size * 6, block_size),
                        # Block(block_size * 7, WIN_HEIGHT - block_size * 8, block_size),
                        # Block(block_size * 8, WIN_HEIGHT - block_size * 10, block_size),
                        # Block(block_size * 9, WIN_HEIGHT - block_size * 12, block_size),
                        # Block(block_size * 10, WIN_HEIGHT - block_size * 13, block_size),
                        # Block(block_size * 11, WIN_HEIGHT - block_size * 15, block_size),
                        # Block(block_size * 12, WIN_HEIGHT - block_size * 16, block_size),
                        # Block(block_size * 13, WIN_HEIGHT - block_size * 17, block_size),
                        # Block(block_size * 14, WIN_HEIGHT - block_size * 18, block_size),
                        *traps, fire])
            destinations.append(Destination(500, WIN_HEIGHT - block_size * 6 - 128, 32, 32))
            collectibles.append([heart1, heart2, speed, collectibles_bullets])

        if j == 3:
            blocks = []
            traps = []
            heart1 = Heart(5020, WIN_HEIGHT - block_size * 6.5, 16, 16)
            heart2 = Heart(7200, WIN_HEIGHT - block_size * 5, 16, 16)
            speed1 = Speed(900, WIN_HEIGHT - block_size - 64, 32, 32)
            speed2 = Speed(2500, WIN_HEIGHT - block_size - 64, 32, 32)
            collectibles_bullets = CollectibleBullets(block_size * 5.2, WIN_HEIGHT - block_size * 6.5, 32, 32)
            #blocks and traps
            fire = Fire(3900, WIN_HEIGHT - block_size - 64, 16, 32)
            fire.on()
            floor = [Block(i * block_size, WIN_HEIGHT - block_size, block_size) for i in range(-WIN_WIDTH // block_size, (WIN_WIDTH * 11)// block_size)]

            placed_traps = set()  # set to keep track of placed trap coordinates

            #design
            objects.append([*floor, 
                        Block(0, WIN_HEIGHT - block_size * 2, block_size), 
                        Block(block_size * 5, WIN_HEIGHT - block_size * 5.5, block_size), 
                        #small floating 
                        Block(block_size * 8, WIN_HEIGHT - block_size * 5, block_size),
                        Block(block_size * 9, WIN_HEIGHT - block_size * 5, block_size),
                        Block(block_size * 10, WIN_HEIGHT - block_size * 5, block_size),

                        Block(block_size * 12, WIN_HEIGHT - block_size * 2, block_size),
                        Block(1200, WIN_HEIGHT - block_size * 2, block_size), 
                        Block(1350, WIN_HEIGHT - block_size * 5, block_size),
                        Block(1700, WIN_HEIGHT - block_size * 3.2, block_size), 
                        Block(1950, WIN_HEIGHT - block_size * 3.2, block_size), 

                        Block(2200, WIN_HEIGHT - block_size * 3.5, block_size), 
                        Block(2200 + block_size*3, WIN_HEIGHT - block_size * 3.5, block_size),
                        Block(2100, WIN_HEIGHT - block_size * 6, block_size),
                        
                        Block(2470, WIN_HEIGHT - block_size * 6, block_size),
                        Block(2470+block_size, WIN_HEIGHT - block_size * 6, block_size),

                        Block(2850, WIN_HEIGHT - block_size * 2, block_size),
                        Block(2850, WIN_HEIGHT - block_size * 3, block_size),
                        Block(3100, WIN_HEIGHT - block_size * 5, block_size),
                        Block(3350, WIN_HEIGHT - block_size * 2, block_size),
                        Block(3350, WIN_HEIGHT - block_size * 3, block_size),


                        #thin blocks
                        Block(3750, WIN_HEIGHT - block_size * 2, block_size),
                        Block(3750, WIN_HEIGHT - block_size * 3, block_size),
                        Block(4170, WIN_HEIGHT - block_size * 2, block_size),
                        Block(4170, WIN_HEIGHT - block_size * 3, block_size),
                        #thick blocks
                        Block(4650, WIN_HEIGHT - block_size * 2, block_size),
                        Block(4650, WIN_HEIGHT - block_size * 3, block_size),
                        Block(4650 + block_size, WIN_HEIGHT - block_size * 2, block_size),
                        Block(4650 + block_size, WIN_HEIGHT - block_size * 3, block_size),
                        Block(5000, WIN_HEIGHT - block_size * 5.5, block_size),
                        Block(5300, WIN_HEIGHT - block_size * 2, block_size),
                        Block(5300, WIN_HEIGHT - block_size * 3, block_size),
                        Block(5300 + block_size, WIN_HEIGHT - block_size * 2, block_size),
                        Block(5300 + block_size, WIN_HEIGHT - block_size * 3, block_size),

                        #steps
                        Block(5600 + block_size, WIN_HEIGHT - block_size * 3, block_size),
                        Block(5750 + block_size, WIN_HEIGHT - block_size * 4.5, block_size),
                        Block(5900 + block_size, WIN_HEIGHT - block_size * 6, block_size),
                        
                        Block(6050 + block_size, WIN_HEIGHT - block_size * 6, block_size),
                        Block(6050 + block_size, WIN_HEIGHT - block_size * 6, block_size),



                        *traps, fire])
            destinations.append(Destination(10000, WIN_HEIGHT - block_size - 128, 32, 32))
            collectibles.append([heart1, heart2, speed1, speed2, collectibles_bullets])

    design["objects"] = objects
    design["collectibles"] = collectibles
    design["destinations"] = destinations
    return design



def main_game(window): 
    
    block_size = 96

    #initialize score variable
    score = 0


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

            #fire
            objects[-1].loop()
        else:
            #you win screen
            objects = []
            collectibles = []
            destination = all_destinations[1]

        if player.lives <= 0:
          # game over
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

            level_transition(window, player)


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
        if player.level != 3 and (((player.rect.bottom - offset_y >= WIN_HEIGHT - block_size + 5) and player.y_vel > 0) or (#moving downwards, off the screen
            (player.rect.top - offset_y <= scroll_area_height) and player.y_vel < 0)): #moving upwards, off the screen
            offset_y += player.y_vel
        elif player.level == 3 and (((player.rect.bottom - offset_y >= WIN_HEIGHT - 87) and player.y_vel > 0) or (#moving downwards, off the screen
            (player.rect.top - offset_y <= 15) and player.y_vel < 0)):
            offset_y += player.y_vel


    pygame.quit()
    quit()


def main(window):
    while True:
        window.blit(BG_IMG, (0,0))
        instruction_image = pygame.image.load("keys.png").convert_alpha()
        window.blit(instruction_image, (260, 100))

        # Set up the font
        font = pygame.font.Font(None, 36)


        mx, my = pygame.mouse.get_pos()
        button_1 = pygame.Rect(400, 490, 200, 50)
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
