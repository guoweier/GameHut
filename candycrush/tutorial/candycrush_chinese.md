# 自学编程汇报#3：我用pygame制作了Candy Crush

我的电脑： **Mac Pro**<br>
我使用的编程语言：**Python**<br>
我使用的编程软件：**VS code**<br>
我使用的游戏制作模块：**pygame**<br>
完整的代码：[点击这里]()<br>

Hello，我是Weier。一个普普通通的编程学习者。

今天，我来介绍我自学编程以来，练习完成的第三个小项目：用pygame制作Candy Crush游戏。
Candy Crush中文叫糖果传奇（以下皆称为Candy Crush）。它是通过移动糖果，令三至五个相同的糖果连在一起后消除，并得分。该游戏可以多平台运行，且具备多个关卡，越往后难度越高，糖果种类和特殊功能也越丰富。作为一个初学者，我的个人能力着实有限，为了简化制作流程，我的目标是制作一个关卡，掌握一些基础功能的代码设计。
接下来，就让我们一起来看看具体的制作攻略吧。

首先，我建立了三个界面：
1. window1: start window (开始界面)
2. window2: game playing window (游戏运行界面)
3. window3: gameover window (游戏结束界面)

## window1（欢迎界面）
![Figure1. window1]()<br>
![Figure2. Table of window1 elements]()<br>
| 内容 | 属性 |
|-----|------|
| 窗口 | 1100x800 pixels；自制背景图 |
| 文字 | 字体：GravitasOne; 颜色：(129,115,92)；居中显示 |
| 玩家指令 | 输入ENTER键进入游戏 |

window1主要就是设置各个变量，例如窗口的尺寸，显示的文字等等。为了增添游戏界面的美观性，我为此专门绘制了一张背景图，主体为肉粉色，增添可爱属性。

## window2 (游戏运行界面)
![Figure3. window2]()<br>
![Figure4. Table of window2 elements]()<br>
| 内容 | 属性 |
|-----|------|
| 游戏框 | 600x600 pixels；6x6共36个格子；位于window右侧 |
| 任务栏 | 210x620 pixels；显示任务糖果以及剩余步骤；位于window左侧 |
| 糖果 | 共6种，颜色为红橙黄绿蓝紫，随机产生 |
| 游戏运行规则 | 移动糖果，当3-5个糖果排成一线后消除，其上方糖果依次下落，后随机生成新的糖果填满空缺格 |
| 得分规则 | 每局游戏会随机生成两种颜色的糖果作为任务糖果，每种糖果需要消除9个。玩家最多可移动糖果12次。若在12次之内完成任务，则胜利；若没有，则失败 |

window2是整个游戏的主体。它包含了两个板块：游戏框（右侧），任务栏（左侧）。
首先，我们先来介绍游戏框。游戏框是一个6x6的矩阵，总共形成了36个格子。每个格子可放置一个糖果。
![Figure5. gameboard matrix]()<br>
糖果一共有6种颜色：红橙黄绿蓝紫。随机产生。
![Figure6. candy exhibition]()<br>
我需要游戏能完成以下的互动：
1. 当玩家用鼠标点击交换两个相邻位置的糖果后；
2. 若产生大于等于三个糖果为排成一线；
3. 则排成一线的糖果消除；
4. 消除后的游戏方格产生空缺，位于其上方的糖果依次下落填充；
5. 之后，最上方留下来的空格则由随机生成新的糖果填满。

一共是5个步骤。我将每个步骤都写了一个function来实现。那么总共就是5个function：
1. 交换糖果：animate_swap() 
2. 监测糖果匹配：find_matches()
3. 消除糖果：remove_matches()
4. 上方糖果下落填充：animate_gravity()
5. 随机生成新糖果填满：refill_gameboard_gravity()

