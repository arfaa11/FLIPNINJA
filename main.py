import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

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
        self.inStartMenu = True  # To control when to show the start menu
        self.player = Player()
        self.obstacleMngr = ObstacleManager()
        self.bgMngr = BackgroundManager()
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.loadButtons()
        self.startButtonAnimPhase = 0
        self.retryButtonAnimPhase = 0
        self.showGameOverScreen = False  # New attribute to control the game over screen


    def loadButtons(self):
        self.startButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/startButton.png').convert_alpha(), BUTTON_SIZE)
        self.settingsButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/settingsButton.png').convert_alpha(), BUTTON_SIZE)
        self.retryButtonImg = pygame.transform.scale(pygame.image.load('Assets/Buttons/retryButton.png').convert_alpha(), BUTTON_SIZE)
        self.startButtonRect = self.startButtonImg.get_rect(center=(SCREEN_WIDTH/2 - BUTTON_SIZE[0]/2 - 25, SCREEN_HEIGHT/2))
        self.settingsButtonRect = self.settingsButtonImg.get_rect(center=(SCREEN_WIDTH/2 + BUTTON_SIZE[0]/2 + 25, SCREEN_HEIGHT/2))
        self.retryButtonRect = self.retryButtonImg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    def runStartMenu(self):
        self.screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()
        
        # Button Animation for Start Button
        if self.startButtonRect.collidepoint((mx, my)):
            self.screen.blit(self.startButtonImg, self.startButtonRect)
        else:
            scaleFactor = 1.10 + 0.05 * math.sin(self.startButtonAnimPhase)
            animButton = pygame.transform.scale(self.startButtonImg, (int(BUTTON_SIZE[0] * scaleFactor), int(BUTTON_SIZE[1] * scaleFactor)))
            animRect = animButton.get_rect(center=self.startButtonRect.center)
            self.screen.blit(animButton, animRect)
            self.startButtonAnimPhase += 0.015
        
        # Settings Button - No Animation
        self.screen.blit(self.settingsButtonImg, self.settingsButtonRect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.inStartMenu = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.startButtonRect.collidepoint((mx, my)):
                    self.inStartMenu = False  # Start the game
                
        pygame.display.flip()

    def runGameOverScreen(self):
        self.screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()

        # Draw semi-transparent rectangle
        s = pygame.Surface((800, 400), pygame.SRCALPHA)  # Size of the rectangle
        s.fill((0, 0, 0, 180))  # Black rectangle with transparency
        self.screen.blit(s, (SCREEN_WIDTH / 2 - 400, SCREEN_HEIGHT / 2 - 200))

        # Retry Button Animation
        if self.retryButtonRect.collidepoint((mx, my)):
            self.screen.blit(self.retryButtonImg, self.retryButtonRect)
        else:
            scaleFactor = 1.15 + 0.10 * math.sin(self.retryButtonAnimPhase)
            animButton = pygame.transform.scale(self.retryButtonImg, (int(BUTTON_SIZE[0] * scaleFactor), int(BUTTON_SIZE[1] * scaleFactor)))
            animRect = animButton.get_rect(center=self.retryButtonRect.center)
            self.screen.blit(animButton, animRect)
            self.retryButtonAnimPhase += 0.015

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.showGameOverScreen = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.retryButtonRect.collidepoint((mx, my)):
                    self.restartGame()

        pygame.display.flip()

    def restartGame(self):
           # Reset game state for a new game
           self.player = Player()
           self.obstacleMngr = ObstacleManager()
           self.score = 0
           self.showGameOverScreen = False
           self.inStartMenu = False  # Or set this to False to restart immediately

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
                scoreTxt = self.font.render(f"Score: {self.score}", True, WHITE)
                self.screen.blit(scoreTxt, (10, 10))

                pygame.display.flip()

                if self.obstacleMngr.checkCollision(self.player.spriteRect):
                    self.showGameOverScreen = True  # Show game over screen instead of quitting

                self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()