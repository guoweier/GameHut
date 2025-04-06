# Programming Learning Project #1: How I made snake game from scratch to advance?

**SCENE**
*scene1*: I sit at the desk, with drawing background
*scene2*: I stand in front of a white board. 
*scene3*: Code or game screen. 

## Introduction
*scene2*
Hello everyone, welcome to my channel. This is Weier, I am currently learning programming. Recently, I have finished my first programming learning project: Making a snake game using pygame. It is very fundamental, but I am still excited about it, because this is my first self-motivated programming project! So today, I would like to share my experience on making the snake game. 

The reason I start this project is because I want to improve my coding skills by creating something fun. I know there are many excellent game dev softwares out there, and pygame is never popular on the market. But since I used to have a little experience with python and pygame is having lots of programming practice involved, I believe this can be a good start. 

Now, let's dive into the snake game! 
*scene3: examples of each window during introduction*
For my snake game, I separate it into 3 windows:
1. window1: start window, where the player will see a welcome message. 
2. window2: game playing window, which is the main window that we are familiar with. It has a snake, a food, and the snake can move around and eat the food. 
3. window3: gameover window, which is when the snake touch the border and died, it shows a scoreboard, and asked if the player want to start a new game. 
*scene3&2: half screen windows image, half screen me with the white board*
And I want my 3 windows to run like this:
- When starts the game, it shows window1. 
- When the player press ENTER key, it starts window2, and the snake game starts running. 
- When the snake died, it starts window3. 
- When the player press ENTER key, it starts window2, the snake game start again. 
- Anytime during the game, if the player press ESC key or click x on the window, the program terminate. 

*scene2*
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
Generally, I designed 2 while loops for the program:
1. The first while loop controls the program. When it stops, the whole python program terminates. 
2. The second while loop controls window2. When it stops, which means the snake died, window2 terminates and window3 automatically starts. 
As you can see, I wrote the window1 code before the 1st while loop. Then for window2, I separated it into 2 sessions: Session1 for window2 objects initialization, and Session2 for window2 animations. Session1 is placed within 1st loop but before 2nd loop. Session2 is placed within 2nd loop. Then window3 code is placed after 2nd loop and before 1st loop ends. 

Now this would be my program backbone. Next, let's look at each window. 

### window1
*title page: window1*
window1 is a 600x600 pixels black screen, contains 2 messages. When the player enters a key except ESC, the program enters window2. 
The code of window1 was placed before the 1st while loop. 

### window2
*title page: window2*
*scene3: example of window2*
*scene3&2: half screen window2 image, half screen me with the white board*
window2 is the main interface of the snake game. Let's together list the objects and their properties in window2 by looking at the picture:
1. There is a snake, a food.
2. The snake changes moving direction if I press arrow keys. 
3. When the snakehead meet the food, it eats the food. Then another food appears at a random position in the window. 
4. When the snake touch the border, it dies. Game over. 
5. There is a score recording system during the game. When the snake eats a food, add 1 point. The final score will be shown in window3. 

Looking at the backbone, I separate window2 code into 2 parts. The 1st part is the code of initialization, which is basically property #1, to set up snake and food. It is placed within 1st while loop, but before 2nd while loop. The 2nd part is the animation, which includes properties #2, #3 and #4. They are placed within 2nd while loop. Property #5, which is about score recording, was set up multiple times through these 2 loops. 

### window3
*title page: window3*
*scene3: example of window3*
*scene3&2: half screen window2 image, half screen me with the white board*
window3 is similar as window1. The only difference is it contains a semi-transparent rectangle as a scoreboard, and hold 4 messages to display the scores. 
The window3 code is placed after 2nd while loop. 

That is a basic snake game! 
But I am a person love cute, pretty stuffs. I cannot accept that my snake and food are just simple squares. I want something adorable, for example, a real snake image with head and tail. How can I do that?
I choose google snake game as my reference. And I mimic it to draw my own pictures and upgraded my snake game into a colorful one. 

First, let's see my results. 
*scene3: compare v1 and v2 with game running*
Left side is the version1, right side is the version2. It is not turning into a 3D game, but at least it has a real snake, with some little cute animations. Now, let's breakdown and compare each window. 

### window1
*title page: window1*
*scene3&2: half screen window1 v1 vs v2, half screen me with the white board*
window1 does not have many changes. By comparing 2 game interfaces, we can see:
1. v1 has a black background, v2 has a green background
2. v1's window is a square, it is 600x600 pixels. v2's window is slightly longer, it is 640x700 pixels. 
These are simple changes. Only need to change some variables. 
Now let's move on to window2. 

### window2
*title page: window2*
*scene3&2: half screen window2 v1 vs v2, half screen me with the white board*
window2 has lots of differences:
1. v1 has a black background, v2 has a plaid game board, and there is score bar on top. 
2. Food: v1 is a green square, v2 is a real apple image, and it has glowing animation. 
3. Snake: v1 is composed of 3 red squares, v2 is a real snake image, and it can open mouth when near the food. 

I drew the apple and the snake using Adobe Illustrator, and loaded them using pygame function. 
For food, it is straightforward. 
But for snake, it is a little complicated. I separated snake into 3 parts: snakehead, snakebody, snaketail. 2 things need to be awared of:
1. When snake change moving direction, the snake images also need to rotate appropriately. 
2. At the turning point, the snake body should have a corner. There are 4 types of corner: lefttop, leftbottom, righttop, rightbottom. By understanding the relationship between the corner and its nextdoor bodypart, I determined which corner type to choose. 
Here is an illustrative figure for their relationship. 

Next is animation. In pygame, animation is actually a stack of frames, and displayed one-by-one through game loop. The multiple frames object is called `sprite`. 
In my case, both food and snake have animations. 
For the food, it is a glowing animation, where the food image become large and small recurrently. So I loaded one apple image, and then set it into different sizes. I put these different sized apple images in a list, then displayed them recurrently through game loop. That's it. 
It is similar for snake mouth open. I drew snakehead with different mouth sizes. Then I calculated the distance between snakehead and the food, and displayed appropriate mouth images at designated distance. Here is an illustrative figure for the distance and corresponded mouth images. If x+y=3, small mouth, if x+y=2, medium mouth, if x+y<=1, wide mouth. All the other cases, close mouth. 
Now let's move on to window3. 

### window3
*title page: window3*
*scene3&2: half screen window3 v1 vs v2, half screen me with the white board*
Some differences we can see between v1 and v2 for window3:
1. v2 has a real scoreboard. 
2. In v2, the snake has a blink eyes animation. 
For adding a blink eyes animation into window3, I would say this is the most difficult change I experienced from v1 to v2. 
Because in v1, window3 only has static objects. All the objects only need to displayed once, so no loop needed. But now in v2, we have both static and animated objects in window3. To achieve this, I built 2 functions:
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

Alright, that is the end of the story. Though it is not as fancy as those published games on the market, I am still very excited and proud about my first game development project. I enjoyed the coding process, and also learning lots of new things. It also combined with lots of drawing, which is always my favorite. 

For complete source code and detailed programming tutorial, I put them on GitHub. I put links in the info box below. You should be able to run the program with the script if you have pygame installed properly. I also attached a link for pygame installation as well. 

Hope you enjoy it, and see you next time! 

