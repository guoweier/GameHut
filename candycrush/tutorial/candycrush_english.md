# Programming Learning Report #3：I made Candy Crush using Pygame

Computer: **Mac Pro**<br>
Programming language: **Python**<br>
Coding software: **VS code**<br>
Package: **pygame**<br>
Source code: [Click here]()<br>

Hello, this is Weier. A programming learner. 
Today, I am going to introduce my 3rd programming learning project: How to make Candy Crush using Pygame
Candy Crush is a tile-matching game. In the game, players complete levels by swapping colored pieces of candy on a gameboard to make a match of three or more of the same color, eliminating those candies from the board and replacing them with new ones, which could potentially create further matches. The original Candy Crush game has multiple levels. The higher the level, the more difficult the game, and also more types of candies as well as more special functions. 
As a beginner, my goal is to make one level, in order to learn fundamental functions design and coding logic. Next, let's see my game development tutorial. 

First, I built 3 windows for my game:
1. window1: start window 
2. window2: game playing window 
3. window3: gameover window 

## window1 (start window)
![Figure1. window1]()<br>
![Figure2. Table of window1 elements]()<br>
| Content | Property |
|-----|------|
| Window | 1100x800 pixels; custom background image |
| Text | Font: GravitasOne; Color; (129,115,92); Centered |
| Reaction | Press ENTER key to start |

window1 is designated for setting up variables, such as the window size, background, texts, etc. 
To enhance the visual appeal of the game interface, I specifically created a custom background image with a light pink tone as the main theme, adding a touch of cuteness.

## window2 (game playing window)
![Figure3. window2]()<br>
![Figure4. Table of window2 elements]()<br>
| Content | Property |
|-----|------|
| gameboard | 600x600 pixels; 6x6 in total 36 cells; at window right |
| scorebar | 210x620 pixels; display target candies and remaining moves; at window left |
| candy | in total 6 types, in red, orange, yellow, green, blue, purple, generated randomly |
| game rules | 1. Move the candies. 2. When over 3 candies align in a row or column, they are eliminated. 3. The candies above then fall down in order. 4. New candies are randomly generated to fill the empty spaces. |
| Get scores | In each round, two candies are randomly selected as target candies, and the player needs to eliminate 9 of each. The player can move candies up to 12 times. If the target is completed within 12 moves, it's a win; otherwise, it's a loss. |

window2 is the main body of the game. It contains 2 blocks: gameboard (right) and scorebar (left).
First, let's look at the gameboard. 
The gameboard is a 6x6 matrix, forming 36 cells. Every cell can carry one candy. 
![Figure5. gameboard matrix]()<br>
There are in total 6 types of candies: red, orange, yellow, green, blue, purple. Generated randomly. 
![Figure6. candy exhibition]()<br>

I would like the game to support the following interactions:
1. When the player click to swap two adjacent candies;
2. If the swap results in three or more candies aligned in a row or column;
3. The aligned candies will be eliminated;
4. The empty spaces left by eliminated candies will be filled by candies falling down from above;
5. The empty spaces at the top will then be filled with newly generated random candies. 

There are a total of 5 steps, and I've written one function for each step. So altogether, there are 5 functions:
1. Swap candies: animate_swap()
2. Detect candy matches: find_matches()
3. Eliminate matched candies: remove_matches()
4. Drop candies from above to fill empty spacies: animate_gravity()
5. Refill the board with randomly generated candies: refill_gameboard_gravity()

Next, we are going to introduce every step's coding logic. 
1. Swap candies
![Figure7. candy swap example]()<br>
The pseudocode of this function is as follows:
```
# swap candies
if MOUSEBUTTONDOWN:
    start_cell = get_cell(event.pos)
elif MOUSEBUTTONUP:
    end_cell = get_cell(event.pos)
    if are_nextdoor(start_cell, end_cell)：
        animate_swap(candy1, start_cell, candy2, end_cell)
```
First, I defined `start_cell` and `end_cell`: `start_cell` is the position where the mouse is pressed down, and `end_cell` is where the mouse is released. I created a function called `get_cell()` to get the position of the mouse click. 
Next, I check whether the two positions are adjacent. For this, I designed a function called `are_nextdoor()` to handle the adjacency check. 
If the two positions are adjacent, I call `animate_swap()` to display the animation of the two candies being swapped. 

