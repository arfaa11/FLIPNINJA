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

# Load and scale sprite images
sprite_images = [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]
sprite_images_flipped = [pygame.transform.flip(img, False, True) for img in sprite_images]

# Scale factor for the sprite
sprite_scale = 0.06
scaled_sprite_height = int(SCREEN_HEIGHT * sprite_scale)
scaled_sprite_width = int(sprite_images[0].get_width() * scaled_sprite_height / sprite_images[0].get_height())
sprite_images = [pygame.transform.scale(img, (scaled_sprite_width, scaled_sprite_height)) for img in sprite_images]
sprite_images_flipped = [pygame.transform.scale(img, (scaled_sprite_width, scaled_sprite_height)) for img in sprite_images_flipped]

# Initial sprite settings
current_sprite = 0
sprite_image = sprite_images[current_sprite]  # Default to non-flipped images
sprite_rect = sprite_image.get_rect(topleft=(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2 - scaled_sprite_height // 2))

# Player physics properties
player_vel = [0, 0]
player_acc = [0, 0.35]  # Adjusted for noticeable effect
gravity_flipped = False
max_vel = 5  # Max vertical velocity

# Obstacle properties
obstacle_width = int(SCREEN_WIDTH * 0.05)
obstacle_gap = SCREEN_HEIGHT * 0.2
obstacle_speed = -4
obstacles = []
obstacle_id = 0  # Unique identifier for obstacle pairs

# Score properties
score = 0
font = pygame.font.SysFont(None, 36)

# Animation timing
animation_time = 10 # Time (in milliseconds) between frames
last_update = pygame.time.get_ticks()

# Load and scale static background images
background_images = {
    'sky': pygame.image.load('Assets/Background/sky.png').convert_alpha(),
    'cloudsBack': pygame.image.load('Assets/Background/cloudsBack.png').convert_alpha(),
    'cloudsFront': pygame.image.load('Assets/Background/cloudsFront.png').convert_alpha(),
    'ground': pygame.image.load('Assets/Background/ground.png').convert_alpha()
}

# Initial positions for moving backgrounds (two instances of each for looping)
background_x_positions = {
    'cloudsBack': [0, SCREEN_WIDTH],
    'cloudsFront': [0, SCREEN_WIDTH],
    'ground': [0, SCREEN_WIDTH]
}

# Speeds for moving backgrounds
background_speeds = {
    'cloudsBack': -1 * SCREEN_WIDTH / 60,
    'cloudsFront': -2 * SCREEN_WIDTH / 60,
    'ground': obstacle_speed * SCREEN_WIDTH / 60
}

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    elapsed_time = clock.get_time() / 1000  # Convert milliseconds to seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gravity_flipped = not gravity_flipped
                player_acc[1] = -player_acc[1]
                sprite_images, sprite_images_flipped = sprite_images_flipped, sprite_images  # Swap lists
                sprite_image = sprite_images[current_sprite]  # Ensure sprite image updates immediately

    # Update sprite animation
    now = pygame.time.get_ticks()
    if now - last_update > animation_time:
        last_update = now
        current_sprite = (current_sprite + 1) % len(sprite_images)
        sprite_image = sprite_images[current_sprite]

    # Player physics
    player_vel[1] += player_acc[1]
    player_vel[1] = max(-max_vel, min(max_vel, player_vel[1]))
    sprite_rect.y += player_vel[1]

    # Prevent sprite from going out of bounds
    if sprite_rect.top <= 0:
        sprite_rect.top = 0
        player_vel[1] = 0
    elif sprite_rect.bottom >= SCREEN_HEIGHT:
        sprite_rect.bottom = SCREEN_HEIGHT
        player_vel[1] = 0

    # Update and loop backgrounds
    for key in background_x_positions.keys():
        background_x_positions[key] = [(x + background_speeds[key] * elapsed_time) % SCREEN_WIDTH for x in background_x_positions[key]]

    # Obstacle creation and management
    if not obstacles or obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
        obstacle_height = random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.6))
        obstacles.append({'x': SCREEN_WIDTH, 'y': 0, 'height': obstacle_height, 'id': obstacle_id, 'passed': False})
        obstacles.append({'x': SCREEN_WIDTH, 'y': obstacle_height + obstacle_gap, 'height': SCREEN_HEIGHT - (obstacle_height + obstacle_gap), 'id': obstacle_id, 'passed': False})
        obstacle_id += 1

    obstacles = [{'x': obstacle['x'] + obstacle_speed, 'y': obstacle['y'], 'height': obstacle['height'], 'id': obstacle['id'], 'passed': obstacle['passed']} for obstacle in obstacles]

    # Remove off-screen obstacles and update score
    obstacles = [obstacle for obstacle in obstacles if obstacle['x'] + obstacle_width > 0]
    for obstacle in obstacles:
        if sprite_rect.right > obstacle['x'] + obstacle_width and not obstacle['passed']:
            obstacle['passed'] = True
            # Check if both obstacles of the pair have been passed
            pair_passed = all(ob['passed'] for ob in obstacles if ob['id'] == obstacle['id'])
            if pair_passed:
                # Increment score only once per obstacle pair
                score += 1
                # Prevent future score increment for this pair
                for ob in obstacles:
                    if ob['id'] == obstacle['id']:
                        ob['passed'] = True

    # Drawing
    screen.fill(BLACK)
    screen.blit(background_images['sky'], (0, 0))
    for key in ['cloudsBack', 'cloudsFront', 'ground']:
        for x_position in background_x_positions[key]:
            screen.blit(background_images[key], (x_position, 0))
            if x_position < SCREEN_WIDTH:
                screen.blit(background_images[key], (x_position - SCREEN_WIDTH, 0))
    screen.blit(sprite_image, sprite_rect)
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, (obstacle['x'], obstacle['y'], obstacle_width, obstacle['height']))

    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    # Collision detection
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], obstacle_width, obstacle['height'])
        if sprite_rect.colliderect(obstacle_rect):
            running = False
            print("Game Over!")
            break

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
