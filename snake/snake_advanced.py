import pygame, sys, random
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 640
WINDOWHEIGHT = 700
WINDOWCOLOR = (120,172,75)
GAMEWIDTH = 600
GAMEHEIGHT = 600
GAMELEFT = (WINDOWWIDTH-GAMEWIDTH)/2
GAMERIGHT = (WINDOWWIDTH+GAMEWIDTH)/2
GAMETOP = WINDOWHEIGHT-(WINDOWWIDTH+GAMEHEIGHT)/2
GAMEBOTTOM = WINDOWHEIGHT-(WINDOWWIDTH-GAMEHEIGHT)/2
TEXTCOLOR = (255,255,255)
FPS = 10
SPACESIZE = 30
SNAKELENGTH = 3

# set up pygame, the window
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Snake')
pygame.mouse.set_visible(False)

## CLASS ##
class Sprites(pygame.sprite.Sprite):
    def __init__(self, frames, speed=2):
        super().__init__()
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        self.timer = 0
        self.speed = speed

    def update(self):
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index+1) % len(self.frames)
            self.image = self.frames[self.index]

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

def load_image(file, x, y):
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, (x,y))
    return img

def scale_image(image, x, y, units):
    scaled_images = []
    for i in range(len(units)):
        image_scale = pygame.transform.scale(image, (x+units[i],y+units[i]))
        scaled_images.append(image_scale)
    return scaled_images

def draw_image(img, surface, x, y):
    img_rect = img.get_rect(center=(x,y))
    surface.blit(img, img_rect)

def rotate_image(direction, image):
    if direction == (-SPACESIZE, 0): # left
        image_rt = pygame.transform.rotate(image, 0)
    elif direction == (SPACESIZE, 0): # right
        image_rt = pygame.transform.rotate(image, 180)
    elif direction == (0, -SPACESIZE): # up
        image_rt = pygame.transform.rotate(image, -90)
    elif direction == (0, SPACESIZE): # up
        image_rt = pygame.transform.rotate(image, 90)
    return image_rt

def draw_sprite(sprite, x, y, surface, direction=(-SPACESIZE, 0)):
    sprite.update()
    img_rt = rotate_image(direction, sprite.image)
    draw_image(img_rt, surface, x, y)

def draw_scorebar(score, topScore, surface):
    draw_image(score_img, surface, 40, 40)
    draw_text(f"{score}", font, surface, 75, 40)
    draw_image(topscore_img, surface, 150, 40)
    draw_text(f"{topScore}", font, surface, 185, 40)

def snakehead_openmouth(dx, dy):
    if abs(dx)+abs(dy) == 3*SPACESIZE:
        return snakehead_frames[1]
    elif abs(dx)+abs(dy) == 2*SPACESIZE:
        return snakehead_frames[2]
    elif abs(dx)+abs(dy) <= SPACESIZE:
        return snakehead_frames[3]
    else:
        return snakehead_frames[0]

def choose_turn_img(dx1, dy1, dx2, dy2):
    if ((dx1, dy1) == (0, -SPACESIZE) and (dx2, dy2) == (-SPACESIZE, 0)) or ((dx1, dy1) == (SPACESIZE, 0) and (dx2, dy2) == (0, SPACESIZE)): # up -> left & right -> down
        return snakebody_turn_frames[0]
    elif ((dx1, dy1) == (0, -SPACESIZE) and (dx2, dy2) == (SPACESIZE, 0)) or ((dx1, dy1) == (-SPACESIZE, 0) and (dx2, dy2) == (0, SPACESIZE)): # up -> right & left -> down
        return snakebody_turn_frames[1]
    elif ((dx1, dy1) == (0, SPACESIZE) and (dx2, dy2) == (-SPACESIZE, 0)) or ((dx1, dy1) == (SPACESIZE, 0) and (dx2, dy2) == (0, -SPACESIZE)): # down -> left & right -> up
        return snakebody_turn_frames[2]
    elif ((dx1, dy1) == (0, SPACESIZE) and (dx2, dy2) == (SPACESIZE, 0)) or ((dx1, dy1) == (-SPACESIZE, 0) and (dx2, dy2) == (0, -SPACESIZE)): # down -> right & left -> up
        return snakebody_turn_frames[3]
    
def define_gameover_snakehead_direction(snake):
    x1,y1 = snake[0]
    x2,y2 = snake[1]
    dx = x1-x2
    dy = y1-y2
    if dx == -SPACESIZE and dy == 0: # left
        direction = (-SPACESIZE, 0)
    elif dx == SPACESIZE and dy == 0: # right
        direction = (SPACESIZE, 0)
    elif dx == 0 and dy == -SPACESIZE: # up
        direction = (0, -SPACESIZE)
    elif dx == 0 and dy == SPACESIZE: # down
        direction = (0, SPACESIZE)
    return direction

