import pygame, sys, random, math
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 477
WINDOWHEIGHT = 633
GAMEHEIGHT = 552
WINDOWCOLOR = (57,57,57)
TEXTCOLOR = (255,255,255)
SHADOWCOLOR = (79,79,79)

## PYGAME INITIALS ##
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Flappybird')

## FONTS ##
textfont = pygame.font.Font("font/Tiny5.ttf", 24)

## FUNCTION ##
# ---------- basic functions ------------ #
def terminate():
    pygame.quit()
    sys.exit()

def reset_game():
    global bird_rect, bird_movement, pipe_list, bird_index
    pipe_list.clear()
    bird_rect.center = (WINDOWWIDTH//2, WINDOWHEIGHT//2)
    bird_movement = 0

def load_image(file, x, y):
    img = pygame.image.load(file)
    img = pygame.transform.scale(img, (x,y))
    return img

# ---------- draw functions ------------ #
def draw_image(img, surface, x, y):
    if img != None:
        img_rect = img.get_rect(center=(x,y))
        surface.blit(img, img_rect)

# ---------- system functions ------------ #
def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(windowSurface, pipe_color, pipe)

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= pipe_speed
    return [pipe for pipe in pipes if pipe.right > 0]

def create_pipe():
    height = random.randint(150, 400)
    bottom = pygame.Rect(WINDOWWIDTH, height, pipe_width, WINDOWHEIGHT - height)
    top = pygame.Rect(WINDOWWIDTH, height - pipe_gap - WINDOWHEIGHT, pipe_width, WINDOWHEIGHT)
    return bottom, top

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= WINDOWHEIGHT:
        return False 
    return True 
    
## VARIABLES ##
game_active = True
start_screen = True

# bird
bird_surface = pygame.Surface((34, 24))  # Placeholder bird
bird_surface.fill((255, 255, 0))
bird_rect = bird_surface.get_rect(center=(100, WINDOWHEIGHT // 2))
bird_movement = 0
gravity = 0.375

# pipe
pipe_width = 70
pipe_gap = 150
pipe_color = (0, 255, 0)
pipe_speed = 3
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

# buttons
button_surface = textfont.render("START", 1, TEXTCOLOR)
button_rect = button_surface.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))


## WINDOW1: START WINDOW ##
while start_screen:
    mouse_click = False
    mouse_pos = pygame.mouse.get_pos()
    hovered = button_rect.collidepoint(mouse_pos)

    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            terminate()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True 

    # draw background, bird, start button
    windowSurface.blit(button_surface, button_rect)

    # cursor hover effect
    if button_rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
        if hovered and mouse_click:
            start_screen = False
    else:
        pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)

    pygame.display.update()
    pygame.time.Clock().tick(60)


## WINDOW2&3 ##
while True:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    hovered = button_rect.collidepoint(mouse_pos)

    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()
            if event.key == K_SPACE and game_active:
                bird_movement = -7.5
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    windowSurface.fill(WINDOWCOLOR)
    ## WINDOW2: GAME WINDOW ##
    if game_active:
        # bird
        bird_movement += gravity
        bird_rect.centery += int(bird_movement)
        windowSurface.blit(bird_surface, bird_rect)

        # pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # collision
        game_active = check_collision(pipe_list)

    ## WINDOW3: GAMEOVER WINDOW ##
    else:
        windowSurface.blit(button_surface, button_rect)

        # cursor hover effect
        if button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
            if hovered and mouse_click:
                reset_game()
                game_active = True
        else:
            pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)
        
    pygame.display.update()
    mainClock.tick(60)

