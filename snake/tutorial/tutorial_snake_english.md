# Programming Learning Project #1: How I made snake game from scratch to advance?

Computer: **Mac Pro**<br>
Programming Language: **Python**<br>
Coding software: **VS code**<br>
Package: **pygame**<br>
Detailed tutorial: Part I, Part II<br>
Source code: Part I, Part II<br>


As a programming beginner, I always want to create something using the coding knowledge I have learned. When I was learning the concepts, I feel dizzy when seeing those data structure exercises, which have no relation to my daily life at all. So I decide to create a game, which sounds fun and easy-to-do. My first game, is snake. 
![Figure1. Snake Game example](fig1_snakegameexample.webp) <br>

I planned my snake game to have 3 windows:
1. window1: 
- Start window, where the player will see a welcome message. 
2. window2: 
- Game playing window, which is the main window that we are familiar with. It has a snake, a food, and the snake can move around and eat the food. 
3. window3: 
- Gameover window, which is when the snake touch the border and died, it shows a scoreboard, and asked if the player want to start a new game. 

And I want my 3 windows to process like this:
- When starts the game, it shows window1. 
- When the player press ENTER key, it starts window2, and the snake game starts running. 
- When the snake died, it starts window3. 
- When the player press ENTER key, it starts window2, the snake game start again. 
- Anytime during the game, if the player press ESC key or click x on the window, the program terminate. 

So I designed a pseudo-code block to organize my 3 windows:
```
# window1
Code for window1 
while True: # 1st loop
    # window2
    code for window2 initialization
    while True: # 2nd loop
        code for window2 animations during the game
        break the 2nd loop if game over
    # window3
    code for window3
    if the player start a new round:
        continue 1st loop
    elif the player terminate the program:
        break the 1st loop
```
Generally, I designed 2 `while` loops for the program:
1. The first while loop controls the program. When it stops, the whole python program terminates. 
2. The second while loop controls window2. When it stops, which means the snake died, window2 terminates and window3 automatically starts. 
As you can see, I wrote the window1 code before the 1st while loop. Then for window2, I separated it into 2 sessions: Session1 for window2 objects initialization, and Session2 for window2 animations. Session1 is placed within 1st loop but before 2nd loop. Session2 is placed within 2nd loop. Then window3 code is placed after 2nd loop and before 1st loop ends. 

Now this would be my program backbone. Next, let's look at each window. 

### window1
![Figure 2. window1 v1]()
window1 is a 600x600 pixels black screen, contains 2 messages. When the player enters a key except ESC, the program enters window2. 
The code of window1 was placed before the 1st while loop. 

### window2
![Figure 3. window2 v2]()
window2 is the main interface of the snake game. Let's together list the objects and their properties in window2 by looking at the picture:
1. There is a snake, a food.
2. The snake changes moving direction if I press arrow keys. 
3. When the snakehead meet the food, it eats the food. Then another food appears at a random position in the window. 
4. When the snake touch the border, it dies. Game over. 
5. There is a score recording system during the game. When the snake eats a food, add 1 point. The final score will be shown in window3. 

Looking at the backbone, I separate window2 code into 2 parts. The 1st part is the code of initialization, which is basically property #1, to set up snake and food. It is placed within 1st while loop, but before 2nd while loop. The 2nd part is the animation, which includes properties #2, #3 and #4. They are placed within 2nd while loop. Property #5, which is about score recording, was set up multiple times through these 2 loops. 

### window3
![Figure 4. window3 v1]()
window3 is similar as window1. The only difference is it contains a semi-transparent rectangle as a scoreboard, and hold 4 messages to display the scores. 
The window3 code is placed after 2nd while loop. 

That is a basic snake game! 
However, I am a person love cute, pretty stuffs. I cannot accept that my snake and food are just simple squares. I want something adorable, for example, a real snake image with head and tail. How can I do that?
I choose google snake game as my reference. And I mimic it to draw my own pictures and upgraded my snake game into a colorful one. 

First, let's see v1 and v2 differences window by window. 
1. window1
![Figure 5. window1 v1 vs v2]()
    | Content    | v1   | v2   |
    |--------|---------|----------|
    | Background    | black     | green     |
    | window size | 600x600 | 640x700 |
