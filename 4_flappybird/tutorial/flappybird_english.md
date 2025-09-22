# Programming Learning Project 4: I made Flappy Bird with Python

Today, I am going to introduce my 4th Programming Learning Project: Making Flappy Bird with Python. 
Flappy Bird is a pixel-style action game. Players control a bird in flight and must avoid the green pipes. Each time the bird successfully passes through a pair of pipes, the player earns 1 point; if the bird collides with an obstacle, the game is over. 
The program for Flappy Bird is relatively simple, and can basically be implemented using Python. Therefore, I tried to recreate all of the game's core elements. 
Now, let's take a look at the stepby-step guide for my procedure. 

## STEP1: Design
I designed 3 windows:
1. window1: start window
2. window2: game running window
3. window3: gameover window
![Figure1. sketch of 3 windows]()<br>

## STEP2: Make a simple version of the game 
### 1. Build pseudo-code
Figure 2 illustrates the relationship between 3 windows. 
![Figure2. workflow of 3 windows]()<br>
a. Start the program and display window1
b. window1 has a start button. When the player clicks it, the game enters window2. 
c. window2 runs the game. When the player dies, it switches to window3. 
d. window3 has a "Play Again" button. When the player clicks it, the game returns to window2. 

We can see that window1 only appears once, and afterward window2 and window3 keep alternating. Therefore, we can write window1 separately, while keeping window2 and window3 connected to each other. In that case, we can set up a pseudo-code framework like this: 
```
# window1
code for window1

# window2&3 
while program_running:
    if game_active: 
        code for window2
        if gameover:
            game_active = False
    else:
        code for window3
        if player_click_restart:
            game_active = True
```
I set up a variable called `game_acitve`. 
While window2 is running, if the game ends, then `game_active = False`, and the program moves to window3. 
While window3 is running, if the player clicks the "Play Again" button, then `game_active = True`, and the program returns to window2. 

With this, the main framework of the game is complete. Next, let's start filling in the details. 

### 2. window2：game running
window2 is the main part of the game. It contains following elements:
| 内容 | 属性 |
|-----|------|
| 小鸟 | 具备翅膀震颤动画；会自然下落；按空格键向上飞行一次 |
| 管道 | 从右向左移动；每组管道分为上下两个，中间有间隔，间隔位置随机 |
| 游戏规则 | 若小鸟撞到障碍物，游戏结束 |
![Figure3. table of window2 elements]()<br>

#### 1. Bird
The bird's moving mechanics are as follows:
a. When there is no input, the bird naturally falls downward. 
b. When the player presses the spacebar, the bird flies upward for a short distance, then starts falling again. 

We can represent the entire game window using a coordinate system, with the top-left corner as the origin, the horizontal axis as the x-axis, and the vertical axis as the y-axis. 
Thus, the bird's position can be expressed with 2 number (x,y). 
The bird's natural fall corresponds to an incrase in the y value, while flying upward corresponds to a decrease in the y value. 
![Figure4. xy-system for the window and the bird movement]()<br>
Therefore, I use `bird_movement` to represent the bird's motion, with its initial value set to 0. 
```
bird_movement = 0
```
Next, I use `gravity` to represent gravity. Since the bird is always affected by gravity, it will keep falling. This value determines the difficulty of the game. After multiple rounds of testing, I set it to 0.375. 
```
gravity = 0.375
```
When the player presses the spacebar, the bird moves upward by a certain distance. This value also affects the difficulty of the game. I ultimately set it to -7.5. 
```
# When the player click the SPACE button
if event.type == KEYDOWN and event.key == K_SPACE: 
    # bird move upward
    bird_movement = -7.5 
```
Next, we combine these variables together to implement the bird's flying animation. 
First, the animation effect of the game is essentially the system continuously drawing the bird at the specific position in a loop. 
Suppose at the initial time t = 0, teh bird is at (100, 100). The system will draw a bird at position (100, 100). 
At t = 1, the bird is affected by gravity. The x value remains the same at 100, while y = 100 + 0.375 = 100.375. So the system will draw a bird at (100, 100.375). 
At t = 2, the player presses the space bar. The x value still doesn't change, while y = 100.375 + 0.375 - 7.5 = 93.25. So the system will draw a bird at (100, 93.25). 
Therefore, we notice that the x value always remains constant, while the y value depends on the previous y and the movement at the current time step. This means that when drawing the bird, we only need to keep updating the current y value. 
```
# bird move downwards 0.375 because of gravity
bird_movement += gravity 
# bird y value + bird movement 
bird_rect.centery += int(bird_movement) 
# draw bird in window2 
windowSurface.blit(bird_surface, bird_rect) 
```

#### 2. Pipe
The properties of pipes:
a. Pipes are continuously genreated. 
b. They move from right to left

