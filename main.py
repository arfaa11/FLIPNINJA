import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and scaling factors
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Player properties
player_scale_factor = 0.025  # Player size relative to screen height
player_size = int(SCREEN_HEIGHT * player_scale_factor)
player_pos = [SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2]
player_vel = [0, 0]
player_acc = [0, 0.05]  # Reduced gravity for better control
gravity_flipped = False
max_vel = 5  # Max vertical velocity

# Obstacle properties
obstacle_width = int(SCREEN_WIDTH * 0.05)
obstacle_gap = SCREEN_HEIGHT * 0.2
obstacle_speed = -2  # Slower obstacle speed for better playability
obstacles = []

# Score properties
score = 0
font = pygame.font.SysFont(None, 36)  # Adjust font and size as needed

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        # Gravity flip
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gravity_flipped = not gravity_flipped
                player_acc[1] = -player_acc[1] if gravity_flipped else abs(player_acc[1])  # Flip gravity
                player_vel[1] = -player_vel[1] if abs(player_vel[1]) > 1 else -max_vel/2  # Control flip speed
        
        # Adjust for window resize
        if event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.size
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            player_size = int(SCREEN_HEIGHT * player_scale_factor)
            obstacle_gap = SCREEN_HEIGHT * 0.2
    
    # Update obstacles and score
    if not obstacles or obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
        obstacle_height = random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.6))
        obstacles.append({'x': SCREEN_WIDTH + obstacle_width, 'y': 0, 'height': obstacle_height})
        obstacles.append({'x': SCREEN_WIDTH + obstacle_width, 'y': obstacle_height + obstacle_gap, 'height': SCREEN_HEIGHT})

    for obstacle in obstacles:
        obstacle['x'] += obstacle_speed
        if obstacle['x'] + obstacle_width < 0:
            obstacles.remove(obstacle)
        # Increase score when player passes an obstacle
        elif obstacle['x'] + obstacle_width < player_pos[0] and not obstacle.get('scored', False):
            score += 1
            obstacle['scored'] = True  # Mark obstacle as scored to prevent multiple score increments

    # Player movement and speed control
    player_vel[0] += player_acc[0]
    player_vel[1] += player_acc[1]
    player_vel[1] = max(-max_vel, min(max_vel, player_vel[1]))  # Limit velocity
    player_pos[0] += player_vel[0]
    player_pos[1] += player_vel[1]

    # Prevent the player from going out of bounds
    if player_pos[1] >= SCREEN_HEIGHT - player_size:
        player_pos[1] = SCREEN_HEIGHT - player_size
        player_vel[1] = 0
    elif player_pos[1] <= 0:
        player_pos[1] = 0
        player_vel[1] = 0
    
    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (*player_pos, player_size, player_size))
    
    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, (obstacle['x'], obstacle['y'], obstacle_width, obstacle['height']))
    
    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))  # Adjust positioning as needed
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

    # Check for collision
    player_rect = pygame.Rect(*player_pos, player_size, player_size)
    for obstacle in obstacles:
        if player_rect.colliderect(pygame.Rect(obstacle['x'], obstacle['y'], obstacle_width, obstacle['height'])):
            print("Game Over!")
            running = False

pygame.quit()
sys.exit()
