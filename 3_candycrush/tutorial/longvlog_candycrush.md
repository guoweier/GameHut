# Programming Learning Report #3：I made Candy Crush 

**SCENE**
*scene1*: I sit at desk
*scene2*: game screen
*scene3*: slides

## Introduction 
*scene1*
Hi everyone, this is Weier. Welcome to my channel. Today, I would like to introduce my 3rd programming learning project: Make Candy Crush using pygame. 

*scene2: candy crush window123*
First, let's take a look of my candy crush. 

There are 3 different windows in my game:
1. window1: start window. It contains welcome messages. 
2. window2: game playing window. It is the main platform of the game. The gameboard is on the right. On the left it is the scorebar, containing target candies and remaining moves. 
3. window3: gameover window. It displays message "YOU WIN" or "YOU LOSE", and asked if the player want to start again. 

*scene3: flow-chart for window running process*
And I want my 3 windows to run like this:
- When starts the game, it shows window1. 
- When the player press ENTER key, it starts window2, and the candy crush starts running. 
- When the gameover, it starts window3. 
- When the player click Play Again button, it starts window2, the game start again. 
- Anytime during the game, if the player press ESC key or click x on the window, the program terminate. 

Now, let's breakdown each window. 

### window1
*scene3: move to window1 label on flow chart, zoom in of window1, transit to window1 example*
window1 is a 1100x800 pixels screen, contains 2 messages. When the player enters ENTER key, the program enters window2. 
To enhance the visual appeal of the game interface, I specifically created a custom background image with a light pink tone as the main theme, adding a touch of cuteness.
*scene3: zoom out of window1 explanation, get back to the flow chart*

### window2
*scene3: move to window2 label on flow chart, zoom in of window2, transit to window2 example*
window2 is the main body of the game. It contains 2 blocks: gameboard (right) and scorebar (left).

*scene3: transit from window2 to an empty gameboard*
First, let's look at the gameboard. 
*scene3: show labels for gameboard rows and columns and cells*
The gameboard is a 6x6 matrix, forming 36 cells. Every cell can carry one candy. 
*scene3: zoom out empty gameboard and put it in corner. show 6 candies*
There are in total 6 types of candies: red, orange, yellow, green, blue, purple. Generated randomly. 

*scene3: combine corner empty gameboard with candies, show a full gameboard*
I would like the game to support the following interactions:
*scene3: cursor exchange two nextdoor candies, list 1. swap: animate_swap()*
1. The player click to swap two adjacent candies. It displays candies swap, and I designed a function `animate_swap()` to show the animation. 
*scene3: highlight matched candies, list 2. match: find_matches()*
2. The swap results in three or more candies aligned in a row or column. This is checked by the function `find_matches()`. 
*scene3: matched candies disappear, list 3. remove: remove_matches()*
3. The aligned candies are eliminated. This is done by the function `remove_matches()`. 
*scene3: top candies fall down to fill the space, list 4. drop: animate_gravity()*
4. The empty spaces left by eliminated candies are filled by candies falling down from above. This is done by the function `animate_gravity()`. 
*scene3: the top row empty space fill with new generated candies, list 5. refill: refill_gameboard_gravity()*
5. The empty spaces at the top will then be filled with newly generated random candies. This is done by the function `refill_gameboard_gravity()`. 

Next, we are going to introduce every step's coding logic. 
*scene3: zoom in 1. swap: animate_swap() in the function list*
1. Swap: animate_swap()
*scene3: show pseudocode block*
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
*scene3: highlight start_cell and end_cell in code block*
First, I defined `start_cell` and `end_cell`: 
*scene3: add label for start_cell*
- `start_cell` is the position where the mouse is pressed down; 
*scene3: add label for end_cell*
- `end_cell` is where the mouse is released. 
*scene3: highlight get_cell(), add label*
I created a function called `get_cell()` to get the position of the mouse click. 
*scene3: highlight are_nextdoor(), add label*
Next, I check whether the two positions are adjacent. For this, I designed a function called `are_nextdoor()` to handle the adjacency check. 
*scene3: highlight animate_swap(), add label*
If the two positions are adjacent, I call `animate_swap()` to display the animation of the two candies being swapped. 

*scene3: move code block to side, show two nextdoor candies for animation example*
So this code block is running like this:
*scene3: a cursor press down animation for the first candy*
1. The mouse click down on the first candy (*highlight if MOUSEBUTTONDOWN*), `get_cell()` records the click down position (*highlight get_cell()*) and stores it in `start_cell` (*highlight start_cell*).
*scene3: a cursor move from first candy area to the second candy area, then release animation*
2. The mouse move to the second candy, and release (*highlight if MOUSEBUTTONUP*), `get_cell()` records the click up position (*highlight get_cell()*) and stores it in `end_cell` (*highlight end_cell*).
*scene3: animation of nextdoor determination*
3. Use `are_nextdoor()` to determine whether `start_cell` and `end_cell` are adjacent with each other (*highlight are_nextdoor(start_cell, end_cell)*). 
*scene3: animation of candies swap*
4. If true, run `animate_swap()` to exchange two candies (*highlight animate_swap(candy1, start_cell, candy2, end_cell)*)