def add_collision_snaketail(snake):
    tx, ty = snake[len(snake)-1][0], snake[len(snake)-1][1]
    tpx, tpy = snake[len(snake)-2][0], snake[len(snake)-2][1]
    dx, dy = tx-tpx, ty-tpy
    if dx == 0 and dy == SPACESIZE: # bottom
        newtail_pos = (tx, ty+SPACESIZE)
        newtail_img = pygame.transform.rotate(snaketail_img, 90)
        oldtail_img = snakebody_ver_img
    elif dx == 0 and dy == -SPACESIZE: # top
        newtail_pos = (tx, ty-SPACESIZE)
        newtail_img = pygame.transform.rotate(snaketail_img, -90)
        oldtail_img = snakebody_ver_img
    elif dx == -SPACESIZE and dy == 0: # left
        newtail_pos = (tx-SPACESIZE, ty)
        newtail_img = pygame.transform.rotate(snaketail_img, 0)
        oldtail_img = snakebody_hor_img
    elif dx == SPACESIZE and dy == 0: # right
        newtail_pos = (tx+SPACESIZE, ty)
        newtail_img = pygame.transform.rotate(snaketail_img, 180)
        oldtail_img = snakebody_hor_img
    oldtail_pos = (tx,ty)
    return (newtail_img, newtail_pos, oldtail_img, oldtail_pos)

def draw_snakebody(surface):
    for i in range(1, len(snake)-1):
        prev = snake[i - 1]
        curr = snake[i]
        nxt = snake[i + 1]
        # check directions
        dx1, dy1 = curr[0] - prev[0], curr[1] - prev[1]
        dx2, dy2 = nxt[0] - curr[0], nxt[1] - curr[1]
        if dx1 == dx2 and dy1 == dy2:
            # straight segment
            if dx1 != 0: # horizontal
                draw_image(snakebody_hor_img, surface, curr[0], curr[1])
            else: # vertical
                draw_image(snakebody_ver_img, surface, curr[0], curr[1])
        else: # choose corner
            turn_img = choose_turn_img(dx1, dy1, dx2, dy2)
            draw_image(turn_img, surface, curr[0], curr[1])

def draw_snaketail(surface):
    tx, ty = snake[len(snake)-1][0], snake[len(snake)-1][1]
    txp, typ = snake[len(snake)-2][0], snake[len(snake)-2][1]
    tdx, tdy = tx-txp, ty-typ
    if tdx > 0: # left
        snake_tail_img_rt = pygame.transform.rotate(snaketail_img, 0)
    elif tdx < 0: # right
        snake_tail_img_rt = pygame.transform.rotate(snaketail_img, 180)
    elif tdy > 0: # up
        snake_tail_img_rt = pygame.transform.rotate(snaketail_img, -90)
    elif tdy < 0: # down
        snake_tail_img_rt = pygame.transform.rotate(snaketail_img, 90)
    draw_image(snake_tail_img_rt, surface, snake[len(snake)-1][0], snake[len(snake)-1][1])

def create_gameover_statics():
    # update background
    surface = pygame.Surface((WINDOWWIDTH,WINDOWHEIGHT))
    surface.fill(WINDOWCOLOR)
    draw_image(game_background_img, surface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+30)
    # draw food
    draw_sprite(food_sprite, food_pos[0], food_pos[1], surface)
    # draw snake body with turns
    draw_snakebody(surface)
    # draw snake tail
    draw_snaketail(surface)
    # draw scorebar
    draw_scorebar(score, topScore, surface)
    # show score board
    board_shadow = pygame.Surface((400,300))
    board_shadow.fill((0,0,0))
    board_shadow.set_alpha(70)
    draw_image(board_shadow, surface, windowSurface.get_rect().centerx+5, windowSurface.get_rect().centery+5)
    draw_image(scoreboard_img, surface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery)
    draw_text(f"{score}", font, surface, windowSurface.get_rect().centerx-100, windowSurface.get_rect().centery-60)
    draw_text(f"{score}", font, surface, windowSurface.get_rect().centerx+100, windowSurface.get_rect().centery-60)
    draw_text("Press ENTER to play again.", font, surface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+110)
    return surface

def show_gameover_screen():
    pygame.mixer.music.stop()
    gameOverSound.play()

    snake.pop(0)
    tails = add_collision_snaketail(snake)
    snake.append(tails[1])

    statics = create_gameover_statics()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                    return
                elif event.key == K_RETURN or event.key == K_SPACE:
                    return
        
        # draw blink snakehead
        draw_sprite(snakehead_gameover_sprite, snake[0][0], snake[0][1], statics, direction)
        # draw statics elements
        windowSurface.blit(statics, (0,0))
        
        pygame.display.update()
        mainClock.tick(FPS)

