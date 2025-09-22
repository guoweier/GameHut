import pygame, sys, random
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 660
WINDOWHEIGHT = 660
WINDOWCOLOR = (57,57,57)
GAMEWIDTH = 300
GAMEHEIGHT = 600
TEXTCOLOR = (255,255,255)
SCORECOLOR = (100,100,100)
SPACESIZE = 30
UNITLENGTH = 4
FPS = 3
topScore = 0

# set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Tetris')

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

def load_image(file, x, y):
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, (x,y))
    return img

def draw_image(img, surface, x, y, square=False):
    if square == False:
        img_rect = img.get_rect(center=(x,y))
        surface.blit(img, img_rect)
    elif square == True:
        img_rect = img.get_rect(topleft=(x,y))
        surface.blit(img, img_rect)

def get_unit_pos(unit,x,y):
    rows_index = []
    cols_index = []
    unit_pos = []
    for r in range(len(unit)):
        for c in range(len(unit)):
            if unit[r][c] == 1:
                rows_index.append(r)
                cols_index.append(c)
                unit_pos.append((int(x+c*SPACESIZE),int(y-(len(unit)-1-r)*SPACESIZE)))
    return [unit_pos, rows_index, cols_index]
    
def rotate_unit(unit,x,y,matrix,rotate):
    if rotate == True:
        unit_rt = [list(row)[::-1] for row in zip(*unit)] # rotate 90 clockwise 
        out = unit_rt
        unit_pos, rows_index, cols_index = get_unit_pos(unit_rt,x,y)
        unit_miny = y-(len(unit_matrix)-1-min(rows_index))*SPACESIZE
        minr = min(rows_index)
        maxr = max(rows_index)
        minc = min(cols_index)
        maxc = max(cols_index)
        if (x//SPACESIZE-1+minc < 0) or (x//SPACESIZE-1+maxc > cols-1) or (y//SPACESIZE-1-(len(unit_rt)-1-minr) < 0) or (y//SPACESIZE-1-(len(unit_rt)-1-maxr) > rows-1): # the rotated unit cannot exceed game board
            out = unit
        elif unit_miny >= (WINDOWHEIGHT-GAMEHEIGHT)/2:
            for square in unit_pos: 
                if matrix[square[1]//SPACESIZE-1][square[0]//SPACESIZE-1] == 1: # already occupied in game board
                    out = unit 
                    break 
    else:
        out = unit 
    return out 

def determine_border(unit_pos, matrix, direction):
    move = True 
    if direction == "left":
        if unit_minx-SPACESIZE < (WINDOWHEIGHT-GAMEHEIGHT)/2: 
            move = False 
        else:
            for square in unit_pos:
                if matrix[square[1]//SPACESIZE-1][square[0]//SPACESIZE-2][0] == 1:
                    move = False
                    break 
    elif direction == "right":
        if unit_maxx+SPACESIZE > ((GAMEWIDTH//SPACESIZE)-1)*SPACESIZE+(WINDOWHEIGHT-GAMEHEIGHT)/2:
            move = False 
        else:
            for square in unit_pos:
                if matrix[square[1]//SPACESIZE-1][square[0]//SPACESIZE][0] == 1:
                    move = False 
                    break
    return move 

def get_nextunit_pos(unit, boardx, boardy):
    rows_index = []
    cols_index = []
    unit_pos_index = []
    unit_pos = []
    for r in range(len(unit)):
        for c in range(len(unit)):
            if unit[r][c] == 1:
                rows_index.append(r)
                cols_index.append(c)
                unit_pos_index.append((c,r))
    rows_index_center = min(set(rows_index))+len(set(rows_index))/2
    cols_index_center = min(set(cols_index))+len(set(cols_index))/2
    for sq in unit_pos_index:
        sqx = boardx+(sq[0]-cols_index_center)*SPACESIZE
        sqy = boardy+(sq[1]-rows_index_center)*SPACESIZE
        unit_pos.append((sqx,sqy))
    return unit_pos 

    
def show_gameover_screen(gameoverboard_img):
    pygame.mixer.music.stop()
    gameOverSound.play()
    draw_image(gameoverboard_img, windowSurface, 180, 330)
    draw_text("GAME OVER", font, windowSurface, 180, 260, SCORECOLOR)
    draw_text(f"Your Score: {score}", fontgameover, windowSurface, 180, 310, SCORECOLOR)
    draw_text(f"Top Score: {topScore}", fontgameover, windowSurface, 180, 340, SCORECOLOR)
    draw_text("Play Again", fontgameover, windowSurface, 180, 410, SCORECOLOR)
    # mouse click for play again
    playagainbox = pygame.Rect(80, 380, 180, 40)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if playagainbox.collidepoint(event.pos):
                    return
                
        pygame.display.update()
        mainClock.tick(FPS)

## SOUND ##
gameOverSound = pygame.mixer.Sound('music/gameover.mp3')
pygame.mixer.music.load('music/Soundbackground_CasaRosa.mp3')

## FONT ##
font = pygame.font.Font("font/Squarea_Regular.ttf", 36)
fontscore = pygame.font.Font("font/Squarea_Regular.ttf", 48)
fontgameover = pygame.font.Font("font/Squarea_Regular.ttf", 28)

## IMAGE ##
gameboard_img = load_image("image/gameboard.png", 320, 620)
nextunitboard_img = load_image("image/nextunitboard.png", 260, 200)
scoreboard_img = load_image("image/scoreboard.png", 260, 200)
label_img = load_image("image/label.png", 240, 90)
gameoverboard_img = load_image("image/gameoverboard.png", 260, 260)

## DEFINE UNITS ##
units_matrix = {"unit1": [[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,1,1,1]],
                "unit2":[[0,0,0],[0,0,1],[1,1,1]],
                "unit3":[[0,0,0],[1,0,0],[1,1,1]],
                "unit4":[[1,1],[1,1]],
                "unit5":[[0,0,0],[1,1,0],[0,1,1]],
                "unit6":[[0,0,0],[0,1,1],[1,1,0]],
                "unit7":[[0,0,0],[0,1,0],[1,1,1]]}
#units_color = [(255,0,0), (255,135,0), (255,209,0), (73,179,0), (0,193,236), (166,87,255), (255,96,245)]
units_img = [load_image(f"image/square{i+1}.png", 30, 30) for i in range(7)]

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
    x = GAMEWIDTH/2+(WINDOWHEIGHT-GAMEHEIGHT)/2
    y = (WINDOWHEIGHT-GAMEHEIGHT)/2
    unit_index = random.randint(0,len(units_matrix)-1)
    unit_matrix = units_matrix[list(units_matrix.keys())[unit_index]]
    unit_pos, rows_index, cols_index = get_unit_pos(unit_matrix, x, y)
    unit_minx = x+min(cols_index)*SPACESIZE
    unit_maxx = x+max(cols_index)*SPACESIZE
    unit_miny = y-(len(unit_matrix)-1-min(rows_index))*SPACESIZE
    unit_maxy = y-(len(unit_matrix)-1-max(rows_index))*SPACESIZE
    unit_img = units_img[unit_index]
    fall_direction = (0, SPACESIZE) # the falling direction is always down
    # initiate occupation matrix
    rows = GAMEHEIGHT//SPACESIZE
    cols = GAMEWIDTH//SPACESIZE
    # initiate stacking drawing group
    matrix = [[(0, WINDOWCOLOR) for _ in range(cols)] for _ in range(rows)]
    # initiate next unit
    next_unit_index = random.randint(0,len(units_matrix)-1)
    next_unit_matrix = units_matrix[list(units_matrix.keys())[next_unit_index]]
    next_unit_pos = get_nextunit_pos(next_unit_matrix, 510, 120)
    next_unit_img = units_img[next_unit_index]

    pygame.mixer.music.play(-1,0.0)

    while gameover == False:
        move_direction = (0,0) # the initial move direction is None
        rotate = False # the initial rotate is None
        keys = pygame.key.get_pressed()
        speed = FPS
        if keys[pygame.K_DOWN]:
            speed = FPS*4
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif (event.key == K_LEFT or event.key == K_a) and (determine_border(unit_pos, matrix, "left")==True):
                    move_direction = (-SPACESIZE, 0)
                elif (event.key == K_RIGHT or event.key == K_d) and (determine_border(unit_pos, matrix, "right")==True):
                    move_direction = (SPACESIZE, 0)
                elif (event.key == K_r):
                    rotate = True 


        # check bottoming
        newunit = False
        if unit_miny >= (WINDOWHEIGHT-GAMEHEIGHT)/2:
            for square in unit_pos:
                if (square[1]//SPACESIZE-1 == len(matrix)-1 and matrix[square[1]//SPACESIZE-1][int(square[0]//SPACESIZE)-1][0] == 0) or (square[1]//SPACESIZE-1 < len(matrix)-1 and matrix[square[1]//SPACESIZE][square[0]//SPACESIZE-1][0] == 1): # unit touch the bottom or unit stack
                    for sq in unit_pos:
                        matrix[int(sq[1]//SPACESIZE)-1][int(sq[0]//SPACESIZE)-1] = (1, unit_img)
                    # if row fully occupied, remove row and get point
                    for r in range(len(matrix)-1, -1, -1):
                        rowsum = 0
                        for c in range(len(matrix[r])):
                            rowsum += matrix[r][c][0]
                        if rowsum == len(matrix[r]): # the row is fully occupied
                            matrix.pop(r)
                            matrix.insert(0, [(0,WINDOWCOLOR) for _ in range(cols)])
                            score += 1
                    # check gameover
                    for i in range(cols):
                        if matrix[0][i][0] == 1:
                            if topScore < score:
                                topScore = score 
                            gameover = True 
                            break 
                    # generate new unit
                    x = GAMEWIDTH/2+(WINDOWHEIGHT-GAMEHEIGHT)/2
                    y = (WINDOWHEIGHT-GAMEHEIGHT)/2
                    unit_index = next_unit_index
                    unit_matrix = next_unit_matrix
                    unit_pos, rows_index, cols_index = get_unit_pos(unit_matrix, x, y)
                    unit_minx = x+min(cols_index)*SPACESIZE
                    unit_maxx = x+max(cols_index)*SPACESIZE
                    unit_miny = y-(len(unit_matrix)-1-min(rows_index))*SPACESIZE
                    unit_maxy = y-(len(unit_matrix)-1-max(rows_index))*SPACESIZE
                    unit_img = units_img[unit_index]
                    # generate next unit
                    next_unit_index = random.randint(0,len(units_matrix)-1)
                    next_unit_matrix = units_matrix[list(units_matrix.keys())[next_unit_index]]
                    next_unit_pos = get_nextunit_pos(next_unit_matrix, 510, 120)
                    next_unit_img = units_img[next_unit_index]
                    newunit = True 
                    break

        # unit next position
        if newunit == False:
            x,y = int(x+fall_direction[0]+move_direction[0]), int(y+fall_direction[1]+move_direction[1])
            unit_matrix = rotate_unit(unit_matrix, x, y, matrix, rotate)
            unit_pos, rows_index, cols_index = get_unit_pos(unit_matrix, x, y)
            unit_minx = x+min(cols_index)*SPACESIZE
            unit_maxx = x+max(cols_index)*SPACESIZE
            unit_miny = y-(len(unit_matrix)-1-min(rows_index))*SPACESIZE
            unit_maxy = y-(len(unit_matrix)-1-max(rows_index))*SPACESIZE
        
        # draw game world in the window
        if gameover == False:
            windowSurface.fill(WINDOWCOLOR)
            draw_image(gameboard_img, windowSurface, GAMEWIDTH/2+(WINDOWHEIGHT-GAMEHEIGHT)/2, GAMEHEIGHT/2+(WINDOWHEIGHT-GAMEHEIGHT)/2)
            draw_image(nextunitboard_img, windowSurface, 510, 120)
            draw_image(scoreboard_img, windowSurface, 510, 360)
            draw_image(label_img, windowSurface, 510, 560)
            for r in range(len(matrix)):
                for c in range(len(matrix[r])):
                    if matrix[r][c][0] == 1:
                        drawx = c*SPACESIZE+(WINDOWHEIGHT-GAMEHEIGHT)/2
                        drawy = r*SPACESIZE+(WINDOWHEIGHT-GAMEHEIGHT)/2
                        img = matrix[r][c][1]
                        draw_image(img, windowSurface, drawx, drawy, square=True)
            # draw falling unit
            for unit in unit_pos:
                if unit[1] >= (WINDOWHEIGHT-GAMEHEIGHT)/2:
                    draw_image(unit_img, windowSurface, unit[0], unit[1], square=True)
            # draw next unit
            for sq in next_unit_pos:
                draw_image(next_unit_img, windowSurface, sq[0], sq[1], square=True)

            # draw scores
            draw_text(f"SCORE: {score}", fontscore, windowSurface, 510, 320, SCORECOLOR)
            draw_text(f"TOP: {topScore}", fontscore, windowSurface, 510, 415, SCORECOLOR)

            pygame.display.flip()
            mainClock.tick(speed)
    
    # show the game over screen
    if gameover:
        show_gameover_screen(gameoverboard_img)
    
    gameOverSound.stop()
    

