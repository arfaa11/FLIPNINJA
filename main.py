import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Load sprite images
sprite_images = [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]

# Create flipped versions for gravity flip (vertical flip for upside-down effect)
sprite_images_flipped = [pygame.transform.flip(img, False, True) for img in sprite_images]

# Scale factor for the sprite (10% of screen height)
sprite_scale = 0.06   
scaled_sprite_height = int(SCREEN_HEIGHT * sprite_scale)
scaled_sprite_width = int(sprite_images[0].get_width() * scaled_sprite_height / sprite_images[0].get_height())

# Initial sprite settings
current_sprite = 0
sprite_image = pygame.transform.scale(sprite_images[current_sprite], (scaled_sprite_width, scaled_sprite_height))
sprite_rect = sprite_image.get_rect(topleft=(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2 - scaled_sprite_height // 2))

# Player physics properties
player_vel = [0, 0]
player_acc = [0, 0.5]  # Adjusted for noticeable effect
gravity_flipped = False
max_vel = 5  # Max vertical velocity

# Obstacle properties
obstacle_width = int(SCREEN_WIDTH * 0.05)
obstacle_gap = SCREEN_HEIGHT * 0.2
obstacle_speed = -2
obstacles = []

# Score properties
score = 0
font = pygame.font.SysFont(None, 36)

# Animation timing
animation_time = 100  # Time (in milliseconds) between frames
last_update = pygame.time.get_ticks()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Gravity flip and sprite flip
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gravity_flipped = not gravity_flipped
                player_acc[1] = -player_acc[1]
                # Determine which set of images to use based on gravity direction
                sprite_images = sprite_images_flipped if gravity_flipped else [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]
                sprite_images_flipped = [pygame.transform.flip(img, False, True) for img in sprite_images]  # Re-generate flipped images for next flip

    # Update the sprite animation
    now = pygame.time.get_ticks()
    if now - last_update > animation_time:
        last_update = now
        current_sprite = (current_sprite + 1) % len(sprite_images)
        sprite_image = pygame.transform.scale(sprite_images[current_sprite], (scaled_sprite_width, scaled_sprite_height))
        # Ensure the sprite is flipped correctly according to gravity
        sprite_rect.size = sprite_image.get_size()

    # Player physics
    player_vel[1] += player_acc[1]
    player_vel[1] = max(-max_vel, min(max_vel, player_vel[1]))
    sprite_rect.y += player_vel[1]

    # Prevent the sprite from going out of bounds
    if sprite_rect.top <= 0:
        sprite_rect.top = 0
        player_vel[1] = 0
    elif sprite_rect.bottom >= SCREEN_HEIGHT:
        sprite_rect.bottom = SCREEN_HEIGHT
        player_vel[1] = 0

    # Update obstacles
    if not obstacles or obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
        obstacle_height = random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.6))
        obstacles.append({'x': SCREEN_WIDTH + obstacle_width, 'y': 0, 'height': obstacle_height})
        obstacles.append({'x': SCREEN_WIDTH + obstacle_width, 'y': obstacle_height + obstacle_gap, 'height': SCREEN_HEIGHT - (obstacle_height + obstacle_gap)})

    for obstacle in obstacles:
        obstacle['x'] += obstacle_speed
        if obstacle['x'] + obstacle_width < 0:
            obstacles.remove(obstacle)
        elif obstacle['x'] + obstacle_width < sprite_rect.left and not obstacle.get('scored', False):
            score += 1
            obstacle['scored'] = True

    # Drawing
    screen.fill(BLACK)
    screen.blit(sprite_image, sprite_rect)
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, (obstacle['x'], obstacle['y'], obstacle_width, obstacle['height']))
    
    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

    # Check for collision
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], obstacle_width, obstacle['height'])
        if sprite_rect.colliderect(obstacle_rect):
            running = False
            print("Game Over!")
            break

pygame.quit()
sys.exit()
