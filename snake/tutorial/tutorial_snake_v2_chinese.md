# 自学编程汇报 NO.2：贪吃蛇开发记：从入门到进阶

我的电脑： **Mac Pro**<br>
我使用的编程语言：**Python**<br>
我使用的编程软件：**VS code**<br>
我使用的游戏制作模块：**pygame**<br>
详细的代码逐行解析：[点击这里](https://github.com/guoweier/GameHut/blob/main/snake/tutorial/tutorial_snake_v2.md)<br>
完整的代码：[点击这里](https://github.com/guoweier/GameHut/blob/main/snake/snake_v2.py)<br>
参考模板：Google Snake Game

上一次我介绍了我用pygame制作的第一款游戏贪吃蛇。如今，它已经完成了华丽的蜕变。
![Figure 1. window2 v1 vs v2]()
接下去，我来分享我是如何从版本1到版本2的。

首先，我们来看第一版和第二版有哪些区别。
1. window1：欢迎界面
![Figure 2. window1 v1 vs v2]()
    | 差异    | 第一版   | 第二版   |
    |--------|---------|----------|
    | 背景    | 黑色     | 绿色     |
    | 窗口大小 | 600x600 | 640x700 |
2. window2：游戏界面
![Figure 3. window2 v1 vs v2]()
    | 差异    | 第一版        | 第二版                                             |
    |----------|------------|--------------------------------------------------|
    | 界面   | 600x600 黑色  | 640x700 绿色背景, 600x600 格子游戏框, 界面上方有分数条 |
    | 食物   | 1个绿色方块 | 可爱的苹果图片，有闪烁动画                              |
    | 蛇    | 3个红色方块  | 可爱的蛇蛇图片，当靠近食物时有张嘴的动画           |
    | 分数条 | 无           | 在界面最上方实时显示分数             |
3. window3：结束界面
![Figure 4. window3 v1 vs v2]()
    | 差异      | 第一版                   | 第二版                             |
    |------------|--------------------------|--------------------------|
    | 蛇      | 无动画             | 眨眼动画                         |
    | 分数板 | 白色半透明长方形，显示4行文字 | 可爱的分数板图片 |

接着，我们分别来看是如何实现这些改动的。
### window1：欢迎界面
这一界面没有大的改动。我只需要调整最开始的variable，修改颜色和窗口大小即可。(详细代码解析可见*tutorial link*)
### window2：游戏界面
1. 食物
- 导入并绘制图片
    - 导入图片函数：
    ```
    def load_image(file, x, y):
        img = pygame.image.load(file)
        img = pygame.transform.scale(img, (x,y))
        return img
    ```
    - 绘制图片函数：
    ```
    def draw_image(img, surface, x, y):
        img_rect = img.get_rect(center=(x,y))
        surface.blit(img, img_rect)
    ```
- 制作闪烁动画:
    - 食物的动画即多个不同的图层在规定时间内循环播放。所以，我将苹果图片设置成不同的大小并保存在一个list中。我将其设置成`sprite`, 然后再游戏运行时循环显示这个list中的图片。
2. 蛇
- 分别导入蛇头，蛇身，蛇尾的图片：
    - 使用之前定义的函数，即可导入和绘制贪吃蛇。
    - 这里有两个注意点：
        - 当蛇改变运动方向时，需恰当地旋转图片。
        - 蛇转弯后，有一个转角，需实时合理显示转角图片。
        我绘制了四个转角，并将这四个转角图片导入保存在list中。通过转角与相邻两个蛇身的位置分析，我们可以判断显示哪一个转角。
        ![Figure 5. corner image choosen]()
- 制作张嘴动画
    - 将多个图层（即不同嘴巴大小的蛇头）放置在list中。接着，计算蛇头与食物之间的距离，在蛇头运动到食物的一定范围内时，显示特定的张嘴动画。
    ![Figure 6. correlation between food and snakehead]()
3. 分数条
- 这个部分相对简单，只需要将实时记录的分数显示在界面最上方即可。

详细代码解析可见*tutorial link*

### window3：结束界面
1. 绘制分数板
- 这一部分我只是画了一张400x300的分数板图片，然后将图片导入显示即可。
2. 制作眨眼动画
- 和之前的动画制作类似。将不同眼睛大小的蛇头图片导入后放置在list中。接着将其设置成`sprite`, 然后循环显示这个list中的图片。
3. 调整代码结构
第二版的window3（结束界面）最大的难点在于：它既需要显示固定的图片（例如分数板），又需要显示动画（例如会眨眼的蛇头）。
为了达到这个效果，我将整体的代码结构做了调整：
首先，我设置了两个函数：第一个函数用于绘制所有的固定元素，例如分数板、背景图、蛇身蛇尾等等。第二个函数专门用来绘制动画元素，也就是会眨眼的蛇头。
第二，我建立了一个新的while loop。
    - 当window2（游戏界面）退出时，这个新的while loop才会开始运行。
    - 在运行时，它只运行固定元素的函数一次，但会循环运行动画元素的函数。这样就能保证固定元素始终稳定显示，而动画元素循环更新。
    - 当玩家输入指令开始新一局游戏或者选择退出，这个while loop就停止。
所以，现在我的整体代码结构变成了如下所示：
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

以上就是我的第二版贪吃蛇的制作概述。
详细的代码解析可以戳这里。
源代码可以戳这里。

今天又进步了一点点！继续加油！
