import pygame
import random

# Initialize Pygame
pygame.init()

# Set the window dimensions
win_width = 800
win_height = 600
win = pygame.display.set_mode((win_width, win_height))

# Set the colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# Set the font
font = pygame.font.SysFont(None, 25)

# Define the Collectible class
class Collectible:
    def __init__(self):
        self.size = 20
        self.color = red
        self.x = random.randint(0, win_width - self.size)
        self.y = random.randint(0, win_height - self.size)

    def draw(self):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

# Create a list to hold the collectibles
collectibles = []

# Create the initial collectible
collectibles.append(Collectible())

# Set the game loop
game_running = True
while game_running:
    # Fill the background
    win.fill(white)

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    # Draw the collectibles
    for collectible in collectibles:
        collectible.draw()

    # Draw the score
    score_text = font.render("Score: {}".format(len(collectibles)), True, black)
    win.blit(score_text, (10, 10))

    # Update the display
    pygame.display.update()

    # Check for collisions between the player and the collectibles
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    for collectible in collectibles:
        collectible_rect = pygame.Rect(collectible.x, collectible.y, collectible.size, collectible.size)
        if player_rect.colliderect(collectible_rect):
            collectibles.remove(collectible)
            collectibles.append(Collectible())
