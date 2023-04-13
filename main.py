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
POLICE_VEL = 5

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.jpg")))

window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

# define font for the text
font = pygame.font.SysFont("Arial", 24)



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
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)  #96, 0 is position of the part we want (top left)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

#######################################################
    
##################### CLASSES #########################


class Player(pygame.sprite.Sprite): #inheriting from sprite for pixel accurate collision (use their methods)
    COLOR = (255, 0, 0)
    GRAVITY = 1

    SPRITES = load_sprite_sheets("MainCharacters", "Cat", 32, 32, True)
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
        self.lives = 2
        self.bullets = 5

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

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self): #update rectangle according to sprite
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)  #sprite uses mask

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

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
            self.x_vel = 4
        elif dx < -19:
            self.direction = "left"
            self.x_vel = -4
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

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  #srcalpha supports transparent images?
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

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

class Heart(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "heart")
        self.heart = load_sprite_sheets("Items", "Lives", 16, 16)
        self.image = self.heart["heart"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = x
        self.y = y
        self.animation_count = 0
        self.animation_name = "heart"


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

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)


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
                #reset player position
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

########################################################

def draw(window, player, objects, offset_x, police, bullets, collectibles):
    #draw background
    window.blit(BG_IMG, (0,0)) #position 0,0 (top left)

    # create text for lives
    lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
    window.blit(lives_text, (10, 10))

    for obj in objects:
        obj.draw(window, offset_x)
    
    for bullet in bullets:
        bullet.draw(window, offset_x)

    for collectible in collectibles:
        collectible.draw(window, offset_x)

    player.draw(window, offset_x)
    police.draw(window, offset_x)

    pygame.display.update()


def main_menu(window):
    while True:
        window.blit(BG_IMG, (0,0))
        instruction_image = pygame.image.load("keys.png")
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
                main(window)
        
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
        clock.tick(FPS)


def main(window): 
    
    block_size = 96

    #instantiate objects
    player = Player(block_size * 3, WIN_HEIGHT - block_size * 4, 50, 50)
    police = Police(-200, 500, 50, 50)
    #weapons
    bullets = []
    #collectibles
    heart1 = Heart(block_size * 3, WIN_HEIGHT - block_size * 5, 16, 16)
    heart2 = Heart(block_size * 5, WIN_HEIGHT - block_size * 5, 16, 16)
    collectibles = [heart1, heart2]
    #blocks and traps
    fire = Fire(700, WIN_HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, WIN_HEIGHT - block_size, block_size) for i in range(-WIN_WIDTH // block_size, (WIN_WIDTH * 2)// block_size)]
    objects = [*floor, Block(0, WIN_HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, WIN_HEIGHT - block_size * 4, block_size),
               Block(block_size * 4, WIN_HEIGHT - block_size * 4, block_size),
               Block(block_size * 5, WIN_HEIGHT - block_size * 4, block_size),
               Block(block_size * 6, WIN_HEIGHT - block_size * 4, block_size),
               fire]
    
    

    offset_x = 0
    scroll_area_width = 320
    run = True

    while run:
        clock.tick(FPS) #running 60 frame/second
        if player.lives <= 0:
          # game over
          if game_over(window):
            main(window)
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
                # match collectible.name:
                #     case "heart":
                #         player.lives += 1
                

        player.loop(FPS)
        police.loop(FPS, player)
        fire.loop()
        
        handle_move(player, objects)
        collided_bullet = handle_police_move(police, objects, player, bullets)
        #make bullet disappear after collision
        if collided_bullet:
            bullets.remove(collided_bullet)
        draw(window, player, objects, offset_x, police, bullets, collectibles)

        if ((player.rect.right - offset_x >= WIN_WIDTH - scroll_area_width) and player.x_vel > 0) or (#moving to the right, off the screen
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0): #moving to the left, off the screen
            offset_x += player.x_vel

    pygame.quit()
    quit()

# if __name__ == "__main__":
#     main(window)
main_menu(window)