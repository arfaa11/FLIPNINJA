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

class BackgroundManager:
    """
    BackgroundManager CLASS TO CONTROL GAME FEATURES RELATED TO THE BACKGROUND IMAGES AND RENDERING
    """
    def __init__(self):
        """
        PURPOSE: DEFINES INITIATION VARIABLES FOR THE BackgroundManager CLASS
        PARAMETER(S): NONE
        RETURN: NONE
        """

        # Load background images for the game from the "Assets/Background folder"
        self.bgImgs = {
            'sky': pygame.image.load('Assets/Background/sky.png').convert_alpha(),
            'cloudsBack': pygame.image.load('Assets/Background/cloudsBack.png').convert_alpha(),
            'cloudsFront': pygame.image.load('Assets/Background/cloudsFront.png').convert_alpha(),
            'ground': pygame.image.load('Assets/Background/ground.png').convert_alpha()
        }

        # Load x positions for the background images
        self.bgXPos = {
            'cloudsBack': [0, SCREEN_WIDTH],
            'cloudsFront': [0, SCREEN_WIDTH],
            'ground': [0, SCREEN_WIDTH]
        }

        # Set movement speeds for the moving background images
        self.bgSpeeds = {
            'cloudsBack': -1 * SCREEN_WIDTH / 60,           # Set back clouds movement speed slower than front clouds                                       
            'cloudsFront': -2 * SCREEN_WIDTH / 60,          # 2x as fast as the back clouds
            'ground': OBSTACLE_SPEED * SCREEN_WIDTH / 60    # Set the ground movement speed to that of the obstacles
        }

    def update(self, elapsedTime):
        """
        PURPOSE: Update the background positions for parallax effect based on elapsed time.
        PARAMETER(S): elapsedTime (float): The time elapsed since the last frame update, used to calculate movement.
        RETURN: None. Modifies the background positions in place.

        """
        
        # Update background positions for a parallax effect
        for key in self.bgXPos.keys():
            # Calculate new position based on speed and elapsed time, wrap around at screen edge
            self.bgXPos[key] = [(x + self.bgSpeeds[key] * elapsedTime) % SCREEN_WIDTH for x in self.bgXPos[key]]

    def draw(self, screen):
        """
        PURPOSE: Draw the backgrounds to the screen, layering them to create a parallax effect.
        PARAMETER(S): screen (pygame.Surface): The main game screen where backgrounds are drawn.
        RETURN: None. Directly draws the backgrounds onto the provided screen surface.

        """

        # Draw the static sky background first
        screen.blit(self.bgImgs['sky'], (0, 0))

        # Loop through and draw each moving background layer
        for key in ['cloudsBack', 'cloudsFront', 'ground']:
            for xPos in self.bgXPos[key]:
                # Draw current background image at its current position
                screen.blit(self.bgImgs[key], (xPos, 0))
                # If part of the image moves off-screen, draw it again on the opposite end
                if xPos < SCREEN_WIDTH:
                    screen.blit(self.bgImgs[key], (xPos - SCREEN_WIDTH, 0))