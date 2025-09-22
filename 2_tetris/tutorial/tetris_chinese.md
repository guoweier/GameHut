# 自学编程汇报#2：用pygame做俄罗斯方块

我的电脑： **Mac Pro**<br>
我使用的编程语言：**Python**<br>
我使用的编程软件：**VS code**<br>
我使用的游戏制作模块：**pygame**<br>
完整的代码：[点击这里]()<br>

自学编程以来的第二个小项目：用pygame做了俄罗斯方块。
下面就来介绍具体制作过程。

首先是建立三个界面：
1. window1: start window (开始界面)
2. window2: game playing window (游戏运行界面)
3. window3: gameover window (游戏结束界面)

接着，是三个window的运行结构。这里我用pseudocode来展示大框架：
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
整个框架包含了两个while loop. 第一个while loop保证python程序的运行，一旦停止，整个程序就退出了，窗口关闭。第二个while loop监测俄罗斯方块游戏的运行，一旦停止，就说明gameover，就会展示游戏结束界面，显示分数板。

## window1（欢迎界面）
![Figure1. window1]()<br>
![Figure2. Table of window1 elements]()<br>
| 内容 | 属性 |
|-----|------|
| 窗口大小及颜色 | 660x660 pixels；RGB=(57,57,57) |
| 文字 | 字体：Squarea; 颜色：白色；居中显示 |
| 玩家指令 | 输入ENTER键进入游戏 |

window1主要就是设置各个变量，例如窗口的尺寸，颜色，显示的文字等等。相对比较容易。

## window2 (游戏运行界面)
![Figure3. window2]()<br>
![Figure4. Table of window2 elements]()<br>
| 内容 | 属性 |
|-----|------|
| 游戏界面分配 | 1. 游戏运行框：位于window左侧；2. 预览框：显示下一个掉落块，位于window右上角；3. 分数框：实时显示当前分数和最高分，位于window右侧；4. 游戏logo：位于window右下角 |
| 掉落块 | 共7种，随机产生，按左右键可左右移动，按向下键可加速下落，按R键可旋转 |
| 游戏运行规则 | 当一整行被占满时，得1分；当掉落快堆叠超过上方边框时，游戏结束 |

window2是整个游戏的主体，也是最难的部分。
我将整个游戏框看作一个矩阵，每个矩阵位置格代表一个掉落块方块。若该位置已被方格占据，则为1；若已没有方格，则为0.
![Figure5. gameboard matrix]()<br>
同时，我将每个掉落块也用一个小矩阵表示。根据掉落块的边长不同，小矩阵分别为：4x4，3x3, 2x2. 同样的，有方格的位置为1，无方格的位置为0.
![Figure6. units represented by matrix]()<br>
因此，掉落块的下落可以看成小矩阵在大矩阵中的位移。
1. 当小矩阵接触到大矩阵最下边一行，则代表掉落块触底；当小矩阵所在的位置在大矩阵中其下方方格为1，则代表掉落块堆叠。那么该掉落块完成下落，随即生成新的掉落块。
2. 当大矩阵一整行均为1时，代表一整行被方格占满，则消除这行，上边的行依序往下移动，并得1分。
3. 当大矩阵的最上边一行有位置为1时，说明掉落块堆叠已超出游戏框，则游戏结束。

这里我觉得比较有意思的是如何设置掉落块的旋转。我们一共有7种掉落块，如果加上旋转，最终有19种（有些掉落块旋转180后与初始状态相同）。若使用枚举法表示它们的形态，代码过于冗长繁杂。所以我选择了一个简化的办法，具体旋转代码如下：
```
unit_rt = [list(row)[::-1] for row in zip(*unit)]
```
- `unit` 代表小矩阵。例如:
![Figure7. unit matrix and its corresponding unit diagram]()<br>
- `zip()` 代表将小矩阵里每行相同index的元素一一配对。例如:
```
zip(unit) 
    = zip([[0,0,0],
        [0,1,0],
        [1,1,1]]) 
    = [(0,0,1),
     (0,1,1),
     (0,0,1)]
```
- `for row in zip(*unit)` 则是将zip()之后的tuple一一列举出来
- `list(row)[::-1]` 是将每个tuple先转化成list，然后倒着列举其中的元素。例如：
```
list(row1)[::-1] 
    = list((0,0,1))[::-1] 
    = [1,0,0]
```
若将三行都完成之后，输出的矩阵为：
```
[[1,0,0],
 [1,1,0],
 [1,0,0]]
```
对比最开始的矩阵：
```
[[0,0,0],
 [0,1,0],
 [1,1,1]]
```
我们注意到它恰好顺时针旋转了90度。
所以，这一行代码就完成了旋转功能。程序代码实现了大大简化。

## window3 (游戏结束界面)
![Figure8. window3]()<br>
![Figure9. Table of window3 elements]()<br>
| 内容 | 属性 |
|-----|------|
| 分数板 | 260x260 pixels, 位于游戏框中间，显示分数 |
| 玩家指令 | 用鼠标点击play again按键可重新开始游戏 |

window3与window1类似，绘制分数板，设置玩家指令。

以上就是俄罗斯方块的制作简介。
源代码可以戳这里。

今天又进步了一点点！继续加油！