2. Detect candy matches
![Figure8. find matches example]()<br>
The pseudocode of this function is as follows:
```
# find matches
if find_matches():
    code for remove matched candies，candy falling，refill gameboard
else:
    animate_swap(candy2, end_cell, candy1, start_cell)
```
I designed the `find_matches()` function to scan all 36 cells of the gameboard and check whether there are 3 or more candies aligned in a row or column. 
If a match is found, the game prceeds to the next step: eliminating the matched candies. 
If no match is found, `animate_swap()` is used to swap the candies back to their original positions. 

3-5. Eliminate matched candies + drop candies from above to fill empty spaces + randomly generate new candies to fill the board
![Figure9. examples of step3-5]()<br>
步骤3-5是一个反复监测，反复运行的过程。即，当匹配糖果消除后，自动进入下一轮监测（find_matches()）。若新生成的游戏框再次出现大于等于3个糖果排成一线，则需要再次执行“消除糖果+上方糖果下落填充+随机生成新糖果填满”的连续步骤。这个连续动作会不断循环，直至没有匹配的糖果。
因此，为了实现这个连续步骤，我设计了resolve_gameboard()这个function，将步骤3-5嵌套于其中。具体的代码框架如下：
Steps 3-5 form a repeating loop. That is, once matched candies are eliminated, the game automatically enters the next round of dtection using `find_matches()`. 
If the newly updated board again contains three or more aligned candies, the sequence of "eliminate + drop + generate" must be executed again. This sequence continues to loop unitl no more matches are found. 
To implement this continuous process, I created a function called `resolve_gameboard()`, which wraps steps 3-5 inside it. The pseudocode of this function is as follows:
```
def resolve_gameboard():
    while True:
        matches = find_matches()
        if not matches:
            break
        
        remove_matches(matches)
        draw_gameboard()
        animate_gravity()
        refill_gameboard_gravity()
        draw_gameboard()
```
In this function, I first set up a `while` loop to continuously check whether there are any matched candies. If matches are found, tehy are stored in the variable `matches`. If no matches are found, the loop ends. 
Once the scan is complete, if the loop hasn't ended it, it means that there are indeed matched candies. Then, the sequence of "eliminate + drop + generate" must be carried out. Specifically:
1. `remove_matches(matches)`: eliminate the matched candies
2. `draw_gameboard()`: redraw the game interface to show that the matched candies have been removed and empty spaces have appeared. 
3. `animate_gravity()`: let the candies above fall down to fill the gaps
4. `refill_gameboard_gravity()`: randomly generate new candies to fill the remaining empty spaces 
5. `draw_gameboard()`: redraw the game interface again to show the fully updated board after filling is complete 

In the main game loop, I only need to call this function once to automatically perform the entire process of repeatedly scanning for matches and filling the board with falling candies. 

Next, let's look at the scorebar. 
![Figure10. scorebar example]()<br>
The scorebar is placed at the left side of the window2. It is 210x620 pixels, divided into 3 sections: top, middle, and bottom. 
The top section displays the remaining number of moves for the current round, with an initial value of 12. 
The middle and bottom sections show the two target candies and the number of each taht needs to be cleared. The target candies are randomly selected for each game round, and 9 of each type must be eliminated. 

The above is an overview of window2. Here, I've only provided a rough explanation of the overall framework and structure, without going into the details of each line of code. If you are interested in specific functions and execution steps, you can refer to my source code, which I will include at the end. 

## window3 (gameover window)
![Figure11. window3]()<br>
![Figure12. Table of window3 elements]()<br>
| Content | Property |
|-----|------|
| Scoreboard | Objective complete: YOU WIN!  Objective not complete: YOU LOSE! |
| Reaction | Click Play Again button can start game again |

window3 displays the desinged scoreboard, and depending on the game result, it selectively shows either "YOU WIN" or "YOU LOSE". 
It also includes a "Play Again" button, which allows the player to start a new game when clicked. 

This is how I made Candy Crush. 
For source code, please click here. 

Hope you enjoy it! 




