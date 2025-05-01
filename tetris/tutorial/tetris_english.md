# Programming Learning Report #2：I made a tetris using Pygame

Computer: **Mac Pro**<br>
Programming language: **Python**<br>
Coding software: **VS code**<br>
Package: **pygame**<br>
Source code: [Click here]()<br>

This is the second project of my programming learning journey. I made a tetris using pygame. 
Now let me introduce the process. 

First, I built 3 windows for my game:
1. window1: start window 
2. window2: game playing window 
3. window3: gameover window 

Next, it is the running logic structure of 3 windows. Here I use a pseudo-code block to represent:
```
# window1
Code for window1 
while True: # 1st loop
    startwindow3 = False
    # window2
    code for window2 initialization
    while startwindow3==False: # 2nd loop
        code for window2 animations during the game
        if game over:
            startwindow3 = True
            break the 2nd loop
    # window3
    if startwindow3 == True:
        code for window3
```
Generally, I designed 2 `while` loops for the program:
1. The first while loop controls the program. When it stops, the whole python program terminates. 
2. The second while loop controls window2. When it stops, which means the snake died, window2 terminates and window3 automatically starts. 

## window1 (start window)
![Figure1. window1]()<br>
![Figure2. Table of window1 elements]()<br>
winodw1 is designated for setting up variables, such as the window size, color, texts, etc. 

## window2 (game playing window)
![Figure3. window2]()<br>
![Figure4. Table of window2 elements]()<br>

window2 is the main body of the game, which is the most difficult part. 
I set the whole gameboard as a matrix. Every cell represents a tetromino square. If this cell has been occupied, it is 1; if not, it is 0. 
![Figure5. gameboard matrix]()<br>
Meanwhile, I set each tetromino as a small matrix. Based on the different side length of tetromino, small matrices can be: 4x4, 3x3, 2x2. Same as the gameboard matrix, the cell with square is 1, no square is 0. 
![Figure6. units represented by matrix]()<br>
So, the moving of tetromino can be seen as the moving of a small matrix inside a large matrix. 
1. When the small matrix touches the bottom row of the large matrix, it means the tetromino touch the gameboard bottom; When taking the position of small matrix and corresponds it into large matrix, and the cell below this this position is 1, it means this tetromino stacks on a previous tetromino.
2. When one row of the large matrix being all 1, it means this row is fully occupied by tetromino squares. This row is removed, all the rows above it move downwards, and the player gets 1 point. 
3. When the top row of the matrix has one cell that is 1, it means the tetromino stacks exceed the gameboard border, so game over. 

Here, I think one interesting point is how to set up tetromino rotation. We have 7 types of tetromino in total, if plus rotation, finally we get 19 types (some tetromino has the same shape after rotating 180 degree). If we list their shapes one-by-one, the code would be super redundant. So I choose an easier way. Here is the code for tetromino rotation:
```
unit_rt = [list(row)[::-1] for row in zip(*unit)]
```
- `unit` represents small matrix. For example: 
![Figure7. unit matrix and its corresponding unit diagram]()<br>
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

## window3 (gameover window)
![Figure8. window3]()<br>
![Figure9. Table of window3 elements]()<br>

window3 is similar as window1, which is to display the scoreboard and set up player reaction. 


This is how I made the tetris. 
For source code, please click here. 

Hope you enjoy it! 