First, let's implement the requirement of continuous pipe generation. 
Here, I use `USEREVENT` to define a custom event and nae it SPAWNPIPE. I then set a time interval of 1500 milliseconds. Every 1500 ms, this event is triggered. 
When the game loop starts, each time a SPAWNPIPE event is triggered, a new pipe is added to the `pipe_list`. 
```
# define a list
pipe_list = []
# define an event for pipes generation 
SPAWNPIPE = pygame.USEREVENT 
# Every 1500ms, the event triggered
pygame.time.set_timer(SPAWNPIPE, 1500) 

# When SPAWNPIPE triggered
if event.type == SPAWNPIPE：
    # add a new pipe to the list
    pipe_list.extend(create_pipe(pipe_gap))
```
Here I wrap all the code for generating pipes into a single function: create_pipe(). This helps keep the code clean and organized.
Since the code inside create_pipe() also contains other nested functions, it’s a bit complex, so I won’t go into detail here. If you’re interested, you can check out my source code (the link is at the end).

Next, let’s complete the requirement of moving the pipes from right to left.
This concept is actually similar to the bird’s movement—it’s just about changing the x value. Moving from right to left means the x value keeps decreasing.

Here I set the pipe movement speed to 3. Then, for each pipe in pipe_list, I take its current x value and subtract 3, which gives its new x position at the current moment.

Once the positions are determined, we draw all the pipes onto the game screen.
```
# pipe moving speed
pipe_speed = 3
# list every pipe (pipe is the image, pipe_rect is the position, scored is for scoring)
for pipe, pipe_rect, scored in pipe_list:
    # pipe's x value - pipe speed 
    pipe_rect.centerx -= pipe_speed

# list every pipe 
for pipe, pipe_rect, _ in pipe_list:
    # draw every pipe on specific position 
    windowSurface.blit(pipe, pipe_rect)
```

#### 3. Game Rule 
In the simplified version of the game, we only consider one game-over condition: when the bird collides with an obstacle, the game ends.

In the first part, when building the main framework, we already introduced a variable game_active, which can be used to check whether the game is over. Now, we need to add the code for detecting collisions between the bird and the pipes.

Here, I use a built-in pygame function: colliderect(). This function can detect whether two elements collide.

Specifically, I wrapped the code for checking collisions between the bird and the pipes into a function called check_collision(). The output of this function is a boolean value — either True or False.
```
# defing check_collision() function 
def check_collision(pipe_list):
    # list every pipe (pipe is the image, pipe_rect is the position, scored is for scoring)
    for pipe, pipe_rect, _ in pipe_list:
        # if bird position collides with pipe position 
        if bird_rect.colliderect(pipe_rect):
            # return False
            return False
    # if bird fly out of the sky or touch the ground
    if bird_rect.top <= 0 or bird_rect.bottom >= GAMEHEIGHT:
        # return False
        return False 
    # if no collision, return True 
    return True 

# In the game loop, every round check the collision, and assign output to game_active variable
game_active = check_collision(pipe_list)
```

### 3. window3：gameover
When the game ends, the program will enter window3.
In the simplified version of the game, we need to set up a button in window3 so that when the player clicks it, the game returns to window2.

To implement such a button, in essence, we need to restart the game when the mouse clicks at a specific location.

Therefore, we can divide the code into the following steps:
a. Get the mouse position
b. Get the button position
c. Check whether the mouse position overlaps with the button position
d. Check whether the mouse is clicked
e. If the mouse overlaps with the button position and a click occurs, restart the game (game_active = True)

```
# get the cursor position 
mouse_pos = pygame.mouse.get_pos()
# set up mouse_click variable
mouse_click = False
# check whether cursor and button overlap 
hovered = restart_button_rect.collidepoint(mouse_pos)

# check player's input 
for event in pygame.event.get():
    if event.type == MOUSEBUTTONDOWN:
        mouse_click = True

# window2&3 framework
if game_active:
    code for window2
    game_active = check_collision(pipe_list)
else:
    code for window3
    # when both satisfied: a. cursor and button overlap; b. mouse click 
    if hovered and mouse_click:
        reset_game()
        game_active = True
```

### 4. window1: start
Now let’s return to the very beginning — window1.
In the simplified version of the game, I only set up a START button. When the player clicks it with the mouse, the game switches to window2.

The implementation of this button is the same as the one in window3.

With this, we now have a simplified version of Flappy Bird.
![Figure5. example of flappy bird v1]()<br>


## STEP3: Optimize details 
I specifically made optimizations in the following areas:
1. Drawing cute images
2. Adding a scoring system
3. Adding wing-flapping and bouncing animations for the bird
4. Adding hover animations for mouse buttons

### 1. Drawing cute images
The simplified version of the game only had blocks, which looked really ugly. Therefore, I specifically drew images for this game.
![Figure6. background+3 birds+2 pipes+2 buttons+scoreboard]()<br>

