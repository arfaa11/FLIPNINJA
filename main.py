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
        PURPOSE: 
        PARAMETER(S): elapsedTime: 
        RETURN:
        """
        
        for key in self.bgXPos.keys():
            self.bgXPos[key] = [(x + self.bgSpeeds[key] * elapsedTime) % SCREEN_WIDTH for x in self.bgXPos[key]]

    def draw(self, screen):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """

        screen.blit(self.bgImgs['sky'], (0, 0))

        for key in ['cloudsBack', 'cloudsFront', 'ground']:
            for xPos in self.bgXPos[key]:
                screen.blit(self.bgImgs[key], (xPos, 0))

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
        
        self.spriteImgs = [pygame.image.load(f'Assets/Sprites/ninjaRun{i}.png') for i in range(1, 12)]
        self.spriteImgsFlipped = [pygame.transform.flip(img, False, True) for img in self.spriteImgs]
        scaledSpriteHeight = int(SCREEN_HEIGHT * SPRITE_SCALE)
        scaledSpriteWidth = int(self.spriteImgs[0].get_width() * scaledSpriteHeight / self.spriteImgs[0].get_height())
        self.spriteImgs = [pygame.transform.scale(img, (scaledSpriteWidth, scaledSpriteHeight)) for img in self.spriteImgs]
        self.spriteImgsFlipped = [pygame.transform.scale(img, (scaledSpriteWidth, scaledSpriteHeight)) for img in self.spriteImgsFlipped]
        self.currSprite = 0
        self.spriteImg = self.spriteImgs[self.currSprite]
        self.spriteRect = self.spriteImg.get_rect(topleft=(SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2 - scaledSpriteHeight // 2))
        self.playerVel = [0, 0]
        self.playerAcc = [0, 0.5]
        self.gravFlipped = False
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        """
        PURPOSE: 
        PARAMETER(S):
        RETURN:
        """
        
        now = pygame.time.get_ticks()
        
        if now - self.lastUpdate > ANIMATION_TIME:
            self.lastUpdate = now
            self.currSprite = (self.currSprite + 1) % len(self.spriteImgs)
            self.spriteImg = self.spriteImgs[self.currSprite]
        
        self.playerVel[1] += self.playerAcc[1]
        self.playerVel[1] = max(-MAX_VEL, min(MAX_VEL, self.playerVel[1]))
        self.spriteRect.y += self.playerVel[1]
        
        if self.spriteRect.top <= 0:
            self.spriteRect.top = 0
            self.playerVel[1] = 0
        
        elif self.spriteRect.bottom >= SCREEN_HEIGHT:
            self.spriteRect.bottom = SCREEN_HEIGHT
            self.playerVel[1] = 0

    def draw(self, screen):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        
        screen.blit(self.spriteImg, self.spriteRect)

    def flipGravity(self):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        
        self.gravFlipped = not self.gravFlipped
        self.playerAcc[1] = -self.playerAcc[1]
        self.spriteImgs, self.spriteImgsFlipped = self.spriteImgsFlipped, self.spriteImgs
        self.spriteImg = self.spriteImgs[self.currSprite]

class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.obstacleID = 0
        # Load the obstacle image
        self.original_img = pygame.image.load('Assets/Background/treeObstacle.png').convert_alpha()
        # Note: No need to scale the obstacle image here, since we're keeping their sizes constant
        self.obstacle_gap = OBSTACLE_GAP

    def add_obstacle(self):
        # Decide the gap's vertical starting position randomly within a range, allowing for some of the obstacle to be potentially out of view
        gap_top = random.randint(int(SCREEN_HEIGHT * 0.2), int(SCREEN_HEIGHT * 0.8 - self.obstacle_gap))
        gap_bottom = gap_top + self.obstacle_gap

        # Top obstacle image, flipped vertically
        top_obstacle_img = pygame.transform.flip(self.original_img, False, True)
        # Position the top obstacle's bottom at the gap's top
        top_obstacle_y = gap_top - top_obstacle_img.get_height()

        # Bottom obstacle image
        bottom_obstacle_img = self.original_img
        # Position the bottom obstacle's top at the gap's bottom
        bottom_obstacle_y = gap_bottom

        # Append both top and bottom obstacles to the list with their positions
        self.obstacles.append({'x': SCREEN_WIDTH, 'y': top_obstacle_y, 'img': top_obstacle_img, 'id': self.obstacleID, 'passed': False})
        self.obstacles.append({'x': SCREEN_WIDTH, 'y': bottom_obstacle_y, 'img': bottom_obstacle_img, 'id': self.obstacleID, 'passed': False})
        self.obstacleID += 1

    def update(self):
        # Add new obstacles if needed
        if not self.obstacles or self.obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
            self.add_obstacle()

        # Move obstacles to the left
        for obstacle in self.obstacles:
            obstacle['x'] += OBSTACLE_SPEED

        # Remove obstacles that have moved out of the frame
        self.obstacles = [ob for ob in self.obstacles if ob['x'] + OBSTACLE_WIDTH > 0]

    def draw(self, screen):
        for obstacle in self.obstacles:
            screen.blit(obstacle['img'], (obstacle['x'], obstacle['y']))

    def checkCollision(self, playerRect):
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], OBSTACLE_WIDTH, obstacle['img'].get_height())
            if playerRect.colliderect(obstacle_rect):
                return True
        return False

    def updateScore(self, playerRect, score):
        for obstacle in self.obstacles:
            if not obstacle['passed'] and playerRect.right > obstacle['x'] + OBSTACLE_WIDTH:
                obstacle['passed'] = True
                if all(o['passed'] for o in self.obstacles if o['id'] == obstacle['id']):
                    score += 1
        return score

