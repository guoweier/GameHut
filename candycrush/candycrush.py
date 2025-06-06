import pygame, sys, random
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 1100
WINDOWHEIGHT = 800
GAMEWIDTH = 600
GAMEHEIGHT = 600
WINDOWCOLOR = (0,0,0)
TEXTCOLOR1 = (129,115,92)
TEXTCOLOR2 = (255,255,255)
SPACESIZE = 100
FPS = 60
rows = GAMEHEIGHT//SPACESIZE
cols = GAMEWIDTH//SPACESIZE
falling_sprites = []

# set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Candycrush')
font = pygame.font.Font("fonts/GravitasOne.ttf", 36)
stepfont = pygame.font.Font("fonts/GravitasOne.ttf", 66)
goalfont = pygame.font.Font("fonts/GravitasOne.ttf", 50)
resultfont = pygame.font.Font("fonts/GravitasOne.ttf", 60)

## FUNCTION ##
# ---------- basic functions ------------ #
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
                
def load_image(file, x, y):
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, (x,y))
    return img

# -------------- draw functions -------------- #
def draw_text(text, font, surface, x, y, color):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x,y))
    surface.blit(textobj, textrect)

def draw_image(img, surface, x, y):
    if img != None:
        img_rect = img.get_rect(center=(x,y))
        surface.blit(img, img_rect)

def draw_gamewindow_static(gamestep):
    draw_image(background_img, windowSurface, 550, 400)
    draw_image(gameboard_img, windowSurface, 700, 400)
    draw_image(scorebar_img, windowSurface, 195, 400)
    draw_text(str(gamestep), stepfont, windowSurface, 195, 180, TEXTCOLOR1)
    draw_image(goal1, windowSurface, 195, 334)
    draw_image(goal2, windowSurface, 195, 548)
    goal1_count = list(gamegoal.values())[0]-list(collect_count.values())[0] if list(gamegoal.values())[0]-list(collect_count.values())[0] >= 0 else 0
    goal2_count = list(gamegoal.values())[1]-list(collect_count.values())[1] if list(gamegoal.values())[1]-list(collect_count.values())[1] >= 0 else 0
    draw_text(str(goal1_count), goalfont, windowSurface, 195, 415, TEXTCOLOR1)
    draw_text(str(goal2_count), goalfont, windowSurface, 195, 629, TEXTCOLOR1)

