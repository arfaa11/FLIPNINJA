import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Load sprite images
sprite_images = [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]

# Create flipped versions for gravity flip
sprite_images_flipped = [pygame.transform.flip(img, False, True) for img in sprite_images]

# Scale factor for the sprite
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
obstacle_speed = -4
obstacles = []

# Score properties
score = 0
font = pygame.font.SysFont(None, 36)

# Animation timing
animation_time = 20  # Time (in milliseconds) between frames
last_update = pygame.time.get_ticks()

# Load static background images
sky_image = pygame.image.load('Assets/Background/sky.png')
rocks_image = pygame.image.load('Assets/Background/rocks.png')

# Load moving background images and duplicate for looping effect
cloudsBack_image = pygame.image.load('Assets/Background/cloudsBack.png')
cloudsFront_image = pygame.image.load('Assets/Background/cloudsFront.png')
ground_image = pygame.image.load('Assets/Background/ground.png')

# Initial positions for moving backgrounds (two instances of each for looping)
cloudsBack_x_positions = [0, SCREEN_WIDTH]
cloudsFront_x_positions = [0, SCREEN_WIDTH]
ground_x_positions = [0, SCREEN_WIDTH]

# Speeds for moving backgrounds
cloudsBack_speed = -10  # pixels per second
cloudsFront_speed = -40  # pixels per second
ground_speed = obstacle_speed  # Same as obstacles

# Time tracking for smooth animation
last_time = pygame.time.get_ticks()

# Main game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - last_time) / 1000  # Convert milliseconds to seconds
    last_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gravity_flipped = not gravity_flipped
                player_acc[1] = -player_acc[1]
                sprite_images = sprite_images_flipped if gravity_flipped else [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]
                sprite_images_flipped = [pygame.transform.flip(img, False, True) for img in sprite_images]

    # Update the sprite animation
    now = pygame.time.get_ticks()
    if now - last_update > animation_time:
        last_update = now
        current_sprite = (current_sprite + 1) % len(sprite_images)
        sprite_image = pygame.transform.scale(sprite_images[current_sprite], (scaled_sprite_width, scaled_sprite_height))
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

    # Update positions of moving backgrounds based on elapsed time
    cloudsBack_x_positions = [(x + cloudsBack_speed * elapsed_time) % SCREEN_WIDTH for x in cloudsBack_x_positions]
    cloudsFront_x_positions = [(x + cloudsFront_speed * elapsed_time) % SCREEN_WIDTH for x in cloudsFront_x_positions]
    ground_x_positions = [(x + ground_speed * elapsed_time) % SCREEN_WIDTH for x in ground_x_positions]

    # Update obstacles
    if not obstacles or obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
        obstacle_height = random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.6))
        obstacles.append({'x': SCREEN_WIDTH, 'y': 0, 'height': obstacle_height})
        obstacles.append({'x': SCREEN_WIDTH, 'y': obstacle_height + obstacle_gap, 'height': SCREEN_HEIGHT - (obstacle_height + obstacle_gap)})

    obstacles = [{'x': obstacle['x'] + obstacle_speed, 'y': obstacle['y'], 'height': obstacle['height'], 'scored': obstacle.get('scored', False)} for obstacle in obstacles]

    # Remove off-screen obstacles and score
    obstacles = [obstacle for obstacle in obstacles if obstacle['x'] + obstacle_width > 0]
    for obstacle in obstacles:
        if sprite_rect.right > obstacle['x'] + obstacle_width and not obstacle.get('scored', False):
            score += 1
            obstacle['scored'] = True

    # Drawing
    screen.fill(BLACK)
    screen.blit(sky_image, (0, 0))
    screen.blit(rocks_image, (0, 0))
    for i in range(2):
        screen.blit(cloudsBack_image, (cloudsBack_x_positions[i] - SCREEN_WIDTH * (i == 1), 0))
        screen.blit(cloudsFront_image, (cloudsFront_x_positions[i] - SCREEN_WIDTH * (i == 1), 0))
        screen.blit(ground_image, (ground_x_positions[i] - SCREEN_WIDTH * (i == 1), 0))
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