### 2. Adding a scoring system
The specific rules of the scoring system are as follows:
a. Each time the bird passes through a set of pipes, the player earns one point.
b. After the game ends, a scoreboard is displayed showing the score of the current game as well as the all-time high score.

First, let’s implement the scoring logic.
Specifically, this means checking the positions of the bird and the pipes. When the bird is located to the right side of a pipe, it indicates the bird has passed through it, and one point is awarded.
```
# initial score = 0
score = 0
# when game runs, if pipe x value < bird x value
if pipe_rect.centerx < bird_rect.centerx:
    # score + 1
    score += 1
# draw current score on the screen 
display_score(score)
```
Here I wrapped the code for drawing the score into a function called display_score(). I won’t go into the details here — if you’re interested, you can check my source code.

Next, let’s implement the scoreboard.
First, import the scoreboard image and draw it at the appropriate position in window3.
Then, compare the current game’s score with the historical high score. If the current score is higher, update the high score. 
```
# import scoreboard image, set up its position
scoreboard_img = load_image("image/scoreboard.png", 144, 180).convert_alpha()
scoreboard_rect = scoreboard_img.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2-50))

# when at window3, draw the scoreboard 
windowSurface.blit(scoreboard_img, scoreboard_rect)
# when this game's score > best score, update best score
if score > best_score:
    best_score = int(score)
# draw the score on the screen 
display_score(score, game_active, best_score)
```

### 3. Adding wing-flapping and bouncing animations for the bird
I added a bird with wing-flapping and bouncing animations to the welcome screen in window1.

Let’s first talk about the wing-flapping.
The wing-flapping animation is achieved by looping through three different bird images. 
![Figure7. example of 3 bird images circular]()<br>
Specifically, what needs to be done is:
a. Import three bird images, with the bird’s wing position slightly different in each image
b. Loop through the three images
c. Draw the bird

The code is as follows:
```
# import 3 bird iamges, save them in a list
birds = [load_image(f"image/bird{i+1}.png", 51, 36).convert_alpha() for i in range(3)]
# set up initial bird image 
bird_index = 0
bird_surface = birds[bird_index]
# set up bird position 
bird_rect = bird_surface.get_rect(center=(WINDOWWIDTH//2, GAMEHEIGHT//2))
# set up loop speed 
frame_count = 0

# when in window1 
while window1:
    frame_count += 1
    # update bird images 
    if frame_count % 10 == 0:
        bird_index = (bird_index + 1) % len(birds)
    bird_surface = birds[bird_index]
    # draw bird on the screen
    windowSurface.blit(bird_surface, bird_rect)
```

Next is the bouncing.
The bouncing animation makes the bird’s position move up and down. I achieved this using a sin() function.
```
# import math 
imort math
# use sin() function, set up bird bouncing distance 
bounce_offset = math.sin(frame_count * 0.1) * 8
# integrate bouncing animation to the bird position 
bird_rect.centery = bird_base_y + int(bounce_offset)
```

### 4. Adding hover animations for mouse buttons
I designed hover animations for the buttons in window1 and window3. This is divided into two steps:
a. When the mouse is within the button area, display a hand cursor; when the mouse is elsewhere on the screen, display an arrow cursor.
b. When the mouse is within the button area, enlarge the button.

First, let’s complete the cursor switching between the arrow and the hand.
Since the system already provides arrow and hand cursors, we can directly set them using function commands.
```
# when teh cursor and button overlap 
if start_button_rect.collidepoint(mouse_pos):
    # cursor change to hand shape 
    pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
else:
    # otherwise, cursor is arrow shape
    pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)
```

Next, let’s add the button enlargement animation. 
![Figure8. example of button hover]()<br>
I set a scaling factor: if the mouse overlaps with the button, the button is enlarged by 1.1×; if not, it remains unchanged. Then, by multiplying the original button image by this scaling factor, the button is enlarged according to the mouse position.

The code is as follows:
```
# set up scale factor 
scale_factor = 1.1 if hovered else 1.0
# based on scale factor, set up button width and height 
start_button_width = int(start_button_img.get_width() * scale_factor)
start_button_height = int(start_button_img.get_height() * scale_factor)
# based on width and height, update image
start_button_img_scaled = pygame.transform.smoothscale(start_button_img, (start_button_width, start_button_height))
start_button_rect_scaled = start_button_img_scaled.get_rect(center=start_button_rect.center)
# draw the button 
windowSurface.blit(start_button_img_scaled, start_button_rect_scaled)
```

With these refinements, we end up with a cute game.
![Figure9. example of flappy bird v2]()<br>


At this point, the Flappy Bird game is complete!
Thank you for reading!

Source code: Click here
My computer: Mac Pro
Programming language: Python
IDE: VS Code
Game development module: pygame