2. window2
![Figure 6. window2 v1 vs v2]()
    | Content    | v1        | v2                                             |
    |----------|------------|--------------------------------------------------|
    | screen   | 600x600 black  | 640x700 green, 600x600 plaid game board, scorebar on top |
    | food   | 1 green square | apple image, glowing animation                              |
    | snake    | 3 red squares  | snake image, open mouth animation when close to food           |
    | scorebar | None           | display score on top of the window             |
3. window3
![Figure 7. window3 v1 vs v2]()
    | Content      | v1                   | v2                             |
    |------------|--------------------------|--------------------------|
    | snake      | no animation             | blink eyes                         |
    | scoreboard | while semi-transparent rectangle, show 4 messages | designed scoreboard image |

Next, let's see how I achieve these changes. 
### window1: start window
This window only changes the color, width and height. I only need to change the corresponded variables. 
### window2: game playing window
1. Food
- Load and draw images
    - function for loading images:
    ```
    def load_image(file, x, y):
        img = pygame.image.load(file)
        img = pygame.transform.scale(img, (x,y))
        return img
    ```
    - function for drawing images:
    ```
    def draw_image(img, surface, x, y):
        img_rect = img.get_rect(center=(x,y))
        surface.blit(img, img_rect)
    ```
- create glowing animation:
In pygame, animation is actually a stack of frames, and displayed one-by-one through game loop. The multiple frames object is called `sprite`. Here for food, it is a glowing animation, where the food image become large and small recurrently. So I loaded one apple image, and then set it into different sizes. I put these different sized apple images in a list, then displayed them recurrently through game loop.

2. Snake
- load images of snakehead, snakebody and snaketail respectively:
    - use the image loading and drawing functions. 
    - 2 thing to be aware of>
        - When snake change moving direction, the snake images also need to rotate appropriately. 
        - At the turning point, the snake body should have a corner. There are 4 types of corner: lefttop, leftbottom, righttop, rightbottom. By understanding the relationship between the corner and its nextdoor bodypart, I determined which corner type to choose. 
        ![Figure 8. corner image choosen]()
- create open mouth animation
    - It is similar as glowing animation for food. I loaded snakehead images with different mouth sizes and put them in a list. Then I calculated the distance between snakehead and the food, and displayed appropriate mouth images at designated distance. 
    ![Figure 9. correlation between food and snakehead]()
3. Scorebar
- Display current scores at the appropriate positions on the window. 

### window3: gameover window
1. Scoreboard
- Load scoreboard image and display it using the previous defined functions. 
2. Create blink eyes animation
- Put snakehead images with different eye sizes in a list, and then displayed them recurrently. 
3. Upgrade structure
The most difficult part of window3 is: It needs to display both static elements and animated elements. To achieve this, I built 2 functions:
1. The 1st function is to display all the static objects, such as the scoreboard, the food image, etc. 
2. The 2nd function is to display animated object, which is the snakehead with multiple blinking eye frames. 
Then I added a while loop specifically for window3. This while loop has these properties:
1. It starts only when window2 loop terminates. 
2. It only run static function once, but would recurrently run for animated function. 
3. It terminates when the player enters a key. 

With this update, now my backbone looks like this:
```
# window1
Code for window1 
while True: # 1st loop
    startwindow3 = False
    # window2
    code for window2 initialization
    while startwindow3==False: # 2nd loop
        code for window2 reactions during the game
        if game over:
            startwindow3 = True
            break the 2nd loop
    # window3
    if startwindow3==True:
        code for window3
```
Most of things stay the same. But in order to control window3 loop, I set up a boolean variable named `startwindow3`. When it turns False, window2 loop runs. When it turns True, window3 loop runs. 

## conclusion
That is the end of the story. Though it is not as fancy as those published games on the market, I am still very excited and proud about my first game development project. I enjoyed the coding process, and also learning lots of new things. It also combined with lots of drawing, which is always my favorite.

Hope you enjoy it! 


## Resources
Detailed tutorial: 
- Part I
- Part II
Source code: 
- Part I
- Part II







