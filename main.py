import pygame
import sys
import random
import math
import json
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(1)  

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
BLACK, WHITE, RED = (0, 0, 0), (255, 255, 255), (255, 0, 0)
SPRITE_SCALE = 0.06
MAX_VEL = 5
OBSTACLE_WIDTH = int(SCREEN_WIDTH * 0.05)
OBSTACLE_GAP = SCREEN_HEIGHT * 0.2
OBSTACLE_SPEED = -4
ANIMATION_TIME = 10
BUTTON_SIZE = (360, 258)  # 3x the original size
NUMBER_SIZE = (80, 108)  # Size of each number image

class BackgroundManager:
    def __init__(self):
        self.bgImgs = {
            'sky': pygame.image.load('Assets/Background/sky.png').convert_alpha(),
            'cloudsBack': pygame.image.load('Assets/Background/cloudsBack.png').convert_alpha(),
            'cloudsFront': pygame.image.load('Assets/Background/cloudsFront.png').convert_alpha(),
            'ground': pygame.image.load('Assets/Background/ground.png').convert_alpha()
        }
        self.bgXPos = {
            'cloudsBack': [0, SCREEN_WIDTH],
            'cloudsFront': [0, SCREEN_WIDTH],
            'ground': [0, SCREEN_WIDTH]
        }
        self.bgSpeeds = {
            'cloudsBack': -1 * SCREEN_WIDTH / 60,
            'cloudsFront': -2 * SCREEN_WIDTH / 60,
            'ground': OBSTACLE_SPEED * SCREEN_WIDTH / 60
        }

    def update(self, elapsedTime):
        for key in self.bgXPos.keys():
            self.bgXPos[key] = [(x + self.bgSpeeds[key] * elapsedTime) % SCREEN_WIDTH for x in self.bgXPos[key]]

    def draw(self, screen):
        screen.blit(self.bgImgs['sky'], (0, 0))
        for key in ['cloudsBack', 'cloudsFront', 'ground']:
            for xPos in self.bgXPos[key]:
                screen.blit(self.bgImgs[key], (xPos, 0))
                if xPos < SCREEN_WIDTH:
                    screen.blit(self.bgImgs[key], (xPos - SCREEN_WIDTH, 0))

class Player:
    def __init__(self):
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
        self.playerAcc = [0, 0.35]
        self.gravFlipped = False
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
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
        screen.blit(self.spriteImg, self.spriteRect)

    def flipGravity(self):
        self.gravFlipped = not self.gravFlipped
        self.playerAcc[1] = -self.playerAcc[1]
        self.spriteImgs, self.spriteImgsFlipped = self.spriteImgsFlipped, self.spriteImgs
        self.spriteImg = self.spriteImgs[self.currSprite]