*scene3: zoom code block out back to function list, then zoom in 2. match: find_matches()*
2. Match: find_matches()
*scene3: show pseudocode block*
The pseudocode of this function is as follows:
```
# find matches
if find_matches():
    code for remove matched candies
    code for candy dropping
    code for refill gameboard
else:
    animate_swap(candy2, end_cell, candy1, start_cell)
```
*scene3: highlight find_matches() in code block, add explanation label*
I designed the `find_matches()` function to scan all 36 cells of the gameboard and check whether there are 3 or more candies aligned in a row or column. 
*scene3: highlight code for remove, drop and refill*
If a match is found, the game proceeds to the next step: eliminating the matched candies. 
*scene3: highlight animate_swap(), add explanation label*
If no match is found, `animate_swap()` is used to swap the candies back to their original positions.

*scene3: expand two adjacent candies to 2x3 cells, with previous swapped candies form 3 same in row*
So this code block is running like this:
*scene3: circle 3 matched candies*
1. If `find_matches()` detect 3 same candies in row (*highlight find_matches()*), proceeds the following steps (*highlight code for remove, drop and refill*)
2. if no matches detected (*highlight else*), use `animate_swap()` to swap candies back (*highlight animate_swap()*)

*scene3: do not move example 2x3 gameboard, zoom out code block to function list, then highlight and zoom in 3-5*
3-5. Eliminate matched candies + drop candies from above to fill empty spaces + randomly generate new candies to fill the board
*scene3: chart flow of step3-5: P206*
Steps 3-5 form a repeating loop. That is, once matched candies are eliminated, the game automatically enters the next round of detection using `find_matches()`. 
If the newly updated board contains three or more aligned candies, the sequence of "eliminate + drop + generate" must be executed. This sequence continues to loop until no more matches are found. 
If there is no aligned candies, the loop exit. 
To implement this continuous process, I created a function called `resolve_gameboard()`, which wraps steps 3-5 inside it. 
*scene3: show pseudocode block*
The pseudocode of this function is as follows:
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
This code block is running like this:
- Start a `while` loop (*highlight while True*) to continuously check whether there are any matched candies with `find_matches()` function (*highlight find_matches()*). If matches are found, they are stored in the variable `matches` (*highlight matches*). If no matches are found (*highlight if not matches*), the loop ends and exit resolve_gameboard() (*highlight break*). 
- Once the scan is complete, if the loop hasn't ended it, it means that there are indeed matched candies. Then the sequence of "eliminate + drop + refill" must be carried out. Specifically: 
*scene3: disappear 3 matched candies*
1. `remove_matches(matches)`: eliminate the matched candies (*highlight remove_matches(matches)*)
2. `draw_gameboard()`: redraw the game interface to show that the matched candies have been removed and empty spaces have appeared. (*highlight draw_gameboard()*)
*scene3: drop top row candies to bottom row*
3. `animate_gravity()`: let the candies above fall down to fill the gaps (*highlight animate_gravity()*)
*scene3: drop from above gameboard to top row with randomly generated candies*
4. `refill_gameboard_gravity()`: randomly generate new candies to fill the remaining empty spaces (*highlight refill_gameboard_gravity()*)
5. `draw_gameboard()`: redraw the game interface again to show the fully updated board after filling is complete (*highlight draw_gameboard()*)

In the main game loop, I only need to call this `reslove_gameboard()` function once to automatically perform the entire process of repeatedly scanning for matches and filling the board with falling candies. 

*scene3: transit back to window2, then zoom in for scorebar*
These are the introduction of gameboard. Next, let's look at the scorebar. 
*scene3: add labels*
The scorebar is divided into 3 sections: top, middle, and bottom. 
*scene3: add label for top section*
The top section displays the remaining number of moves for the current round, with an initial value of 12. 
*scene3: add labels for middle and bottom sections*
The middle and bottom sections show the two target candies and the number of each taht needs to be cleared. The target candies are randomly selected for each game round, and 9 of each type must be eliminated. 

*scene3: transit back to window2*
The above is an overview of window2. Now let's move on to window3. 

### window3
*scene3: transit back to flow chart, move to window3 label on flow chart, zoom in of window3, transit to window3 example*
Now let's move on to window3. 
*scene3: add label for scoreboard*
window3 displays the desinged scoreboard, and depending on the game result, it selectively shows either "YOU WIN" or "YOU LOSE". 
*scene3: add label for Play Again*
It also includes a "Play Again" button, which allows the player to start a new game when clicked. 

*scene1*
This is how I made Candy Crush. Comparing with my 1st and 2nd projects - snake and tetris - candy crush definitely has more complexity. But of course with more fun for learning the design and implementation and finally successfully make it out! 

For complete source code, I put them on GitHub. I put links in the info box below. You should be able to run the program with the script if you have pygame installed properly. I also attached a link for pygame installation as well. 

Hope you enjoy it, and see you next time!