接下去，我将简述每一个步骤的代码逻辑。
1. 交换糖果
![Figure7. candy swap example]()<br>
其代码框架如下：
```
# swap candies
if MOUSEBUTTONDOWN:
    start_cell = get_cell(event.pos)
elif MOUSEBUTTONUP:
    end_cell = get_cell(event.pos)
    if are_nextdoor(start_cell, end_cell)：
        animate_swap(candy1, start_cell, candy2, end_cell)
```
我先定义了start_cell和end_cell：start_cell为鼠标按下去的位置；end_cell为鼠标抬起来的位置。这里我设计了一个function：get_cell()，来获取鼠标点击的位置。
接着，判断这两个位置是否相邻。我设计了are_nextdoor()这个function来实现判断功能。
若两个位置相邻，则交换糖果。我设计了animate_swap()这个function来展示两个糖果的交换动画。

2. 监测糖果匹配
![Figure8. find matches example]()<br>
其代码框架如下：
```
# find matches
if find_matches():
    code for remove matched candies
    code for candy falling 
    code for refill gameboard
else:
    animate_swap(candy2, end_cell, candy1, start_cell)
```
我设计了find_matches()这个function，用于监测整个游戏框36个方格，观察是否有大于等于3个的糖果排成一线。
若有，则进入下一步，即消除糖果。若没有，则使用animate_swap()将原本交换的糖果放回原本的位置。

3-5. 消除糖果+上方糖果下落填充+随机生成新糖果填满
![Figure9. examples of step3-5]()<br>
步骤3-5是一个反复监测，反复运行的过程。即，当匹配糖果消除后，自动进入下一轮监测（find_matches()）。若新生成的游戏框再次出现大于等于3个糖果排成一线，则需要再次执行“消除糖果+上方糖果下落填充+随机生成新糖果填满”的连续步骤。这个连续动作会不断循环，直至没有匹配的糖果。
因此，为了实现这个连续步骤，我设计了resolve_gameboard()这个function，将步骤3-5嵌套于其中。具体的代码框架如下：
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
在这个function中， 我首先设置了一个while loop，循环式的检测是否有糖果匹配。若有，则将匹配的糖果们保存在matches这个变量中。若没有，则结束while loop。
在完成扫描检测后，若循环没有结束，则证明确实存在匹配的糖果。那么接下去就需要完成“消除糖果+上方糖果下落填充+随机生成新糖果填满”这一系列步骤。即：
1. remove_matches(matches)：消除糖果
2. draw_gameboard()：重新绘制游戏界面，展示匹配糖果已被消除，游戏框里出现了空格。
3. animate_gravity()：上方糖果依次下落填充
4. refill_gameboard_gravity()：随机生成新糖果填满
5. draw_gameboard()：再次绘制游戏界面，展示填充完成后的游戏界面。

在正式的game loop中，我只需要运行这个function一次，就直接实现了循环监测扫描并下落填充糖果的步骤。

接着，我们来看任务栏。
![Figure10. scorebar example]()<br>
任务栏位于界面左侧，210x620 pixels，分为上中下三层。
最上层显示该局游戏的剩余交换步数，初始步数为12. 
中下层显示两个任务糖果以及需要消除的个数。糖果颜色每局游戏随机生成，每种糖果需要消除9个。

以上就是window2的简介。这里我只粗略解析了大框架结构，未涉及细节的每一行代码。若对具体的function和运行步骤感兴趣，可以参考我的源代码。源代码我会附在文末。

## window3 (游戏结束界面)
![Figure11. window3]()<br>
![Figure12. Table of window3 elements]()<br>
| 内容 | 属性 |
|-----|------|
| 分数板 | 若完成任务，则显示YOU WIN!；若任务失败，则显示YOU LOSE！|
| 玩家指令 | 用鼠标点击play again按键可重新开始游戏 |

window3显示绘制好的分数板，然后根据游戏结果，选择性显示YOU WIN或YOU LOSE的字样。
并且包含一个Play Again的按键，点击按钮可开启新一局游戏。


以上就是Candy Crush的制作简介。
源代码可以戳这里。

今天又进步了一点点！继续加油！
