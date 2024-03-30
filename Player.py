"""
AUTHOR: ARFAA MUMTAZ
PROJECT: CMPT 230 GAME
DESCRIPTION: A GAME REVOLVING A NINJA THAT CAN FLIP HIS GRAVITY AND HAS OT NAVIGATE THROUGH OBSTACLES
             IN A JOURNEY TOWARDS SELF-IMPROVEMENT BECAUSE HE IS ALWAYS TRYING TO DO BETTER THAN HE DID
             LAST TIME.
"""

# Import statements
import pygame

# Star imports from other game files
from BackgroundManager import *
from ObstacleManager import *
from Player import *

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080                    # 1920 x 1080 pixels
BLACK, WHITE, RED = (0, 0, 0), (255, 255, 255), (255, 0, 0) # Define basic colors for now
SPRITE_SCALE = 0.06                                         # Set sprite size to 6% of entire screen
MAX_VEL = 5                                                 # Define a max velocity placeholder
OBSTACLE_WIDTH = 111                                        # Set obstacle width to 5% of screen width
OBSTACLE_GAP = SCREEN_HEIGHT * 0.2                          # Set obstacle gap to 20% of screen height
OBSTACLE_SPEED = -4                                         # Move obstacles from right to left at 4px/frame
ANIMATION_TIME = 10                                         # Set the animation time for the player to a total of 10 ms
BUTTON_SIZE = (360, 258)                                    # Set buttons to appropriate size to increase visibility
NUMBER_SIZE = (80, 108)                                     # Size of each number image for score drawing

class Player:
    """
    Player CLASS TO CONTROL PLAYER FEATURES AND FUNCTIONALITY
    """
    def __init__(self):
        """
        PURPOSE: DEFINES VARIABLES AND EVENT FLAGS FOR THE PLAYER COMPONENT
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        # Load running animation images
        self.spriteImgs = [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]
        
        # Create flipped versions for when gravity is inverted
        self.spriteImgsFlipped = [pygame.transform.flip(img, False, True) for img in self.spriteImgs]
        
        # Calculate scaled dimensions for the sprite
        scaledSpriteHeight = int(SCREEN_HEIGHT * SPRITE_SCALE)
        scaledSpriteWidth = int(self.spriteImgs[0].get_width() * scaledSpriteHeight / self.spriteImgs[0].get_height())
        
        # Apply scaling to both sprite sets
        self.spriteImgs = [pygame.transform.scale(img, (scaledSpriteWidth, scaledSpriteHeight)) for img in self.spriteImgs]
        self.spriteImgsFlipped = [pygame.transform.scale(img, (scaledSpriteWidth, scaledSpriteHeight)) for img in self.spriteImgsFlipped]
        
        # Initialize animation state
        self.currSprite = 0
        self.spriteImg = self.spriteImgs[self.currSprite]
        
        # Position the player sprite
        self.spriteRect = self.spriteImg.get_rect(topleft=(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2 - scaledSpriteHeight // 2))
        
        # Initialize velocity and acceleration
        self.playerVel = [0, 0]
        self.playerAcc = [0, 0.5]
        
        # Flag for gravity direction
        self.gravFlipped = False
        
        # Timing for animation updates
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        """
        PURPOSE: Update the player's sprite and position based on gravity and current velocity.
        PARAMETER(S): None. Uses the object's current state to determine updates.
        RETURN: None. Modifies the player's position and sprite index in place.

        """
        
        # Track time for sprite animation frame updates
        now = pygame.time.get_ticks()
        
        if now - self.lastUpdate > ANIMATION_TIME:
            self.lastUpdate = now
        
            # Cycle through sprite images for animation
            self.currSprite = (self.currSprite + 1) % len(self.spriteImgs)
            self.spriteImg = self.spriteImgs[self.currSprite]
        
        # Apply acceleration to velocity
        self.playerVel[1] += self.playerAcc[1]
        
        # Limit velocity to maximum value
        self.playerVel[1] = max(-MAX_VEL, min(MAX_VEL, self.playerVel[1]))
        
        # Update position based on velocity
        self.spriteRect.y += self.playerVel[1]
        
        # Prevent player from moving beyond the screen bounds
        if self.spriteRect.top <= 0:
            self.spriteRect.top = 0
            self.playerVel[1] = 0
        
        elif self.spriteRect.bottom >= SCREEN_HEIGHT:
            self.spriteRect.bottom = SCREEN_HEIGHT
            self.playerVel[1] = 0

    def draw(self, screen):
        """
        PURPOSE: Draw the player's current sprite at its current position.
        PARAMETER(S): screen (pygame.Surface): The main game screen where the player sprite is drawn.
        RETURN: None. Directly draws the player's sprite onto the provided screen surface.

        """
        
        # Draw sprite at current position
        screen.blit(self.spriteImg, self.spriteRect)

    def flipGravity(self):
        """
        PURPOSE: Invert the player's gravity, affecting its acceleration and flipping the sprite orientation.
        PARAMETER(S): None. Toggles the gravity effect and sprite orientation based on the current state.
        RETURN: None. Modifies the player's acceleration and sprite orientation in place.

        """
        
        # Invert gravity direction and update sprite set for animation
        self.gravFlipped = not self.gravFlipped
        self.playerAcc[1] = -self.playerAcc[1]

        # Swap sprite sets to reflect gravity flip
        self.spriteImgs, self.spriteImgsFlipped = self.spriteImgsFlipped, self.spriteImgs
        self.spriteImg = self.spriteImgs[self.currSprite]