def draw_gameboard():
    animated_targets = {(int(y_to//SPACESIZE), col) for _, col, _, y_to, _ in falling_sprites}
    for i in range(rows):
        for j in range(cols):
            if (i,j) in animated_targets:
                continue
            candy = gameboard[i][j] if gameboard[i][j] is not None else candynone
            draw_image(candy, windowSurface, j*SPACESIZE+SPACESIZE/2+400, i*SPACESIZE+SPACESIZE/2+100)
    for candy, col, y_from, y_to, progress in falling_sprites:
        y = y_from+(y_to-y_from)*progress
        if y < -SPACESIZE/2:
            continue
        draw_image(candy, windowSurface, col*SPACESIZE+SPACESIZE/2+400, y+SPACESIZE/2+100)
    pygame.display.flip()

def draw_gameover(win):
    draw_image(gameover_img, windowSurface, 550, 400)
    msg = "YOU WIN!" if win else "YOU LOSE!"
    draw_text(msg, resultfont, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-40, TEXTCOLOR1)
    draw_text("Play Again", font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+110, TEXTCOLOR2)
    playagainbox = pygame.Rect(347, 473, 415, 68)
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
            elif event.type == MOUSEBUTTONDOWN:
                if playagainbox.collidepoint(event.pos):
                    return
                   
        pygame.display.flip()


# ---------------- system functions ------------------- #
# initiate gameboard #
def initiate_gameboard(rows, cols, candys):
    gameboard = [[None for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            possible_candys = list(candys)
            while candys:
                candy = random.choice(possible_candys)
                # check left
                if j >= 2 and gameboard[i][j-1] == gameboard[i][j-2] == candy:
                    possible_candys.remove(candy)
                    continue 
                # check up
                if i >= 2 and gameboard[i-1][j] == gameboard[i-2][j] == candy:
                    possible_candys.remove(candy)
                    continue
                gameboard[i][j] = candy
                break
    return gameboard

# resolve gameboard #
def get_cell(pos):
    x,y = pos 
    row = (y-100)//SPACESIZE
    col = (x-400)//SPACESIZE
    return row, col 

def are_nextdoor(a,b):
    r1,c1 = a 
    r2,c2 = b
    return abs(r1-r2)+abs(c1-c2) == 1

def find_matches():
    matched = set()
    # horizontal matches
    for i in range(rows):
        count = 1
        for j in range(1, cols):
            if gameboard[i][j] == gameboard[i][j-1]:
                count += 1
            else:
                if count >= 3:
                    for k in range(j-count, j):
                        matched.add((i,k))
                count = 1
        if count >= 3:
            for k in range(cols-count, cols):
                matched.add((i,k))
    # vertical matches
    for j in range(cols):
        count = 1
        for i in range(1, rows):
            if gameboard[i][j] == gameboard[i-1][j]:
                count += 1
            else:
                if count >= 3:
                    for k in range(i-count, i):
                        matched.add((k,j))
                count = 1
        if count >= 3:
            for k in range(rows-count, rows):
                matched.add((k,j))
    return matched 

def remove_matches(matches):
    for (i, j) in matches:
        gameboard[i][j] = None  

def animate_gravity():
    fall_speed = 10
    changed = True 
    while changed:
        changed = False 
        falling_sprites.clear()
        for j in range(cols):
            for i in range(rows-2, -1, -1):
                if gameboard[i][j] and gameboard[i+1][j] is None:
                    drop = 1
                    while i+drop < rows and gameboard[i+drop][j] is None:
                        drop += 1
                    drop -= 1
                    y_from = i*SPACESIZE
                    y_to = (i+drop)*SPACESIZE
                    candy = gameboard[i][j]
                    gameboard[i+drop][j] = candy
                    gameboard[i][j] = None
                    falling_sprites.append([candy, j, y_from, y_to, 0])
                    changed = True 
        if falling_sprites:
            for frame in range(SPACESIZE//fall_speed):
                for sprite in falling_sprites:
                    sprite[4] += fall_speed/SPACESIZE
                draw_gamewindow_static(gamestep)
                draw_gameboard()
                mainClock.tick(FPS)

def refill_gameboard_gravity():
    global gameboard
    falling_sprites.clear()
    for j in range(cols):
        empty_rows = []
        for i in range(rows):
            if gameboard[i][j] is None:
                empty_rows.append(i)
        for idx, row in enumerate(reversed(empty_rows)):
            candy = random.choice(candys)
            gameboard[row][j] = candy 
            y_from = -(idx+1)*SPACESIZE
            y_to = row*SPACESIZE
            falling_sprites.append([candy, j, y_from, y_to, 0])
    # animate refill falling
    fall_speed = 15
    if falling_sprites:
        for frame in range(SPACESIZE*rows//fall_speed):
            for sprite in falling_sprites:
                sprite[4] += fall_speed/(sprite[3]-sprite[2])
                sprite[4] = min(sprite[4], 1)
            draw_gamewindow_static(gamestep)
            draw_gameboard()
            mainClock.tick(FPS)

def random_candy(candys):
    return random.choice(candys)

def has_valid_move():
    for i in range(rows):
        for j in range(cols):
            current = gameboard[i][j]
            # check right 
            if j+1 < cols:
                neighbor = gameboard[i][j+1]
                gameboard[i][j], gameboard[i][j+1] = neighbor, current 
                if find_matches():
                    gameboard[i][j], gameboard[i][j+1] = current, neighbor
                    return True 
                gameboard[i][j], gameboard[i][j+1] = current, neighbor
            # check down
            if i+1 < cols:
                neighbor = gameboard[i+1][j]
                gameboard[i][j], gameboard[i+1][j] = neighbor, current
                if find_matches():
                    gameboard[i][j], gameboard[i+1][j] = current, neighbor
                    return True 
                gameboard[i][j], gameboard[i+1][j] = current, neighbor
    return False

def shuffle_gameboard():
    # flatten the gameboard
    flat = [c for row in gameboard for c in row if c is not None]
    random.shuffle(flat)
    # put back into the board
    idx = 0
    for i in range(rows):
        for j in range(cols):
            gameboard[i][j] = flat[idx]
            idx += 1

def resolve_gameboard():
    while True:
        matches = find_matches()
        if not matches:
            break 

        for (i, j) in matches:
            c = gameboard[i][j]
            if c in collect_count:
                collect_count[c] += 1

        remove_matches(matches)
        draw_gamewindow_static(gamestep)
        draw_gameboard()
        animate_gravity()
        refill_gameboard_gravity()
        draw_gamewindow_static(gamestep)
        draw_gameboard()
        while not has_valid_move():
            shuffle_gameboard()
            resolve_gameboard()

# animate swap #
def animate_swap(candy1, pos1, candy2, pos2, duration=10):
    x1 = pos1[1]*SPACESIZE
    y1 = pos1[0]*SPACESIZE
    x2 = pos2[1]*SPACESIZE
    y2 = pos2[0]*SPACESIZE
    for step in range(duration):
        t = (step+1)/duration
        # interpolated position
        cx1 = x1+(x2-x1)*t
        cy1 = y1+(y2-y1)*t
        cx2 = x2+(x1-x2)*t 
        cy2 = y2+(y1-y2)*t 
        # draw boards background elements
        draw_gamewindow_static(gamestep)
        # draw static board
        for i in range(rows):
            for j in range(cols):
                if (i,j)==pos1 or (i,j)==pos2:
                    continue 
                candy=gameboard[i][j] if gameboard[i][j] is not None else candynone 
                draw_image(candy, windowSurface, j*SPACESIZE+SPACESIZE/2+400, i*SPACESIZE+SPACESIZE/2+100)
        # draw 2 animated candies
        draw_image(candy1, windowSurface, cx1+SPACESIZE/2+400, cy1+SPACESIZE/2+100)
        draw_image(candy2, windowSurface, cx2+SPACESIZE/2+400, cy2+SPACESIZE/2+100)

        pygame.display.flip()
        mainClock.tick(FPS)

# gameover #
def check_gameover():
    win = all(collect_count[c] >= gamegoal[c] for c in gamegoal)
    lose = gamestep <= 0 and not win 
    return win, lose 

## IMAGES ##
background_img = load_image("image/background.png", 1100, 800)
gameboard_img = load_image("image/gameboard.png", 620, 620)
scorebar_img = load_image("image/scorebar.png", 210, 620)
candys = [load_image(f"image/candy{i+1}.png", 80, 80) for i in range(6)]
candynone = load_image("image/candy7.png", 80, 80)
gameover_img = load_image("image/gameover.png", 1100, 800)

## WINDOW1: START WINDOW ##
draw_image(background_img, windowSurface, 550, 400)
draw_text('Welcome to candycrush!', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-50, TEXTCOLOR1)
draw_text('Press ENTER to start.', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery, TEXTCOLOR1)
pygame.display.update()
start_game()

# game loop
start_cell = None 
while True:
    ## WINDOW2: GAME PLAYING WINDOW ##
    draw_image(background_img, windowSurface, 550, 400)
    gameboard = initiate_gameboard(rows, cols, candys)
    gameover = False
    gamestep = 12
    goalnums = random.sample(range(6),2)
    goal1_idx = goalnums[0]
    goal2_idx = goalnums[1]
    goal1 = candys[goal1_idx]
    goal2 = candys[goal2_idx]
    gamegoal = {goal1: 9, goal2: 9}
    collect_count = {goal1: 0, goal2: 0}
    while gameover == False:
        draw_gamewindow_static(gamestep)
        draw_gameboard()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONDOWN:
                start_cell = get_cell(event.pos)
            elif event.type == MOUSEBUTTONUP:
                if start_cell:
                    end_cell = get_cell(event.pos)
                    if are_nextdoor(start_cell, end_cell):
                        r1,c1 = start_cell
                        r2,c2 = end_cell
                        candy1 = gameboard[r1][c1]
                        candy2 = gameboard[r2][c2]
                        animate_swap(candy1, (r1,c1), candy2, (r2,c2))
                        gameboard[r1][c1], gameboard[r2][c2] = candy2, candy1

                        if find_matches():
                            resolve_gameboard()
                            gamestep -= 1
                            win, lose = check_gameover()
                            if win or lose:
                                gamestep = gamestep if win else 0
                                draw_gamewindow_static(gamestep)
                                draw_gameboard()
                                gameover = True 
                                break 
                        else:
                            animate_swap(candy2, (r2, c2), candy1, (r1, c1))
                            gameboard[r1][c1], gameboard[r2][c2] = candy1, candy2
                    start_cell = None 
    ## WINDOW3: GAMEOVER WINDOW ##
    if gameover == True:
        draw_gameover(win)


