import pygame, sys, random
from pygame.locals import *

WINDOWWIDTH = 600
WINDOWHEIGHT = 600
TEXTCOLOR = (255,255,255)
BACKGROUNDCOLOR = (0,0,0)
FPS = 10
SPACESIZE = 25
SNAKECOLOR = (255,0,0)
SNAKELENGTH = 3
FOODCOLOR = (0,255,0)

def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # pressing ESC quits
                    terminate()
                return 
    
def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)

# set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Snake')
pygame.mouse.set_visible(False)

# set up sounds
gameOverSound = pygame.mixer.Sound('music/gameover.mp3')
pygame.mixer.music.load('music/Soundbackground_CasaRosa.mp3')

# set up the fonts
font = pygame.font.SysFont(None, 36)

# show the "Start" screen
windowSurface.fill(BACKGROUNDCOLOR)
drawText('Welcome to the Snake!', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-50)
drawText('Press a key to start.', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery)
pygame.display.update()
waitForPlayerToPressKey()

# game loop
topScore = 0
while True:
    score = 0
    windowSurface.fill(BACKGROUNDCOLOR)
    # initialize snake
    snake = []
    snakeX = WINDOWWIDTH/2
    snakeY = WINDOWHEIGHT/2
    for i in range(SNAKELENGTH):
        snake.append((snakeX+i*SPACESIZE, snakeY))
    direction = (-SPACESIZE, 0) # the initial direction is left
    # initialize food
    food = (random.randint(0,((WINDOWWIDTH//SPACESIZE)-1))*SPACESIZE, random.randint(0,((WINDOWHEIGHT//SPACESIZE)-1))*SPACESIZE)
    pygame.mixer.music.play(-1,0.0)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif (event.key == K_LEFT or event.key == K_a) and direction != (SPACESIZE, 0):
                    direction = (-SPACESIZE, 0)
                elif (event.key == K_RIGHT or event.key == K_d) and direction != (-SPACESIZE, 0):
                    direction = (SPACESIZE, 0)
                elif (event.key == K_UP or event.key == K_w) and direction != (0, SPACESIZE):
                    direction = (0, -SPACESIZE)
                elif (event.key == K_DOWN or event.key == K_s) and direction != (0, -SPACESIZE):
                    direction = (0, SPACESIZE)
                    

        # snake next turn
        new_head = (snake[0][0]+direction[0], snake[0][1]+direction[1])
        snake.insert(0, new_head)

        # check collision
        if new_head == food:
            food = (random.randint(0,((WINDOWWIDTH//SPACESIZE)-1))*SPACESIZE, random.randint(0,((WINDOWHEIGHT//SPACESIZE)-1))*SPACESIZE)
            score += 1
        else:
            snake.pop() # remove the last part if no food eaten
    
        if new_head[0] < 0 or new_head[0] >= WINDOWWIDTH or new_head[1] < 0 or new_head[1] >= WINDOWHEIGHT or new_head in snake[1:]:
            if score > topScore:
                topScore = score
            break
        
        # draw the game world on the window
        windowSurface.fill(BACKGROUNDCOLOR)
        # draw food
        pygame.draw.rect(windowSurface, FOODCOLOR, (food[0], food[1], SPACESIZE, SPACESIZE))
        # draw snake
        for bodypart in snake:
            pygame.draw.rect(windowSurface, SNAKECOLOR, (bodypart[0], bodypart[1], SPACESIZE, SPACESIZE))
        
        pygame.display.flip()
        mainClock.tick(FPS)
    
    # show the game over screen
    pygame.mixer.music.stop()
    gameOverSound.play()

    transparent_surface = pygame.Surface((400,300))
    transparent_surface.fill((255, 255, 255))
    transparent_surface.set_alpha(70)
    surface = transparent_surface.get_rect()
    surface.centerx = windowSurface.get_rect().centerx
    surface.centery = windowSurface.get_rect().centery
    windowSurface.blit(transparent_surface, surface)
    drawText("GAME OVER", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-80)
    drawText(f"Your Score: {score}", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-30)
    drawText(f"Top Score: {topScore}", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+20)
    drawText("Press a key to play again.", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+70)
    pygame.display.update()
    waitForPlayerToPressKey()
    gameOverSound.stop()
