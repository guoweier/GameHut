import pygame, sys, random
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 600
WINDOWHEIGHT = 600
WINDOWCOLOR = (238,123,195)
TEXTCOLOR = (255,255,255)
SPACESIZE = 30
FPS = 3
topScore = 0

# set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Candycrush')

## FUNCTION ##
def terminate():
    pygame.quit()
    sys.exit()

def start_game():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE: # pressing ESC quits
                    terminate()
                elif event.key == K_RETURN:
                    return 
                
def draw_text(text, font, surface, x, y, color=TEXTCOLOR):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x,y))
    surface.blit(textobj, textrect)

## SOUND ##
gameOverSound = pygame.mixer.Sound('music/gameover.mp3')
pygame.mixer.music.load('music/Soundbackground_CasaRosa.mp3')