class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.obstacleID = 0

    def update(self):
        if not self.obstacles or self.obstacles[-1]['x'] < SCREEN_WIDTH * 0.75:
            obstacleHeight = random.randint(int(SCREEN_HEIGHT * 0.1), int(SCREEN_HEIGHT * 0.6))
            self.obstacles.append({'x': SCREEN_WIDTH, 'y': 0, 'height': obstacleHeight, 'id': self.obstacleID, 'passed': False})
            self.obstacles.append({'x': SCREEN_WIDTH, 'y': obstacleHeight + OBSTACLE_GAP, 'height': SCREEN_HEIGHT - (obstacleHeight + OBSTACLE_GAP), 'id': self.obstacleID, 'passed': False})
            self.obstacleID += 1
        self.obstacles = [{'x': obstacle['x'] + OBSTACLE_SPEED, 'y': obstacle['y'], 'height': obstacle['height'], 'id': obstacle['id'], 'passed': obstacle['passed']} for obstacle in self.obstacles]
        self.obstacles = [obstacle for obstacle in self.obstacles if obstacle['x'] + OBSTACLE_WIDTH > 0]

    def draw(self, screen):
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, RED, (obstacle['x'], obstacle['y'], OBSTACLE_WIDTH, obstacle['height']))

    def checkCollision(self, playerRect):
        for obstacle in self.obstacles:
            obstacleRect = pygame.Rect(obstacle['x'], obstacle['y'], OBSTACLE_WIDTH, obstacle['height'])
            if playerRect.colliderect(obstacleRect):
                return True
        return False

    def updateScore(self, playerRect, score):
        for obstacle in self.obstacles:
            if playerRect.right > obstacle['x'] + OBSTACLE_WIDTH and not obstacle['passed']:
                obstacle['passed'] = True
                pairPassed = all(ob['passed'] for ob in self.obstacles if ob['id'] == obstacle['id'])
                if pairPassed:
                    score += 1
                    for ob in self.obstacles:
                        if ob['id'] == obstacle['id']:
                            ob['passed'] = True
        return score

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.inStartMenu = True
        self.player = Player()
        self.obstacleMngr = ObstacleManager()
        self.bgMngr = BackgroundManager()
        self.score = 0
        self.font = pygame.font.SysFont('firacodenerdfontpropomed', 28)
        self.loadButtons()
        self.startButtonAnimPhase = 0
        self.settingsButtonAnimPhase = 0
        self.retryButtonAnimPhase = 0
        self.showGameOverScreen = False
        self.numberImgs = self.loadNumberImages()
        self.scoreRecordsPath = 'Extras/scoreRecords.json'
        self.bestScore = self.getBestScore()
        self.playMenuMusic()  # Play menu music when the game object is initialized
        self.hoverSound = pygame.mixer.Sound('Assets/Music/hover.wav')  # Load hover sound
        self.hoverSoundPlayed = False  # Flag to track if the hover sound has been played
        self.selectSound = pygame.mixer.Sound('Assets/Music/select.wav')  # Load select sound
        self.selectSoundPlayed = False # Flag to track if select sound has been played
        self.gameMusicStarted = False  # Add this line
        self.inGame = False
        self.homeButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/homeButton.png').convert_alpha(), (BUTTON_SIZE[0]/1.5, BUTTON_SIZE[1]/1.5))
        self.homeButtonRect = self.homeButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + BUTTON_SIZE[1] * 1.5))
        self.homeButtonAnimPhase = 0
        self.volume = 0.5  # Default volume level
        self.isMuted = False  # Mute state
        self.inSettings = False  # Flag to toggle settings UI
        self.muteButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/muteButton.png').convert_alpha(), (100, 100))
        self.unmuteButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/unmuteButton.png').convert_alpha(), (100, 100))
        self.volumeButtonImg = self.unmuteButtonImg  # Start with unmute image
        self.volumeButtonRect = self.unmuteButtonImg.get_rect(topright=(SCREEN_WIDTH - 150, 110))  # Adjust position as needed
        self.deathSound = pygame.mixer.Sound('Assets/Music/death.wav')  # Load the death sound
        self.volumeSliderRects = []
        self.initVolumeSlider()
        self.volumeTextFont = pygame.font.SysFont('segoeui', 36, bold=True)  # Choose an appropriate font size
        self.volumeText = self.volumeTextFont.render('Game Volume', True, WHITE)


    def loadNumberImages(self):
        numberPaths = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        return [pygame.transform.scale(pygame.image.load(f'Assets/Numbers/{name}.png').convert_alpha(), NUMBER_SIZE) for name in numberPaths]

    def loadButtons(self):
        self.startButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/startButton.png').convert_alpha(), BUTTON_SIZE)
        self.settingsButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/settingsButton.png').convert_alpha(), BUTTON_SIZE)
        self.retryButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/retryButton.png').convert_alpha(), BUTTON_SIZE)
        self.startButtonRect = self.startButtonImg.get_rect(center=(SCREEN_WIDTH/2 - BUTTON_SIZE[0]/2 - 45, SCREEN_HEIGHT/2))
        self.settingsButtonRect = self.settingsButtonImg.get_rect(center=(SCREEN_WIDTH/2 + BUTTON_SIZE[0]/2 + 45, SCREEN_HEIGHT/2))
        self.retryButtonRect = self.retryButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))

    def updateScoreRecord(self, currentScore):
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
        self.screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()

        self.screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()

        s = pygame.Surface((800, 600), pygame.SRCALPHA)   # Semi-transparent overlay
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (SCREEN_WIDTH / 2 - 400, SCREEN_HEIGHT / 2 - 300))

        # Draw "YOU DIED!" text with animation
        pygame.font.init()
        youDiedFont = pygame.font.SysFont("firacodenerdfontpropomed", 78) 
        youDiedText = youDiedFont.render("You Died!", True, RED)
        youDiedTextSize = youDiedText.get_size()
        scaleFactor = 1.1 + 0.05 * math.sin(pygame.time.get_ticks() / 200)  # Adjust for desired animation speed and size
        youDiedText = pygame.transform.scale(youDiedText, (int(youDiedTextSize[0] * scaleFactor), int(youDiedTextSize[1] * scaleFactor)))
        youDiedRect = youDiedText.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 450))  # Adjust Y position as needed
        self.screen.blit(youDiedText, youDiedRect.topleft)

        homeButtonYOffset = self.retryButtonRect.bottom + 50  # 20 pixels below the retry button

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

        # Logic for animating and positioning the home button below the retry button
        homeButtonYOffset = self.retryButtonRect.bottom + 20  # 20 pixels below the retry button

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
        self.player = Player()
        self.obstacleMngr = ObstacleManager()
        self.score = 0
        self.showGameOverScreen = False
        self.inStartMenu = False
        self.inGame = True

        if self.inGame == True:
            self.playGameMusic()
            self.gameMusicStarted = True  # Prevent future calls

    def playMenuMusic(self):
        pygame.mixer.music.load('Assets/Music/menuMusic.wav')  # Load the menu music
        pygame.mixer.music.play(-1)  # Play the music in a loop (the -1 means it loops indefinitely)
    
    def playGameMusic(self):
        pygame.mixer.music.load('Assets/Music/gameMusic.wav')  # Load the menu music
        pygame.mixer.music.play(-1)  # Play the music in a loop (the -1 means it loops indefinitely)
    
    def toggleMute(self):
        if self.volume > 0:
            self.volume = 0
            self.volumeButtonImg = self.muteButtonImg
        else:
            self.volume = 0.5  # Restore volume
            self.volumeButtonImg = self.unmuteButtonImg
        pygame.mixer.music.set_volume(self.volume)

    def initVolumeSlider(self):
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
        for i, rect in enumerate(self.volumeSliderRects):
            if i < self.volume * 10:
                self.screen.blit(pygame.transform.scale(self.volOnImg, (rect.width, rect.height)), (rect.x, rect.y))
            else:
                self.screen.blit(pygame.transform.scale(self.volOffImg, (rect.width, rect.height)), (rect.x, rect.y))

    def drawSettingsUI(self):
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.inSettings = False
                    self.inStartMenu = True

            # Redraw the settings UI
            self.screen.fill(BLACK)
            # Draw the volume text each time the settings UI is updated
            volumeTextPos = (self.volumeSliderRects[0].left - 250, (self.volumeSliderRects[0].centery - self.volumeTextFont.get_height() // 2 ) - 5)
            self.screen.blit(self.volumeText, volumeTextPos)
            self.drawVolumeSlider()
            self.screen.blit(self.volumeButtonImg, self.volumeButtonRect)
            pygame.display.flip()

    def setVolume(self, volume):
        self.volume = volume
        pygame.mixer.music.set_volume(self.volume)
        if volume > 0:
            self.volumeButtonImg = self.unmuteButtonImg
        else:
            self.volumeButtonImg = self.muteButtonImg

    def runStartMenu(self):
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
                        pygame.mixer.music.stop()  # Stop the menu music
                        self.selectSound.play()
                        self.inStartMenu = False
                        self.inGame = True
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
        scoreStr = str(self.score)
        totalWidth = NUMBER_SIZE[0] * len(scoreStr)  # Total width to display all digits side by side
        startX = SCREEN_WIDTH / 2 - totalWidth / 2  # Starting X position for the first digit
        for i, digit in enumerate(scoreStr):
            self.screen.blit(self.numberImgs[int(digit)], (startX + i * NUMBER_SIZE[0], 10))

    def run(self):
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
                self.score = self.obstacleMngr.updateScore(self.player.spriteRect, self.score)

                self.screen.fill(BLACK)
                self.bgMngr.draw(self.screen)
                self.player.draw(self.screen)
                self.obstacleMngr.draw(self.screen)
                self.drawScore()  # Replace the old score drawing method

                pygame.display.flip()

                if self.obstacleMngr.checkCollision(self.player.spriteRect) or (self.player.spriteRect.top <= 0 or self.player.spriteRect.bottom >= SCREEN_HEIGHT):
                    self.deathSound.play()
                    pygame.mixer.music.stop()  # Stop the game music here
                    self.showGameOverScreen = True

                self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()