"""
AUTHOR: ARFAA MUMTAZ
PROJECT: CMPT 230 GAME
DESCRIPTION: A GAME REVOLVING A NINJA THAT CAN FLIP HIS GRAVITY AND HAS OT NAVIGATE THROUGH OBSTACLES
             IN A JOURNEY TOWARDS SELF-IMPROVEMENT BECAUSE HE IS ALWAYS TRYING TO DO BETTER THAN HE DID
             LAST TIME.
"""

# Import statements
import pygame
import random

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

class ObstacleManager:
    
    def __init__(self):
    
        self.obstacles = []  # List to hold obstacles
        self.obstacleID = 0  # Unique ID for each obstacle pair
    
        # Load the obstacle image (tree) from assets
        self.original_img = pygame.image.load('Assets/Background/treeObstacle.png').convert_alpha()
        self.obstacle_gap = OBSTACLE_GAP  # Vertical space between top and bottom obstacles

    def addObstacle(self):
        """
        PURPOSE: Add a new obstacle at a random position to the game, managing top and bottom obstacles.
        PARAMETER(S): None. Generates obstacles and their positions based on predefined settings.
        RETURN: None. Adds newly created obstacles to the obstacle list.
        """
        
        # Randomly set the gap's start position
        gap_top = random.randint(int(SCREEN_HEIGHT * 0.2), int(SCREEN_HEIGHT * 0.8 - self.obstacle_gap))
        gap_bottom = gap_top + self.obstacle_gap
        
        # Flip the top obstacle image for visual consistency
        top_obstacle_img = pygame.transform.flip(self.original_img, False, True)
        top_obstacle_y = gap_top - top_obstacle_img.get_height()
        
        # Bottom obstacle uses the original image
        bottom_obstacle_img = self.original_img
        bottom_obstacle_y = gap_bottom
        
        # Add both obstacles to the list with a unique ID and a passed flag
        self.obstacles.append({'x': SCREEN_WIDTH, 'y': top_obstacle_y, 'img': top_obstacle_img, 'id': self.obstacleID, 'passed': False})
        self.obstacles.append({'x': SCREEN_WIDTH, 'y': bottom_obstacle_y, 'img': bottom_obstacle_img, 'id': self.obstacleID, 'passed': False})
        self.obstacleID += 1  # Increment ID for the next pair

    def update(self):
        """
        PURPOSE: Update the position of all obstacles, moving them across the screen, and add new obstacles as necessary.
        PARAMETER(S): None. Utilizes current obstacle positions and game settings to update state.
        RETURN: None. Updates obstacles' positions and possibly adds new obstacles.
        """
        # Add new obstacles if needed
        if not self.obstacles or self.obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
            self.addObstacle()

        # Move obstacles to the left
        for obstacle in self.obstacles:
            obstacle['x'] += OBSTACLE_SPEED

        # Remove obstacles that have moved out of the frame
        self.obstacles = [ob for ob in self.obstacles if ob['x'] + OBSTACLE_WIDTH > 0]

    def draw(self, screen):
        """
        PURPOSE: Draw all obstacles on the screen at their current positions.
        PARAMETER(S): screen (pygame.Surface): The main game screen where obstacles are drawn.
        RETURN: None. Directly draws all obstacles onto the provided screen surface.
        """
        
        # Draw all obstacles on the screen
        for obstacle in self.obstacles:
            screen.blit(obstacle['img'], (obstacle['x'], obstacle['y']))

    def checkCollision(self, playerRect):
        """
        PURPOSE: Check if the player has collided with any of the obstacles.
        PARAMETER(S): playerRect (pygame.Rect): The bounding rectangle of the player's sprite for collision detection.
        RETURN: Boolean. Returns True if a collision is detected, False otherwise.
        """
    
        # Check for collisions between the player and any obstacle
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], OBSTACLE_WIDTH, obstacle['img'].get_height())
         
            if playerRect.colliderect(obstacle_rect):
                return True  # Collision detected
        
        return False  # No collision

    def updateScore(self, playerRect, score):
        """
        PURPOSE: Update the game score based on obstacles passed by the player.
        PARAMETER(S): playerRect (pygame.Rect): The bounding rectangle of the player's sprite for scoring checks.
                      score (int): The current score of the game.
        RETURN: int. Returns the updated score after checking passed obstacles.
        """
        
        # Increment score if the player passes an obstacle without colliding
        for obstacle in self.obstacles:
            if not obstacle['passed'] and playerRect.right > obstacle['x'] + OBSTACLE_WIDTH:
                obstacle['passed'] = True
        
                # Ensure both top and bottom parts of the obstacle were passed
                if all(o['passed'] for o in self.obstacles if o['id'] == obstacle['id']):
                    score += 1  # Increase score
        
        return score  # Return the updated score