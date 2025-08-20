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
scorefont = pygame.font.Font("font/Micro5.ttf", 72)

## FUNCTION ##
# ---------- basic functions ------------ #
def terminate():
    pygame.quit()
    sys.exit()

def reset_game():
    global bird_rect, bird_movement, pipe_list, score, bird_index
    pipe_list.clear()
    bird_rect.center = (WINDOWWIDTH//2, WINDOWHEIGHT//2)
    bird_movement = 0
    score = 0

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
def get_subset_pipe(pipe_img, height, pos):
    if pos == "top":
        pipe_crop = pipe_img.subsurface(pygame.Rect(0, pipe_img.get_height()-height, pipe_img.get_width(), height))
    elif pos == "bottom":
        pipe_crop = pipe_img.subsurface(pygame.Rect(0, 0, pipe_img.get_width(), height))
    return pipe_crop

def create_pipe(pipe_gap):
    top_pipe_height = random.randint(0, GAMEHEIGHT-pipe_gap)
    pipetop_surface = get_subset_pipe(pipe_top_img, top_pipe_height, "top")
    pipebottom_surface = get_subset_pipe(pipe_bottom_img, GAMEHEIGHT-pipe_gap-top_pipe_height, "bottom")
    pipetop_rect = pipetop_surface.get_rect(topleft=(WINDOWWIDTH, 0))
    pipebottom_rect = pipebottom_surface.get_rect(topleft=(WINDOWWIDTH, top_pipe_height+pipe_gap))
    return [(pipebottom_surface, pipebottom_rect, False), (pipetop_surface, pipetop_rect, False)]

def check_collision(pipes):
    for pipe, pipe_rect, _ in pipes:
        if bird_rect.colliderect(pipe_rect):
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= GAMEHEIGHT:
        return False 
    return True 

def _show_score(score, x, y):
    score_shadow = scorefont.render(f"{score}", True, SHADOWCOLOR)
    score_surface = scorefont.render(f"{score}", True, TEXTCOLOR)
    draw_image(score_shadow, windowSurface, x+2, y+2)
    draw_image(score_surface, windowSurface, x, y)

def display_score(score, game_active, best_score=0):
    if game_active:
        _show_score(score, WINDOWWIDTH//2, GAMEHEIGHT//2-150)
    else:
        _show_score(score, WINDOWWIDTH//2, GAMEHEIGHT//2-28)
        _show_score(best_score, WINDOWWIDTH//2, GAMEHEIGHT//2+42)
    
## VARIABLES ##
game_active = True
start_screen = True
score = 0
best_score = 0

# background
background_img = load_image("image/background.png", 477, 633).convert_alpha()

# bird
birds = [load_image(f"image/bird{i+1}.png", 51, 36).convert_alpha() for i in range(3)]
bird_index = 0
bird_surface = birds[bird_index]
bird_rect = bird_surface.get_rect(center=(WINDOWWIDTH//2, GAMEHEIGHT//2))
frame_count = 0
bird_movement = 0
gravity = 0.375
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

bird_gameover = load_image("image/bird_gameover.png", 36, 51)
bird_gameover_rect = bird_gameover.get_rect(center=(WINDOWWIDTH//2, GAMEHEIGHT-20))

# pipe
pipe_top_img = load_image("image/pipe_top.png", 84, 552)
pipe_bottom_img = load_image("image/pipe_bottom.png", 84, 552)
pipe_gap = 150
pipe_speed = 3
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

# buttons
start_button_img = load_image("image/start.png", 132, 45).convert_alpha()
start_button_rect = start_button_img.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2+100))
restart_button_img = load_image("image/restart.png", 132, 45).convert_alpha()
restart_button_rect = restart_button_img.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2+100))

# scoreboard
scoreboard_img = load_image("image/scoreboard.png", 144, 180).convert_alpha()
scoreboard_rect = scoreboard_img.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2-50))

## WINDOW1: START WINDOW ##
while start_screen:
    mouse_click = False
    mouse_pos = pygame.mouse.get_pos()
    hovered = start_button_rect.collidepoint(mouse_pos)
    scale_factor = 1.1 if hovered else 1.0
    start_button_width = int(start_button_img.get_width() * scale_factor)
    start_button_height = int(start_button_img.get_height() * scale_factor)
    start_button_img_scaled = pygame.transform.smoothscale(start_button_img, (start_button_width, start_button_height))
    start_button_rect_scaled = start_button_img_scaled.get_rect(center=start_button_rect.center)

    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            terminate()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True 
    
    # update bird animation
    frame_count += 1
    if frame_count % 10 == 0:
        bird_index = (bird_index + 1) % len(birds)
    bird_surface = birds[bird_index]
    bird_base_y = GAMEHEIGHT//2
    bounce_offset = math.sin(frame_count * 0.1) * 8
    bird_rect.centery = bird_base_y + int(bounce_offset)

    # draw background, bird, start button
    draw_image(background_img, windowSurface, 238.5, 316.5)
    windowSurface.blit(bird_surface, bird_rect)
    windowSurface.blit(start_button_img_scaled, start_button_rect_scaled)

    # hover effect
    if start_button_rect.collidepoint(mouse_pos):
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
    hovered = restart_button_rect.collidepoint(mouse_pos)
    scale_factor = 1.1 if hovered else 1.0
    restart_button_width = int(restart_button_img.get_width() * scale_factor)
    restart_button_height = int(restart_button_img.get_height() * scale_factor)
    restart_button_img_scaled = pygame.transform.smoothscale(restart_button_img, (restart_button_width, restart_button_height))
    restart_button_rect_scaled = restart_button_img_scaled.get_rect(center=restart_button_rect.center)

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
            pipe_list.extend(create_pipe(pipe_gap))
        if event.type == BIRDFLAP and game_active:
            bird_index = (bird_index + 1) % len(birds)
            bird_surface = birds[bird_index]
            bird_rect = bird_surface.get_rect(center=bird_rect.center)

    draw_image(background_img, windowSurface, 238.5, 316.5)

    ## WINDOW2: GAME WINDOW ##
    if game_active:
        # bird
        bird_movement += gravity
        bird_rect.centery += int(bird_movement)
        windowSurface.blit(bird_surface, bird_rect)

        # pipes
        new_pipe_list = []
        for pipe, pipe_rect, scored in pipe_list:
            pipe_rect.centerx -= pipe_speed
            if pipe_rect.right > 0:
                new_pipe_list.append((pipe, pipe_rect, scored))

            # check for scoring
            if pipe_rect.centerx < bird_rect.centerx and not scored:
                score += 0.5 
                new_pipe_list[-1] = (pipe, pipe_rect, True)
        pipe_list = new_pipe_list
        for pipe, pipe_rect, _ in pipe_list:
            windowSurface.blit(pipe, pipe_rect)
        display_score(int(score), game_active)

        # collision
        game_active = check_collision(pipe_list)

    ## WINDOW3: GAMEOVER WINDOW ##
    else:
        # draw pipe, bird, scoreboard, scores
        for pipe, pipe_rect, _ in pipe_list:
            windowSurface.blit(pipe, pipe_rect)
        windowSurface.blit(bird_gameover, bird_gameover_rect)
        windowSurface.blit(scoreboard_img, scoreboard_rect)
        if int(score) > best_score:
            best_score = int(score)
        display_score(int(score), game_active, int(best_score))
        windowSurface.blit(restart_button_img_scaled, restart_button_rect_scaled)

        # cursor hover effect
        if restart_button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
            if hovered and mouse_click:
                reset_game()
                game_active = True
        else:
            pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)
        
    pygame.display.update()
    mainClock.tick(60)

