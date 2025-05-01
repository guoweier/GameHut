# Programming Learning Project #2: I made a tetris game

**SCENE**
*scene1*: I stand in front of a white board. 
*scene2*: Code or game screen. 

## Introduction 
*scene1*
Hi everyone, this is Weier. Welcome to my channel. Today, I would like to introduce my 2nd programming learning project: Make a tetris game. 

*scene2*
First, let's take a look of my tetris game. 
*video of tetris game window123*

*scene1&2: half whiteboard, half computer screen*
As we can see, there are 3 different windows:
1. window1: start window. It contains welcome messages. 
2. window2: game playing window. It is the main window of the game. One the left it is the gameboard, where tetrominoes fall down and stack. On the right it has blocks for next tetromino preview and score box. 
3. window3: gameover window. It displays a scoreboard on the left, and asked if the player want to start again. 

*scene1: flow-chart for window running process*
And I want my 3 windows to run like this:
- When starts the game, it shows window1. 
- When the player press ENTER key, it starts window2, and the tetris game starts running. 
- When the tetromino stacking exceed top border, gameover, it starts window3. 
- When the player click Play Again button, it starts window2, the tetris game start again. 
- Anytime during the game, if the player press ESC key or click x on the window, the program terminate. 

*scene1: write pseudo-code on the whiteboard in advance*
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
2. The second while loop controls window2. When it stops, which means gameover, window2 terminates and window3 automatically starts. 
As you can see, I wrote the window1 code before the 1st while loop. Then for window2, I separated it into 2 sessions: Session1 for window2 objects initialization, and Session2 for window2 animations. Session1 is placed within 1st loop but before 2nd loop. Session2 is placed within 2nd loop. Then window3 code is placed after 2nd loop and before 1st loop ends. 

Now let's look at each window. 

### window1
*scene2: example of window1*
window1 is a 660x660 pixels charcoal screen, contains 2 messages. When the player enters ENTER key, the program enters window2. 

### window2
*scene2: example of window2*
window2 is the main interface of the tetris game. 
It consists of 4 objects:
1. gameboard, located on the left, which is the main interface for game animations. 
2. preview box, located on the right top, which shows the next tetromino. 
3. score box, located on the right, which shows the current score and top score. 
4. game logo, located on the right bottom. 

Let's look at the gameboard in detail. What is the coding logic I designed to proceed the game? 
*scene1: draw an exmaple gameboard on whiteborad in advance*
I set the whole gameboard as a matrix. Every cell represents a tetromino square. If this cell has been occupied, it is 1; if not, it is 0. 
*scene1: draw an exmaple tetromino on whiteborad in advance*
Meanwhile, I set each tetromino as a small matrix. Same as the gameboard matrix, the cell with square is 1, no square is 0. 
*scene1: draw 7 tetrominoes on whiteborad in advance*
In total, there are 7 types of tetromino. 

So, the moving of tetromino can be seen as the moving of a small matrix inside a large matrix. 
1. When the small matrix touches the bottom row of the large matrix, it means the tetromino touch the gameboard bottom; When taking the position of small matrix and corresponds it into large matrix, and the cell below this this position is 1, it means this tetromino stacks on a previous tetromino.
2. When one row of the large matrix being all 1, it means this row is fully occupied by tetromino squares. This row is removed, all the rows above it move downwards, and the player gets 1 point. 
3. When the top row of the matrix has one cell that is 1, it means the tetromino stacks exceed the gameboard border, so game over. 

*scene1*
Here, I think one interesting point is how to set up tetromino rotation. We have 7 types of tetromino in total, if plus rotation, finally we get 19 types (some tetromino has the same shape after rotating 180 degree). If we list their shapes one-by-one, the code would be super redundant. So I choose an easier way. Here is the code for tetromino rotation:
```
unit_rt = [list(row)[::-1] for row in zip(*unit)]
```
Let's breakdown this line of code:
- `unit` represents small matrix. For example:
```
unit = [[0,0,0],
       [0,1,0],
       [1,1,1]]
```
This represents a T-shape tetromino. 

- `zip()` aggregates elements from multiple iterables into an iterator of tuples. Each tuple contains elements from the input iterables at the same index. For example: 
```
zip(unit) 
    = zip([[0,0,0],
        [0,1,0],
        [1,1,1]]) 
    = [(0,0,1),
     (0,1,1),
     (0,0,1)]
```
- `for row in zip(*unit)` uses for loop to list zipped tuples one by one. 
- `list(row)[::-1]` is to first transfer the tuple into list, and then write each element reversely. For example: 
```
list(row1)[::-1] 
    = list((0,0,1))[::-1] 
    = [1,0,0]
```
If 3 rows are all finished, then the output matrix is: 
```
[[1,0,0],
 [1,1,0],
 [1,0,0]]
```
Compare with the initial matrix: 
```
[[0,0,0],
 [0,1,0],
 [1,1,1]]
```
We noticed it has a clockwise rotation for 90 degree. 
So, we achieved rotation function with only one line of code. How beautiful it is! 

### window3
*scene2: example of window3*
window3 is similar as window1, which is to display the scoreboard and set up player reaction. 
Here, I set up a Play Again button, when click it, we restart the game. 

*scene1*
Alright, that is the end of the story. Comparing with my 1st project, which is to make a snake game, this tetris game have more coding complexity in the game playing window. It is a little challenging for me at the beginning, but I enjoyed it a lot. 

For complete source code, I put them on GitHub. I put links in the info box below. You should be able to run the program with the script if you have pygame installed properly. I also attached a link for pygame installation as well. 

Hope you enjoy it, and see you next time!