class Game:
    def __init__(self):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True
        self.inStartMenu = True
        self.inSettings = False  # Flag to toggle settings UI
        self.inGame = False
        self.showGameOverScreen = False

        self.player = Player()
        self.obstacleMngr = ObstacleManager()
        self.bgMngr = BackgroundManager()
        self.score = 0
        self.font = pygame.font.SysFont('firacodenerdfontpropomed', 28)

        self.loadButtons()
        self.startButtonAnimPhase = 0
        self.settingsButtonAnimPhase = 0
        self.retryButtonAnimPhase = 0

        self.numberImgs = self.loadNumberImages()
        self.scoreRecordsPath = 'Extras/scoreRecords.json'
        self.bestScore = self.getBestScore()

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

        self.homeButtonAnimPhase = 0
        self.homeButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/homeButton.png').convert_alpha(), (BUTTON_SIZE[0]/1.5, BUTTON_SIZE[1]/1.5))
        self.homeButtonRect = self.homeButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + BUTTON_SIZE[1] * 1.5))

        self.backButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/backButton.png').convert_alpha(), (BUTTON_SIZE[0]/2.5, BUTTON_SIZE[1]/2.5)) 
        self.backButtonRect = self.backButtonImg.get_rect(topleft=(10, 10))  # Position it at the top left

        self.volume = 0.5  # Default volume level
        self.muteButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/muteButton.png').convert_alpha(), (100, 100))
        self.unmuteButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/unmuteButton.png').convert_alpha(), (100, 100))
        self.volumeButtonImg = self.unmuteButtonImg  # Start with unmute image
        self.volumeButtonRect = self.unmuteButtonImg.get_rect(topright=(SCREEN_WIDTH - 100, 350))
        self.initVolumeSlider()
        self.volumeTextFont = pygame.font.SysFont('firacodenerdfontpropomed', 36) 
        self.volumeText = self.volumeTextFont.render('Game Volume', True, WHITE)

        self.trophyImg = pygame.image.load('Assets/Buttons/trophy.png').convert_alpha()
        self.trophyImg = pygame.transform.scale(self.trophyImg, (100, 100))

        self.scoreRecorded = False 


    def loadNumberImages(self):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        
        numberPaths = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        
        return [pygame.transform.scale(pygame.image.load(f'Assets/Numbers/{name}.png').convert_alpha(), NUMBER_SIZE) for name in numberPaths]

    def loadButtons(self):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        
        self.startButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/startButton.png').convert_alpha(), BUTTON_SIZE)
        self.settingsButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/settingsButton.png').convert_alpha(), BUTTON_SIZE)
        self.retryButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/retryButton.png').convert_alpha(), BUTTON_SIZE)
        
        self.startButtonRect = self.startButtonImg.get_rect(center=(SCREEN_WIDTH/2 - BUTTON_SIZE[0]/2 - 45, SCREEN_HEIGHT/2))
        self.settingsButtonRect = self.settingsButtonImg.get_rect(center=(SCREEN_WIDTH/2 + BUTTON_SIZE[0]/2 + 45, SCREEN_HEIGHT/2))
        self.retryButtonRect = self.retryButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))

    def updateScoreRecord(self, currentScore):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        try:
        
            if not os.path.exists('Extras'):
                os.makedirs('Extras')
        
            if os.path.exists(self.scoreRecordsPath):
        
                with open(self.scoreRecordsPath, 'r') as file:
                    scores = json.load(file)
        
            else:
                scores = []
        
            scores.append(currentScore)
        
            with open(self.scoreRecordsPath, 'w') as file:
                json.dump(scores, file)
        
        except Exception as e:
            print(f"Error updating score record: {e}")

    def getBestScore(self):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """

        try:
        
            if os.path.exists(self.scoreRecordsPath):
        
                with open(self.scoreRecordsPath, 'r') as file:
                    scores = json.load(file)
        
                return max(scores)
        
            return 0
        
        except Exception as e:
            print(f"Error reading best score: {e}")
        
            return 0

    def drawAnimatedScore(self, score, yPosition, animationPhase):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        
        scoreStr = str(score)
        
        totalWidth = NUMBER_SIZE[0] * len(scoreStr)
        startX = SCREEN_WIDTH / 2 - totalWidth / 2
        scaleFactor = 1.05 + 0.05 * math.sin(animationPhase)
        
        for i, digit in enumerate(scoreStr):
        
            animSize = (int(NUMBER_SIZE[0] * scaleFactor), int(NUMBER_SIZE[1] * scaleFactor))
            animImg = pygame.transform.scale(self.numberImgs[int(digit)], animSize)
            animRect = animImg.get_rect(center=(startX + i * NUMBER_SIZE[0] + NUMBER_SIZE[0] // 2, yPosition))
            self.screen.blit(animImg, animRect)

    def runGameOverScreen(self):
        """
        PURPOSE: LOGIC TO SET UP THE GAME OVER SCREEN, INCLUDING DETAILS LIKE
                 THE RETRY BUTTON, AND THE HOME BUTTON, ALONG WITH THE SCORE
                 OBTAINED, AND THE BEST SCORE
        PARAMETER(S): NONE
        RETURN: NONE
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

        self.drawAnimatedScore(self.score, SCREEN_HEIGHT / 2 - 250, self.retryButtonAnimPhase - 1)

        bestScoreStr = f"Best Score: {self.bestScore}"
        bestScoreText = self.font.render(bestScoreStr, True, WHITE)
        
        self.screen.blit(bestScoreText, (SCREEN_WIDTH / 2 - bestScoreText.get_width() / 2, SCREEN_HEIGHT / 2 - 150))

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.running = False
                self.showGameOverScreen = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
            
                if self.retryButtonRect.collidepoint((mx, my)):
                    self.selectSound.play()
                    self.restartGame()
                    self.inGame = True
                    self.inStartMenu = False
                    self.playGameMusic()
            
                elif self.homeButtonRect.collidepoint((mx, my)):
                    self.selectSound.play()
                    self.restartGame()
                    self.gameMusicStarted = False
                    self.showGameOverScreen = False
                    self.inStartMenu = True
                    self.inGame = False
                    
                    self.playMenuMusic()

        pygame.display.flip()

    def restartGame(self):
        """
        PURPOSE: DEFINES LOGIC TO RESTART GAME, AND RESET THE SCORE BY 
                 MANIPULATING BOOLEAN STATE FLAGS FROM INIT FUNC
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        self.player = Player()
        self.obstacleMngr = ObstacleManager()
        self.score = 0
        
        self.showGameOverScreen = False
        self.inStartMenu = False
        self.inGame = True
        self.scoreRecorded = False  # Reset the flag to allow score recording for the new session

        if self.inGame == True:
            self.playGameMusic()
            self.gameMusicStarted = True  # Prevent future calls

    def playMenuMusic(self):
        """
        PURPOSE: FUNCTION TO PLAY THE MENU MUSIC IN A LOOP
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        pygame.mixer.music.load('Assets/Music/menuMusic.wav')  # Load the menu music
        pygame.mixer.music.play(-1)  # Play the music in a loop (the -1 means it loops indefinitely)
    
    def playGameMusic(self):
        """
        PURPOSE: FUNCTION TO PLAY THE GAME PLAY MUSIC IN A LOOP
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        pygame.mixer.music.load('Assets/Music/gameMusic.wav')  # Load the menu music
        pygame.mixer.music.play(-1)  # Play the music in a loop (the -1 means it loops indefinitely)
    
    def toggleMute(self):
        """
        PURPOSE: LOGIC TO TOGGLE BETWEEN MUTE AND UNMUTE AND UPDATE IMAGE IN 
                 SETTINGS UI ACCORDINGLY
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        if self.volume > 0:
            self.volume = 0
            self.volumeButtonImg = self.muteButtonImg
        
        else:
            self.volume = 0.5  # Restore volume
            self.volumeButtonImg = self.unmuteButtonImg
        
        pygame.mixer.music.set_volume(self.volume)

    def initVolumeSlider(self):
        """
        PURPOSE:
        PARAMETER(S):
        RETURN:
        """
        
        # Initialize the slider to the right of the mute button, with a small gap
        sliderXStart = self.volumeButtonRect.right - 1450
        sliderY = self.volumeButtonRect.bottom - 75  # Align with the middle of the mute button
        rectWidth, rectHeight = 120, self.volumeButtonRect.height / 2  # Match height of the mute button, adjust width as desired
        spacing = 10  # Space between rectangles

        self.volOnImg = pygame.image.load('Assets/Buttons/volOn.png').convert_alpha()
        self.volOffImg = pygame.image.load('Assets/Buttons/volOff.png').convert_alpha()

        for i in range(10):
            x = sliderXStart + i * (rectWidth + spacing)
            rect = pygame.Rect(x, sliderY, rectWidth, rectHeight)
        
            self.volumeSliderRects.append(rect)

    def drawVolumeSlider(self):
        """
        PURPOSE: 
        PARAMETER(S):
        RETURN:
        """
        
        for i, rect in enumerate(self.volumeSliderRects):
        
            if i < self.volume * 10:
                self.screen.blit(pygame.transform.scale(self.volOnImg, (rect.width, rect.height)), (rect.x, rect.y))
        
            else:
                self.screen.blit(pygame.transform.scale(self.volOffImg, (rect.width, rect.height)), (rect.x, rect.y))

    def drawSettingsUI(self):
        """
        PURPOSE: CONSTRUCTS THE SETTINGS UI FOR THE USER TO BE ALLOWED TO 
                 ADJUST VOLUME IN, AND OTHER FEATURES SUCH AS NAVIGATION AND
                 MUTE BUTTONS
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        while self.inSettings:
        
            for event in pygame.event.get():
        
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
        
                    # Check if a volume slider rectangle is clicked
                    for i, rect in enumerate(self.volumeSliderRects):
                        
                        if rect.collidepoint(pos):
                            self.setVolume((i + 1) / 10.0)  # Set volume based on the rectangle clicked
                        
                            break
                    
                    # Check if the mute button is clicked
                    if self.volumeButtonRect.collidepoint(pos):
                        self.toggleMute()
                    
                    elif self.backButtonRect.collidepoint(pos):
                        self.selectSound.play()
                        self.inSettings = False
                        self.inStartMenu = True
                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.inSettings = False
                    self.inStartMenu = True

            # Redraw the settings UI
            self.screen.fill(BLACK)
            
            # Draw the back button
            mx, my = pygame.mouse.get_pos()
            
            if self.backButtonRect.collidepoint((mx, my)):
                
                if not self.backHoverSoundPlayed:
                    self.hoverSound.play()
                    self.backHoverSoundPlayed = True  # Set the flag to True after playing the sound
            
            else:
                self.backHoverSoundPlayed = False  # Reset the flag when not hovering
            
            self.screen.blit(self.backButtonImg, self.backButtonRect)
            
            # Draw the "Settings" title
            settingsFont = pygame.font.SysFont("firacodenerdfontpropomed", 72)
            settingsText = settingsFont.render("Settings", True, WHITE)
            
            self.screen.blit(settingsText, (self.screen.get_width() / 2 - settingsText.get_width() / 2, 20))

            # Draw the volume text each time the settings UI is updated
            volumeTextPos = (self.volumeSliderRects[0].left - 275, (self.volumeSliderRects[0].centery - self.volumeTextFont.get_height() // 2 ))
            self.screen.blit(self.volumeText, volumeTextPos)
            self.drawVolumeSlider()
            
            self.screen.blit(self.volumeButtonImg, self.volumeButtonRect)

            pygame.display.flip()

    def setVolume(self, volume):
        """
        PURPOSE: LOGIC TO CONTROL VOLUME DEPENDING ON SETTINGS UI INPUT FROM USER
        PARAMETER(S): volume: THE CURRENT VOLUME LEVEL DEFINED IN INIT FUNC
        RETURN: NONE
        """
        
        self.volume = volume
        pygame.mixer.music.set_volume(self.volume)
        
        if volume > 0:
            self.volumeButtonImg = self.unmuteButtonImg
        
        else:
            self.volumeButtonImg = self.muteButtonImg

    def runStartMenu(self):
        """
        PURPOSE: LOGIC TO RUN THE START MENU OF THE GAME AND DEFINE ALL RELATED
                 FUNCTIONALITY AND FEATURES
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        self.screen.fill(BLACK)
        
        mx, my = pygame.mouse.get_pos()
        
        if self.inSettings:
            self.drawSettingsUI()
        
        else:    
        
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
                self.hoverSoundPlayed = False  # Reset flag when not hovering

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


            for event in pygame.event.get():
        
                if event.type == pygame.QUIT:
                    self.running = False
                    self.inStartMenu = False
        
                elif event.type == pygame.MOUSEBUTTONDOWN:
        
                    if self.startButtonRect.collidepoint((mx, my)):
                        self.selectSound.play()
                        # Check if score records exist
                        if self.getBestScore() == 0:
                            self.runTutorial()  # Run the tutorial
                        else:
                            # self.run()  # Method to encapsulate starting the game
                            self.inGame = True
                            self.inStartMenu = False
        
                        if not self.gameMusicStarted:
                            self.playGameMusic()  # Start game music
                            self.gameMusicStarted = True  # Prevent future calls

                    elif self.settingsButtonRect.collidepoint((mx, my)):
                        self.selectSound.play()
                        self.selectSoundPlayed = True
                        self.inSettings = True  # Open settings UI

                    else:
                        self.selectSoundPlayed = False

            pygame.display.flip()

    def drawScore(self):
        """
        PURPOSE: GOES THROUGH SCORE VARIABLE TO DETERMINE CURRENT SCORE, AND 
                 UPDATES THE SCORE DRAWING ON SCREEN TO REPRESENT CHANGES AND 
                 ACCURATELY DRAW SCORES
        PARAMETER(S): NONE
        RETURN: NONE
        """
        
        scoreStr = str(self.score)
        totalWidth = NUMBER_SIZE[0] * len(scoreStr)  # Total width to display all digits side by side
        startX = SCREEN_WIDTH / 2 - totalWidth / 2  # Starting X position for the first digit
        
        for i, digit in enumerate(scoreStr):
            self.screen.blit(self.numberImgs[int(digit)], (startX + i * NUMBER_SIZE[0], 10))

    def runTutorial(self):
        tutorialDone = False
        promptShown = False
        self.player = Player()  # Reset player
        self.obstacleMngr = ObstacleManager()  # Reset obstacles

        while not tutorialDone and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    tutorialDone = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not promptShown:
                            promptShown = True  # Hide prompt after first gravity flip
                            self.player.flipGravity()
                        else:
                            tutorialDone = True  # End tutorial on second space press
                    if event.key == pygame.K_ESCAPE:
                        tutorialDone = True  # Allow exiting the tutorial with ESC

            self.screen.fill(BLACK)
            self.bgMngr.draw(self.screen)
            if not promptShown:
                # Display the spacebar prompt
                spaceBarImg = pygame.image.load('Assets/Buttons/spaceBar.png').convert_alpha()
                spaceBarImg = pygame.transform.scale(spaceBarImg, (400, 300))
                self.screen.blit(spaceBarImg, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 - 150))
            else:
                # Regular tutorial gameplay
                self.player.update()
                self.obstacleMngr.update()
                self.player.draw(self.screen)
                self.obstacleMngr.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        # self.run()
        self.inGame = True
        self.inStartMenu = False

    def run(self):
        """
        PURPOSE: MAIN GAME LOOP TO PERFORM ALL IN GAME FUNCTIONS THROUGH METHOD CALLS
        PARAMETER(S): NONE
        RETURN: NONE
        """
        while self.running:
        
            if self.inStartMenu:
                self.runStartMenu()
        
            elif self.showGameOverScreen:
                self.runGameOverScreen()
        
            else:
                elapsedTime = self.clock.get_time() / 1000
        
                for event in pygame.event.get():
        
                    if event.type == pygame.QUIT:
                        self.running = False
        
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.player.flipGravity()

                self.player.update()
                self.bgMngr.update(elapsedTime)
                self.obstacleMngr.update()
        
                previous_score = self.score
                self.score = self.obstacleMngr.updateScore(self.player.spriteRect, self.score)
        
                if self.score > previous_score:
                    self.pointSound.play()
                
                self.screen.fill(BLACK)
                self.bgMngr.draw(self.screen)
                self.player.draw(self.screen)
                self.obstacleMngr.draw(self.screen)
        
                self.drawScore()  # Replace the old score drawing method

                pygame.display.flip()

                if self.obstacleMngr.checkCollision(self.player.spriteRect) or (self.player.spriteRect.top <= 0 or self.player.spriteRect.bottom >= SCREEN_HEIGHT):
                    if not self.scoreRecorded:  # Check if the score hasn't been recorded yet
                        self.updateScoreRecord(self.score)  # Update the score record
                        self.scoreRecorded = True  # Set the flag to True to avoid duplicate recordings
                    self.deathSound.play()
                    pygame.mixer.music.stop()  # Stop the game music here

                    self.showGameOverScreen = True

                self.clock.tick(60)

        pygame.quit()
        sys.exit()

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    game = Game()
    game.run()