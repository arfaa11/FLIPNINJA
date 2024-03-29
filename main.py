"""
AUTHOR: ARFAA MUMTAZ
PROJECT: CMPT 230 GAME
DESCRIPTION: A GAME REVOLVING A NINJA THAT CAN FLIP HIS GRAVITY AND HAS OT NAVIGATE THROUGH OBSTACLES
             IN A JOURNEY TOWARDS SELF-IMPROVEMENT BECAUSE HE IS ALWAYS TRYING TO DO BETTER THAN HE DID
             LAST TIME.
"""

# Import statements
import pygame
import sys
import random
import math
import json
import os

# Initialize pygame and some mixer settings
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(1)  

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


class Game:
    
    def __init__(self):
        """
        PURPOSE: Initialize the game, setting up the screen, game elements, and state flags.
        PARAMETER(S): None. Sets up the game environment using predefined settings and assets.
        RETURN: None. Constructs a Game object with initialized properties.
        """
        
        # Set display with given size
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Start clock
        self.clock = pygame.time.Clock()

        # Initialize game state flags
        self.running = True # Flag to toggle running state
        self.inStartMenu = True # Flag to set start menu UI
        self.inSettings = False  # Flag to toggle settings UI
        self.inGame = False # Flag to toggle gameplay
        self.showGameOverScreen = False # Flag to toggle game over screen

        # Call other classes' instances
        self.player = Player() 
        self.obstacleMngr = ObstacleManager()
        self.bgMngr = BackgroundManager()
        
        # Initialize score as 0
        self.score = 0
        
        # Set main UI font
        self.font = pygame.font.SysFont('firacodenerdfontpropomed', 28)

        # Load buttons to be displayed
        self.loadButtons()

        # Animation phases for buttons
        self.startButtonAnimPhase = 0
        self.homeButtonAnimPhase = 0
        self.settingsButtonAnimPhase = 0
        self.retryButtonAnimPhase = 0

        # Set up logic for score tracking and displaying
        self.numberImgs = self.loadNumberImages()
        self.scoreRecordsPath = 'Extras/scoreRecords.json' # Store scores in json file
        self.bestScore = self.getBestScore()

        # Initialize and set up all in game music and sound effects
        self.playMenuMusic()  # Play menu music when the game object is initialized
        self.hoverSound = pygame.mixer.Sound('Assets/Music/hover.wav')  # Load hover sound
        self.selectSound = pygame.mixer.Sound('Assets/Music/select.wav')  # Load select sound
        self.deathSound = pygame.mixer.Sound('Assets/Music/death.wav')  # Load the death sound
        self.pointSound = pygame.mixer.Sound('Assets/Music/point.wav')
        self.isMuted = False  # Mute state
        self.hoverSoundPlayed = False  # Flag to track if the hover sound has been played
        self.selectSoundPlayed = False # Flag to track if select sound has been played
        self.gameMusicStarted = False  # Flag to track if game music has been started
        self.backHoverSoundPlayed = False # Flag to track if back hover sound has been played
        self.volumeSliderRects = []
        self.volume = 0.5  # Default volume level
        self.muteButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/muteButton.png').convert_alpha(), (100, 100))
        self.unmuteButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/unmuteButton.png').convert_alpha(), (100, 100))
        self.volumeButtonImg = self.unmuteButtonImg  # Start with unmute image
        self.volumeButtonRect = self.unmuteButtonImg.get_rect(topright=(SCREEN_WIDTH - 100, 350))
        self.initVolumeSlider()
        self.volumeTextFont = pygame.font.SysFont('firacodenerdfontpropomed', 36) 
        self.volumeText = self.volumeTextFont.render('Game Volume', True, WHITE)

        # Set up logic to display home and back buttons
        self.homeButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/homeButton.png').convert_alpha(), (BUTTON_SIZE[0]/1.5, BUTTON_SIZE[1]/1.5))
        self.homeButtonRect = self.homeButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + BUTTON_SIZE[1] * 1.5))
        self.backButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/backButton.png').convert_alpha(), (BUTTON_SIZE[0]/2.5, BUTTON_SIZE[1]/2.5)) 
        self.backButtonRect = self.backButtonImg.get_rect(topleft=(10, 10))  # Position it at the top left

        # Logic to display trophies on game over screen when high score beat
        self.trophyImg = pygame.image.load('Assets/Buttons/trophy.png').convert_alpha()
        self.trophyImg = pygame.transform.scale(self.trophyImg, (100, 100))

        # Flag to track score recording to prevent duplicate score entries
        self.scoreRecorded = False 


    def loadNumberImages(self):
        """
        PURPOSE: Load and scale number images used for score display.
        PARAMETER(S): None. Loads images from predefined file paths.
        RETURN: List[pygame.Surface]. Returns a list of loaded and scaled number images.
        """
        
        # Load images for numbers 0-9 for score display.
        numberPaths = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        
        return [pygame.transform.scale(pygame.image.load(f'Assets/Numbers/{name}.png').convert_alpha(), NUMBER_SIZE) for name in numberPaths]

    def loadButtons(self):
        """
        PURPOSE: Load and scale button images used in the game menus.
        PARAMETER(S): None. Loads images from predefined file paths.
        RETURN: None. Initializes button images and their bounding rectangles.
        """
        
        # Load and scale images for UI buttons.
        self.startButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/startButton.png').convert_alpha(), BUTTON_SIZE)
        self.settingsButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/settingsButton.png').convert_alpha(), BUTTON_SIZE)
        self.retryButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/retryButton.png').convert_alpha(), BUTTON_SIZE)
        
        # Define button positions.
        self.startButtonRect = self.startButtonImg.get_rect(center=(SCREEN_WIDTH/2 - BUTTON_SIZE[0]/2 - 45, SCREEN_HEIGHT/2))
        self.settingsButtonRect = self.settingsButtonImg.get_rect(center=(SCREEN_WIDTH/2 + BUTTON_SIZE[0]/2 + 45, SCREEN_HEIGHT/2))
        self.retryButtonRect = self.retryButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))

    def updateScoreRecord(self, currentScore):
        """
        PURPOSE: Update the file containing the score records with the current game session score.
        PARAMETER(S): currentScore (int): The score achieved in the current game session.
        RETURN: None. Updates or creates the score record file with the new score.
        """
        
        try:
        
            # Save the current game score to a file.
            if not os.path.exists('Extras'):
                os.makedirs('Extras')  # Ensure the directory exists.
            
            if os.path.exists(self.scoreRecordsPath):
                with open(self.scoreRecordsPath, 'r') as file:
                    scores = json.load(file)  # Load existing scores.
            
            else:
                scores = []  # Start a new score list if the file doesn't exist.
            
            scores.append(currentScore)  # Add the current score.
            
            # Write the updated scores back to the file.
            with open(self.scoreRecordsPath, 'w') as file:
                json.dump(scores, file)
        
        # Error message if unsuccessful
        except Exception as e:
            print(f"Error updating score record: {e}")

    def getBestScore(self):
        """
        PURPOSE: Retrieve the highest score from the score records.
        PARAMETER(S): None. Reads the score record file if it exists.
        RETURN: int. Returns the highest score recorded; returns 0 if no records exist.
        """

        try:
        
            # Load the highest score from the score records file.
            if os.path.exists(self.scoreRecordsPath):
                with open(self.scoreRecordsPath, 'r') as file:
                    scores = json.load(file)
    
                return max(scores)  # Return the highest score.
    
            return 0  # Return 0 if no scores are recorded yet.
        
        except Exception as e:
            print(f"Error reading best score: {e}")
        
            return 0

    def drawAnimatedScore(self, score, yPosition, animationPhase):
        """
        PURPOSE: Draw the current score with animation effects.
        PARAMETER(S): score (int): The current score to display.
                      yPosition (int): The vertical position on the screen to draw the score.
                      animationPhase (float): The phase of the animation for dynamic effect.
        RETURN: None. Draws the animated score on the screen.
        """
        
        # Draw the current score with an animation effect.
        scoreStr = str(score)  # Convert score to string for individual digit processing.
        totalWidth = NUMBER_SIZE[0] * len(scoreStr)  # Calculate total width needed for the score.
        startX = SCREEN_WIDTH / 2 - totalWidth / 2  # Calculate starting X position.

        # Calculate scale factor for animation effect.
        scaleFactor = 1.05 + 0.05 * math.sin(animationPhase)

        for i, digit in enumerate(scoreStr):
            # Scale each digit image.
            animSize = (int(NUMBER_SIZE[0] * scaleFactor), int(NUMBER_SIZE[1] * scaleFactor))
            animImg = pygame.transform.scale(self.numberImgs[int(digit)], animSize)
            animRect = animImg.get_rect(center=(startX + i * NUMBER_SIZE[0] + NUMBER_SIZE[0] // 2, yPosition))
            self.screen.blit(animImg, animRect)  # Draw animated digit.

    def runGameOverScreen(self):
        """
        PURPOSE: Display the game over screen, including options to retry or return to the main menu, and shows the final score and best score.
        PARAMETER(S): None. Uses the game's current state and score information.
        RETURN: None. Handles user input and transitions between game states based on selection.
        """
    
        self.screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()

        s = pygame.Surface((800, 600), pygame.SRCALPHA)   # Semi-transparent overlay
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (SCREEN_WIDTH / 2 - 400, SCREEN_HEIGHT / 2 - 300))

        # Determine if a new high score has been set
        if self.score >= self.bestScore:
            self.bestScore = self.score
            message = "NEW HIGH SCORE!"
            color = (0, 255, 0)  # Gold color for the high score message
            
        else:
            message = "You Died!"
            color = RED

        font = pygame.font.SysFont("firacodenerdfontpropomed", 78)
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 400))
        self.screen.blit(text, text_rect)

        # Display trophies on both sides of the message if a new high score has been set
        if self.score >= self.bestScore:
            trophy_left_rect = self.trophyImg.get_rect(midright=(text_rect.left - 20, text_rect.centery))
            trophy_right_rect = self.trophyImg.get_rect(midleft=(text_rect.right + 20, text_rect.centery))
            self.screen.blit(self.trophyImg, trophy_left_rect)
            self.screen.blit(self.trophyImg, trophy_right_rect)

        homeButtonYOffset = self.retryButtonRect.bottom + 50  # 50 pixels below the retry button

        # Logic for animating and positioning the retry button
        if self.retryButtonRect.collidepoint((mx, my)):

            if not self.hoverSoundPlayed:
                self.hoverSound.play()
                self.hoverSoundPlayed = True

            self.screen.blit(self.retryButtonImg, self.retryButtonRect)
        
        elif self.homeButtonRect.collidepoint((mx, my)):

            if not self.hoverSoundPlayed:
                self.hoverSound.play()
                self.hoverSoundPlayed = True

            self.screen.blit(self.homeButtonImg, self.homeButtonRect.move(0, homeButtonYOffset - self.homeButtonRect.top))
        
        else:
            scaleFactorRetry = 1.15 + 0.10 * math.sin(self.retryButtonAnimPhase)
            animButtonRetry = pygame.transform.scale(self.retryButtonImg, (int(BUTTON_SIZE[0] * scaleFactorRetry), int(BUTTON_SIZE[1] * scaleFactorRetry)))
            animRectRetry = animButtonRetry.get_rect(center=self.retryButtonRect.center)

            self.screen.blit(animButtonRetry, animRectRetry)
            self.retryButtonAnimPhase += 0.015
            self.hoverSoundPlayed = False  # Reset flag when not hovering
    
            scaleFactorHome = 1.05 + 0.05 * math.sin(self.homeButtonAnimPhase)  # Smaller scale factor for home button
            animButtonHome = pygame.transform.scale(self.homeButtonImg, (int(self.homeButtonImg.get_width() * scaleFactorHome), int(self.homeButtonImg.get_height() * scaleFactorHome)))
            animRectHome = animButtonHome.get_rect(center=(self.homeButtonRect.centerx, homeButtonYOffset + self.homeButtonImg.get_height() / 2))

            self.screen.blit(animButtonHome, animRectHome)
            self.homeButtonAnimPhase += 0.015

        # Display the animated score on the game over screen.
        self.drawAnimatedScore(self.score, SCREEN_HEIGHT / 2 - 250, self.retryButtonAnimPhase - 1)

        # Display the best score text.
        bestScoreStr = f"Best Score: {self.bestScore}"
        bestScoreText = self.font.render(bestScoreStr, True, WHITE)
       
        self.screen.blit(bestScoreText, (SCREEN_WIDTH / 2 - bestScoreText.get_width() / 2, SCREEN_HEIGHT / 2 - 150))

        # Handle user input on the game over screen.
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False
                self.showGameOverScreen = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if self.retryButtonRect.collidepoint((mx, my)):
                    self.selectSound.play()
                    self.restartGame()  # Restart the game when retry is clicked.

                    self.inGame = True
                    self.inStartMenu = False

                    self.playGameMusic()  # Play the game music again.

                elif self.homeButtonRect.collidepoint((mx, my)):
                    self.selectSound.play()
                    self.restartGame()  # Go back to the start menu when home is clicked.

                    self.gameMusicStarted = False
                    self.showGameOverScreen = False
                    self.inStartMenu = True
                    self.inGame = False

                    self.playMenuMusic()  # Play the menu music.

        pygame.display.flip()  # Update the full display Surface to the screen.

    def restartGame(self):
        """
        PURPOSE: Reset the game to its initial state, ready for a new session.
        PARAMETER(S): None. Resets game elements and score.
        RETURN: None. Prepares the game for a new session without exiting to the menu.
        """
        
        # Reset the game for a new play session.
        self.player = Player()  # Reset player.
        self.obstacleMngr = ObstacleManager()  # Reset obstacles.
        self.score = 0  # Reset score.
        
        self.showGameOverScreen = False
        self.inStartMenu = False
        self.inGame = True
        self.scoreRecorded = False  # Allow score recording for the new session.
        
        if self.inGame == True:
            self.playGameMusic()  # Play game music.
            self.gameMusicStarted = True  # Prevent future calls.


    def playMenuMusic(self):
        """
        PURPOSE: Load and play background music for the menu.
        PARAMETER(S): None. Selects and plays specified music tracks.
        RETURN: None. Starts playing the selected background music loop.
        """
        
        pygame.mixer.music.load('Assets/Music/menuMusic.wav')  # Load the menu music
        pygame.mixer.music.play(-1)  # Play the music in a loop
    
    def playGameMusic(self):
        """
        PURPOSE: Load and play background music for the game session.
        PARAMETER(S): None. Selects and plays specified music tracks.
        RETURN: None. Starts playing the selected background music loop.
        """
        
        pygame.mixer.music.load('Assets/Music/gameMusic.wav')  # Load the menu music
        pygame.mixer.music.play(-1)  # Play the music in a loop 
    
    def toggleMute(self):
        """
        PURPOSE: Toggle the game's mute state, adjusting volume and updating the mute button image.
        PARAMETER(S): None. Changes the volume to 0 or restores it based on the current state.
        RETURN: None. Modifies the game's volume and updates the mute button's appearance.
        """
        
        # Toggle the mute state of the game.
        if self.volume > 0:
            self.volume = 0  # Mute the game.
            self.volumeButtonImg = self.muteButtonImg
       
        else:
            self.volume = 0.5  # Unmute the game and set volume to 50%.
            self.volumeButtonImg = self.unmuteButtonImg
       
        pygame.mixer.music.set_volume(self.volume)  # Apply the volume change.

    def initVolumeSlider(self):
        """
        PURPOSE: Initialize the graphical representation and functionality of the volume slider in the settings menu.
        PARAMETER(S): None. Sets up the positions and sizes of volume slider components.
        RETURN: None. Creates volume slider rectangles and assigns them to a list.
        """
        
        # Initialize the volume slider for the settings menu.
        sliderXStart = self.volumeButtonRect.right - 1450  # Position starting X.
        sliderY = self.volumeButtonRect.bottom - 75  # Position Y aligned with mute button.
        rectWidth, rectHeight = 120, self.volumeButtonRect.height / 2  # Slider dimensions.
        spacing = 10  # Space between slider segments.

        # Load slider images.
        self.volOnImg = pygame.image.load('Assets/Buttons/volOn.png').convert_alpha()
        self.volOffImg = pygame.image.load('Assets/Buttons/volOff.png').convert_alpha()

        # Create slider segments.
        for i in range(10):
            x = sliderXStart + i * (rectWidth + spacing)
            rect = pygame.Rect(x, sliderY, rectWidth, rectHeight)
            self.volumeSliderRects.append(rect)  # Add segment to the list.


    def drawVolumeSlider(self):
        """
        PURPOSE: Draw the volume slider and its current level on the settings screen.
        PARAMETER(S): None. Utilizes the current volume level and slider setup.
        RETURN: None. Draws the slider and its current setting visually on the screen.
        """
        
        # Draw the volume slider and highlight segments based on the current volume.
        for i, rect in enumerate(self.volumeSliderRects):
            if i < self.volume * 10:
                self.screen.blit(pygame.transform.scale(self.volOnImg, (rect.width, rect.height)), (rect.x, rect.y))
            
            else:
                self.screen.blit(pygame.transform.scale(self.volOffImg, (rect.width, rect.height)), (rect.x, rect.y))

    def drawSettingsUI(self):
        """
        PURPOSE: Draw and manage the settings UI, allowing the user to adjust volume and access other settings.
        PARAMETER(S): None. Handles user input and visual representation of settings.
        RETURN: None. Updates the game's settings based on user interactions.
        """
        
        # Display and manage the settings menu interface.
        while self.inSettings:
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                
                    # Check if a volume slider rectangle is clicked.
                    for i, rect in enumerate(self.volumeSliderRects):
                        if rect.collidepoint(pos):
                            self.setVolume((i + 1) / 10.0)  # Adjust volume based on click.
                
                            break
                
                    # Check if the mute button is clicked.
                    if self.volumeButtonRect.collidepoint(pos):
                        self.toggleMute()
                
                    # Check if the back button is clicked.
                    elif self.backButtonRect.collidepoint(pos):
                        self.selectSound.play()
                        self.inSettings = False
                        self.inStartMenu = True
                
                # Allow exiting settings with ESC key.
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.inSettings = False
                    self.inStartMenu = True

            # Redraw the settings UI.
            self.screen.fill(BLACK)
            mx, my = pygame.mouse.get_pos()
            
            # Highlight the back button on hover.
            if self.backButtonRect.collidepoint((mx, my)):
                if not self.backHoverSoundPlayed:
                    self.hoverSound.play()
                    self.backHoverSoundPlayed = True
            
            else:
                self.backHoverSoundPlayed = False
            self.screen.blit(self.backButtonImg, self.backButtonRect)

            # Draw the "Settings" title.
            settingsFont = pygame.font.SysFont("firacodenerdfontpropomed", 72)
            settingsText = settingsFont.render("Settings", True, WHITE)
            self.screen.blit(settingsText, (self.screen.get_width() / 2 - settingsText.get_width() / 2, 20))

            # Draw the volume text and slider.
            volumeTextPos = (self.volumeSliderRects[0].left - 275, (self.volumeSliderRects[0].centery - self.volumeTextFont.get_height() // 2))
            self.screen.blit(self.volumeText, volumeTextPos)
            self.drawVolumeSlider()
            self.screen.blit(self.volumeButtonImg, self.volumeButtonRect)

            pygame.display.flip()  # Update the full display Surface to the screen.


    def setVolume(self, volume):
        """
        PURPOSE: Adjust the game's volume based on user input from the settings UI.
        PARAMETER(S): volume (float): The new volume level, ranging from 0.0 to 1.0.
        RETURN: None. Updates the game's volume and the mute button's appearance.
        """
        
        # Adjust the game's volume and update the mute button's appearance.
        self.volume = volume
        pygame.mixer.music.set_volume(self.volume)
        
        if volume > 0:
            self.volumeButtonImg = self.unmuteButtonImg
        
        else:
            self.volumeButtonImg = self.muteButtonImg

    def runStartMenu(self):
        """
        PURPOSE: Display the start menu and handle user interactions, including starting the game or accessing settings.
        PARAMETER(S): None. Manages transitions based on user input.
        RETURN: None. Directs the game to the appropriate state based on menu selections.
        """
        
        # Display the start menu and handle interactions.
        self.screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()
        
        if self.inSettings:
            self.drawSettingsUI()
        
        else:
        
            # Handle button hover and click effects for start and settings buttons.
            if self.startButtonRect.collidepoint((mx, my)):
        
                if not self.hoverSoundPlayed:
                    self.hoverSound.play()
                    self.hoverSoundPlayed = True
        
                self.screen.blit(self.startButtonImg, self.startButtonRect)
        
            elif self.settingsButtonRect.collidepoint((mx, my)):
        
                if not self.hoverSoundPlayed:
                    self.hoverSound.play()
                    self.hoverSoundPlayed = True
        
                self.screen.blit(self.settingsButtonImg, self.settingsButtonRect)
        
            else:
                # Animate buttons if not hovered.
                self.hoverSoundPlayed = False
                scaleFactor = 1.10 + 0.05 * math.sin(self.startButtonAnimPhase)
                animButton = pygame.transform.scale(self.startButtonImg, (int(BUTTON_SIZE[0] * scaleFactor), int(BUTTON_SIZE[1] * scaleFactor)))
                animRect = animButton.get_rect(center=self.startButtonRect.center)
                self.screen.blit(animButton, animRect)
                self.startButtonAnimPhase += 0.015

                scaleFactorB = 1.10 + 0.05 * math.sin(self.settingsButtonAnimPhase)
                animButtonB = pygame.transform.scale(self.settingsButtonImg, (int(BUTTON_SIZE[0] * scaleFactorB), int(BUTTON_SIZE[1] * scaleFactorB)))
                animRectB = animButtonB.get_rect(center=self.settingsButtonRect.center)
                self.screen.blit(animButtonB, animRectB)
                self.settingsButtonAnimPhase += 0.015

            # Handle menu interactions.
            for event in pygame.event.get():
        
                if event.type == pygame.QUIT:
                    self.running = False
                    self.inStartMenu = False
        
                elif event.type == pygame.MOUSEBUTTONDOWN:
        
                    if self.startButtonRect.collidepoint((mx, my)):
                        self.selectSound.play()
        
                        if self.getBestScore() == 0:
                            self.runTutorial()  # Show tutorial for new players.
        
                        else:
                            self.inGame = True
                            self.inStartMenu = False
        
                        if not self.gameMusicStarted:
                            self.playGameMusic()  # Start game music.
                            self.gameMusicStarted = True
        
                    elif self.settingsButtonRect.collidepoint((mx, my)):
                        self.selectSound.play()
                        self.selectSoundPlayed = True
                        self.inSettings = True  # Open settings menu.
        
                    else:
                        self.selectSoundPlayed = False

            pygame.display.flip()  # Update the full display Surface to the screen.

    def drawScore(self):
        """
        PURPOSE: Draw the current game score on the screen.
        PARAMETER(S): None. Uses the game's current score to display.
        RETURN: None. Renders the score on the game screen using number images.
        """
        
        # Display the current score on the screen using number images.
        scoreStr = str(self.score)  # Convert score to string.
        totalWidth = NUMBER_SIZE[0] * len(scoreStr)  # Total width needed.
        startX = SCREEN_WIDTH / 2 - totalWidth / 2  # Calculate starting X position.
        
        for i, digit in enumerate(scoreStr):
            self.screen.blit(self.numberImgs[int(digit)], (startX + i * NUMBER_SIZE[0], 10))

    def runTutorial(self):
        """
        PURPOSE: Run a tutorial session for new players, introducing game mechanics like gravity flipping.
        PARAMETER(S): None. Guides the player through initial gameplay concepts.
        RETURN: None. Initiates the game session after the tutorial is completed or skipped.
        """
        
        # Run a tutorial for first-time players.
        tutorialDone = False
        promptShown = False
        
        self.player = Player()  # Reset player.
        self.obstacleMngr = ObstacleManager()  # Reset obstacles.
        
        while not tutorialDone and self.running:
        
            for event in pygame.event.get():
        
                if event.type == pygame.QUIT:
                    self.running = False
                    tutorialDone = True
        
                if event.type == pygame.KEYDOWN:
        
                    if event.key == pygame.K_SPACE:
        
                        if not promptShown:
                            promptShown = True  # Hide prompt after first gravity flip.
                            self.player.flipGravity()
        
                        else:
                            tutorialDone = True  # End tutorial on second space press.
        
                    if event.key == pygame.K_ESCAPE:
                        tutorialDone = True  # Allow exiting the tutorial with ESC.

            self.screen.fill(BLACK)  # Clear screen for drawing.
            self.bgMngr.draw(self.screen)  # Draw the background.
        
            if not promptShown:
                # Display the spacebar prompt for gravity flipping.
                spaceBarImg = pygame.image.load('Assets/Buttons/spaceBar.png').convert_alpha()
                spaceBarImg = pygame.transform.scale(spaceBarImg, (400, 300))
                self.screen.blit(spaceBarImg, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 - 150))
        
            else:
                # Regular gameplay during the tutorial.
                self.player.update()
                self.obstacleMngr.update()
                self.player.draw(self.screen)
                self.obstacleMngr.draw(self.screen)

            pygame.display.flip()  # Update the full display Surface to the screen.
            self.clock.tick(60)  # Limit the frame rate to 60 frames per second.

        self.inGame = True  # Start the main game after the tutorial.
        self.inStartMenu = False

    def run(self):
        """
        PURPOSE: Main game loop that handles updates, drawing, and state transitions.
        PARAMETER(S): None. Coordinates game updates, drawing, and input handling.
        RETURN: None. Maintains the game loop until the game is exited.
        """
        
        # Main game loop.
        while self.running:
        
            if self.inStartMenu:
                self.runStartMenu()  # Display the start menu.
        
            elif self.showGameOverScreen:
                self.runGameOverScreen()  # Display the game over screen.
        
            else:
                elapsedTime = self.clock.get_time() / 1000  # Time since last frame.

                for event in pygame.event.get():
        
                    if event.type == pygame.QUIT:
                        self.running = False
        
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.player.flipGravity()  # Flip gravity on space press.

                # Update game components.
                self.player.update()
                self.bgMngr.update(elapsedTime)
                self.obstacleMngr.update()

                # Update and display the score.
                previous_score = self.score
                self.score = self.obstacleMngr.updateScore(self.player.spriteRect, self.score)
        
                if self.score > previous_score:
                    self.pointSound.play()  # Play sound on score update.

                self.screen.fill(BLACK)  # Clear screen for drawing.
                self.bgMngr.draw(self.screen)  # Draw the background.
                self.player.draw(self.screen)  # Draw the player.
                self.obstacleMngr.draw(self.screen)  # Draw obstacles.

                self.drawScore()  # Display the score.

                pygame.display.flip()  # Update the full display Surface to the screen.

                # Check for collisions and handle game over state.
                if self.obstacleMngr.checkCollision(self.player.spriteRect) or (self.player.spriteRect.top <= 0 or self.player.spriteRect.bottom >= SCREEN_HEIGHT):
        
                    if not self.scoreRecorded:  # Record score once per game session.
                        self.updateScoreRecord(self.score)
                        self.scoreRecorded = True
        
                    self.deathSound.play()  # Play death sound.
                    pygame.mixer.music.stop()  # Stop game music.
                    self.showGameOverScreen = True  # Show game over screen.

                self.clock.tick(60)  # Limit the frame rate to 60 frames per second.

        pygame.quit()  # Quit pygame when the game loop ends.
        sys.exit()  # Exit the program.

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    game = Game()
    game.run()