## IMAGE ##
# game background
game_background_img = load_image("image/background.png", GAMEWIDTH, GAMEHEIGHT)
# food
food_img = pygame.image.load("image/food.png")
food_scale_units = [0, 2.5, 5, 7.5, 10, 7.5, 5, 2.5]
food_frames = scale_image(food_img, 30, 30, food_scale_units)
food_sprite = Sprites(food_frames, speed=2)
# snake
snakehead_frames = [load_image(f"image/snakehead{i+1}.png", 42.85, 42.85) for i in range(4)]
snakebody_hor_img = load_image("image/snakebody_horizontal.png", 30, 30)
snakebody_ver_img = load_image("image/snakebody_vertical.png", 30, 30)
snakebody_turn_frames = [load_image(f"image/snakebody_turn{i+1}.png", 30, 30) for i in range(4)]
snaketail_img = load_image("image/snaketail.png", 30, 30)
# gameover snake
snakehead_gameover_frames = [load_image(f"image/snakehead_over{i+1}.png", 42.85, 42.85) for i in range(4)]
snakehead_gameover_sprite = Sprites(snakehead_gameover_frames, speed=3)
# score
score_img = load_image("image/food.png", 30, 30)
topscore_img = load_image("image/champ.png", 30, 30)
scoreboard_img = load_image("image/scoreboard.png", 400, 300)

## SOUND ##
gameOverSound = pygame.mixer.Sound('music/gameover.mp3')
pygame.mixer.music.load('music/Soundbackground_CasaRosa.mp3')

## FONT ##
font = pygame.font.SysFont(None, 36)

## WINDOW1: START WINDOW ##
windowSurface.fill(WINDOWCOLOR)
draw_text('Welcome to the Snake!', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-50)
draw_text('Press ENTER to start.', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery)
pygame.display.update()
start_game()

## GAME LOOP ##
topScore = 0
while True:
    gameover = False
    score = 0
    windowSurface.fill(WINDOWCOLOR)
    draw_image(game_background_img, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+30)
    # initiate food
    food_pos = (random.randint(0,((GAMEWIDTH//SPACESIZE)-1))*SPACESIZE+0.5*SPACESIZE+GAMELEFT, random.randint(0,((GAMEHEIGHT//SPACESIZE)-1))*SPACESIZE+0.5*SPACESIZE+GAMETOP)
    # initiate snake
    snake = []
    snakeX = GAMEWIDTH/2
    snakeY = GAMEHEIGHT/2
    for i in range(SNAKELENGTH):
        snake.append((snakeX+(i+0.5)*SPACESIZE+GAMELEFT, snakeY+0.5*SPACESIZE+GAMETOP))
    direction = (-SPACESIZE, 0) # the initial direction is left
    pygame.mixer.music.play(-1,0.0)

    ## WINDOW2: GAME WINDOW ##
    while gameover == False:
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
        if new_head == food_pos:
            food_pos = (random.randint(0,((GAMEWIDTH//SPACESIZE)-1))*SPACESIZE+0.5*SPACESIZE+GAMELEFT, random.randint(0,((GAMEHEIGHT//SPACESIZE)-1))*SPACESIZE+0.5*SPACESIZE+GAMETOP)
            score += 1
        else:
            snake.pop() # remove the last part if no food eaten
    
        if new_head[0] < GAMELEFT or new_head[0] >= GAMERIGHT or new_head[1] < GAMETOP or new_head[1] >= GAMEBOTTOM or new_head in snake[1:]:
            if score > topScore:
                topScore = score
            gameover = True
            break

        # draw the game world on the window
        windowSurface.fill(WINDOWCOLOR)
        draw_image(game_background_img, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery+30)
        # draw score bar on top
        draw_scorebar(score, topScore, windowSurface)
        # draw food
        draw_sprite(food_sprite, food_pos[0], food_pos[1], windowSurface)
        # draw snake head
        snakehead_pos = snake[0]
        head_food_dx, head_food_dy = snakehead_pos[0]-food_pos[0], snakehead_pos[1]-food_pos[1]
        snake_head_img = snakehead_openmouth(head_food_dx, head_food_dy)
        snake_head_img_rt = rotate_image(direction, snake_head_img)
        draw_image(snake_head_img_rt, windowSurface, snake[0][0], snake[0][1])
        # draw snake body with turns
        draw_snakebody(windowSurface)
        # draw snake tail
        draw_snaketail(windowSurface)
        
        pygame.display.flip()
        mainClock.tick(FPS)

    ## WINDOW3: GAMEOVER WINDOW ##
    if gameover:
        show_gameover_screen()

    gameOverSound.stop()
