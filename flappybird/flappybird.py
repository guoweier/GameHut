import pygame, sys, random
from pygame.locals import *

## PARAMETERS ##
WINDOWWIDTH = 500
WINDOWHEIGHT = 600
WINDOWCOLOR = (57,57,57)
TEXTCOLOR = (255,255,255)

## PYGAME INITIALS ##
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Flappybird')

## FONTS ##
font = pygame.font.SysFont(None, 36)

## VARIABLES ##
gravity = 0.375
bird_movement = 0
game_active = True
score = 0

# bird
bird_surface = pygame.Surface((34, 24))  # Placeholder bird
bird_surface.fill((255, 255, 0))
bird_rect = bird_surface.get_rect(center=(100, WINDOWHEIGHT//2))

# pipe
pipe_width = 70
pipe_gap = 150
pipe_color = (0, 255, 0)
pipe_speed = 2
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)


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

# ---------- draw functions ------------ #
def draw_text(text, font, surface, x, y, color):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x,y))
    surface.blit(textobj, textrect)

# ---------- system functions ------------ #
def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(windowSurface, pipe_color, pipe)

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= pipe_speed
    return [pipe for pipe in pipes if pipe.right > 0]

def check_collision(pipes):
    for pipe, _ in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= WINDOWHEIGHT:
        return False 
    return True 

def display_score(score):
    score_surface = font.render(f"Score: {score}", True, TEXTCOLOR)
    windowSurface.blit(score_surface, (10,10))

def create_pipe():
    height = random.randint(150, 400)
    bottom = pygame.Rect(WINDOWWIDTH, height, pipe_width, WINDOWHEIGHT-height)
    top = pygame.Rect(WINDOWWIDTH, height-pipe_gap-WINDOWHEIGHT, pipe_width, WINDOWHEIGHT)
    return [(bottom, False), (top, False)]


## WINDOW1: START WINDOW ##
windowSurface.fill(WINDOWCOLOR)
draw_text('Welcome to the Flappy Bird!', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery-50, TEXTCOLOR)
draw_text('Press ENTER to start.', font, windowSurface, windowSurface.get_rect().centerx, windowSurface.get_rect().centery, TEXTCOLOR)
pygame.display.update()
start_game()


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()
            if event.key == K_SPACE and game_active:
                bird_movement = -7.5
            if event.key == K_SPACE and not game_active:
                # reset game
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, WINDOWHEIGHT//2)
                bird_movement = 0
                score = 0

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    windowSurface.fill(WINDOWCOLOR)

    if game_active:
        # bird
        bird_movement += gravity
        bird_rect.centery += int(bird_movement)
        windowSurface.blit(bird_surface, bird_rect)

        # pipes
        new_pipe_list = []
        for pipe, scored in pipe_list:
            pipe.centerx -= pipe_speed
            if pipe.right > 0:
                new_pipe_list.append((pipe, scored))

            # check for scoring
            if pipe.centerx < bird_rect.centerx and not scored:
                score += 0.5 
                new_pipe_list[-1] = (pipe, True)
        display_score(int(score))
        pipe_list = new_pipe_list
        for pipe, _ in pipe_list:
            pygame.draw.rect(windowSurface, pipe_color, pipe)

        # collision
        game_active = check_collision(pipe_list)
    else:
        game_over_surface = font.render("Game Over", True, TEXTCOLOR)
        windowSurface.blit(game_over_surface, (WINDOWWIDTH//10, WINDOWHEIGHT//2))
        
    pygame.display.update()
    mainClock.tick(60)

                


