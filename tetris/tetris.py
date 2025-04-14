import pygame, sys, random
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 300
WINDOWHEIGHT = 600
WINDOWCOLOR = (0,0,0)
TEXTCOLOR = (255,255,255)
SPACESIZE = 30
UNITLENGTH = 4
FPS = 5
topScore = 0

# set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Tetris')
pygame.mouse.set_visible(False)

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
                
def draw_text(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect(center=(x,y))
    surface.blit(textobj, textrect)

def show_gameover_screen():
    pygame.mixer.music.stop()
    gameOverSound.play()
    transparent_surface = pygame.Surface((400,300))
    transparent_surface.fill((255, 255, 255))
    transparent_surface.set_alpha(70)
    surface = transparent_surface.get_rect()
    surface.centerx = windowSurface.get_rect().centerx
    surface.centery = windowSurface.get_rect().centery
    windowSurface.blit(transparent_surface, surface)
    draw_text("GAME OVER", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-80)
    draw_text(f"Your Score: {score}", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-30)
    draw_text(f"Top Score: {topScore}", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+20)
    draw_text("Press a key to play again.", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+70)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                    return
                elif event.key == K_RETURN:
                    return
    
        pygame.display.update()
        mainClock.tick(FPS)



## SOUND ##
gameOverSound = pygame.mixer.Sound('music/gameover.mp3')
pygame.mixer.music.load('music/Soundbackground_CasaRosa.mp3')

## FONT ##
font = pygame.font.SysFont(None, 36)

## DEFINE UNITS ##
x = WINDOWWIDTH/2
y = 0
units = {"unit1": [(x,y), (x+SPACESIZE,y), (x+2*SPACESIZE,y), (x+3*SPACESIZE,y)],
         "unit2": [(x,y), (x-2*SPACESIZE,y+SPACESIZE), (x-SPACESIZE,y+SPACESIZE), (x,y+SPACESIZE)],
         "unit3": [(x,y), (x,y+SPACESIZE), (x+SPACESIZE,y+SPACESIZE), (x+2*SPACESIZE,y+SPACESIZE)],
         "unit4": [(x,y), (x+SPACESIZE,y), (x,y+SPACESIZE), (x+SPACESIZE,y+SPACESIZE)],
         "unit5": [(x,y), (x+SPACESIZE,y), (x+SPACESIZE,y+SPACESIZE), (x+2*SPACESIZE, y+SPACESIZE)],
         "unit6": [(x,y), (x+SPACESIZE,y), (x-SPACESIZE,y+SPACESIZE), (x,y+SPACESIZE)],
         "unit7": [(x,y), (x-SPACESIZE,y+SPACESIZE), (x,y+SPACESIZE), (x+SPACESIZE,y+SPACESIZE)]}
units_minx = []
units_maxx = []
for unit in units:
    minx = units[unit][0][0]
    maxx = units[unit][0][0]
    for square in units[unit]:
        if square[0] < minx:
            minx = square[0]
        if square[0] > maxx:
            maxx = square[0]
    units_minx.append(minx)
    units_maxx.append(maxx)
units_color = [(255,0,0), (255,135,0), (255,209,0), (73,179,0), (0,193,236), (166,87,255), (255,96,245)]


## WINDOW1: START WINDOW ##
windowSurface.fill(WINDOWCOLOR)
draw_text('Welcome to the Tetris!', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-50)
draw_text('Press ENTER to start.', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery)
pygame.display.update()
start_game()

# game loop
while True:
    gameover = False
    score = 0
    windowSurface.fill(WINDOWCOLOR)
    # initiate the falling unit
    unit_index = random.randint(0,len(units)-1)
    unit_pos = units[list(units.keys())[unit_index]]
    unit_color = units_color[unit_index]
    fall_direction = (0, SPACESIZE) # the falling direction is always down
    # initiate bottom line
    bottoms = []
    for i in range(WINDOWWIDTH//SPACESIZE):
        bottoms.append((i*SPACESIZE, (WINDOWHEIGHT//SPACESIZE-1)*SPACESIZE))
    # initiate occupation matrix
    rows = WINDOWHEIGHT//SPACESIZE
    cols = WINDOWWIDTH//SPACESIZE
    # initiate stacking drawing group
    stacks = []
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    pygame.mixer.music.play(-1,0.0)

    while gameover == False:
        move_direction = (0,0) # the initial move direction is None
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif (event.key == K_LEFT or event.key == K_a) and (units_minx[unit_index] > 0):
                    move_direction = (-SPACESIZE, 0)
                elif (event.key == K_RIGHT or event.key == K_d) and (units_maxx[unit_index] < ((WINDOWWIDTH//SPACESIZE)-1)*SPACESIZE):
                    move_direction = (SPACESIZE, 0)
        
        # unit next position
        new_unit_pos = []
        for square in unit_pos:
            new_square = (int(square[0]+fall_direction[0]+move_direction[0]), int(square[1]+fall_direction[1]+move_direction[1]))
            new_unit_pos.append(new_square)
        unit_pos = new_unit_pos

        # check bottoming
        for square in unit_pos:
            if bottoms[square[0]//SPACESIZE][1] == square[1]: # the unit touch the bottom
                for sq in unit_pos:
                    if sq[1]-SPACESIZE < bottoms[sq[0]//SPACESIZE][1]:
                        bottoms[sq[0]//SPACESIZE] = (sq[0], sq[1]-SPACESIZE) # update bottom list
                    # update occupation matrix
                    matrix[sq[1]//SPACESIZE][sq[0]//SPACESIZE] = 1
                    # add to static drawing group
                    stacks.append((unit_pos, unit_color))
                # check row removing and get score
                for r in range(len(matrix)-1, -1, -1):
                    if sum(matrix[r]) == len(matrix[r]):
                        matrix.pop(r)
                        matrix.insert(0, [0 for _ in range(cols)])
                        score += 1
                # generate new unit
                unit_index = random.randint(0,len(units)-1)
                unit_pos = units[list(units.keys())[unit_index]]
                unit_color = units_color[unit_index]
                break

        # check gameover
        for b in bottoms:
            if b[1] <= 0:
                if topScore < score:
                    topScore = score
                gameover = True
                break
        
        # draw game world in the window
        windowSurface.fill(WINDOWCOLOR)
        for unit in stacks:
            pos = unit[0]
            color = unit[1]
            for p in pos:
                pygame.draw.rect(windowSurface, color, (p[0], p[1], SPACESIZE, SPACESIZE))

        for unit in unit_pos:
            pygame.draw.rect(windowSurface, unit_color, (unit[0], unit[1], SPACESIZE, SPACESIZE))

        pygame.display.flip()
        mainClock.tick(FPS)
    
    # show the game over screen
    if gameover:
        show_gameover_screen()
    
    gameOverSound.stop()
    

