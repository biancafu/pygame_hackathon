import pygame

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((800, 600))

# Define the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Define the player and chaser rectangles
player_rect = pygame.Rect(100, 100, 50, 50)
chaser_rect = pygame.Rect(300, 300, 50, 50)

# Define the chaser speed
chaser_speed = 1

# Set up the game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the player with arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= 2
    if keys[pygame.K_RIGHT]:
        player_rect.x += 2
    if keys[pygame.K_UP]:
        player_rect.y -= 2
    if keys[pygame.K_DOWN]:
        player_rect.y += 2

    # Move the chaser towards the player
    dx = player_rect.x - chaser_rect.x
    dy = player_rect.y - chaser_rect.y
    dist = (dx ** 2 + dy ** 2) ** 0.5
    if dist != 0:
        dx_norm = dx / dist
        dy_norm = dy / dist
        chaser_rect.x += dx_norm * chaser_speed
        chaser_rect.y += dy_norm * chaser_speed

    # Draw the rectangles on the screen
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, player_rect)
    pygame.draw.rect(screen, RED, chaser_rect)
    pygame.display.flip()

# Quit Pygame
pygame.quit()
