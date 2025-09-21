# 我的第4个游戏：飞扬的小鸟

今天，我来介绍我自学编程以来，练习完成的第4个项目：用python制作飞扬的小鸟. 
飞扬的小鸟（Flappy Bird）是一款敏捷类的像素风游戏。玩家操控小鸟飞行且避开绿色的管道。当小鸟飞过一组管道，玩家获得一分；如果小鸟碰到了障碍物，游戏结束。
飞扬的小鸟的程序相对简单，用python基本都能实现。因此，我尽量复刻了该游戏的所有元素。
接下来，就让我们一起来看看具体的制作攻略吧。

## 第一步：设计
我给游戏设计了三个界面：
1. window1: 开始界面
2. window2: 游戏运行界面
3. window3: 游戏结束界面
![Figure1. sketch of 3 windows]()<br>

## 第二步：制作一个简易版游戏
### 1. 建立大框架
三个界面的运行关系如下：
![Figure2. workflow of 3 windows]()<br>
a. 开始运行程序，显示window1
b. window1有一个开始按键，玩家点击，进入window2
c. window2运行游戏。当玩家死亡，进入window3
d. window3有一个再来一局的按键，玩家点击，重回window2

我们可以看到，window1只会出现一次，之后就是window2和3反复出现。
因此，我们可以把window1独立编写，而window2和3相互关联。那么可以建立一个这样的代码框架：
```
#window1的代码
code for window1

#window2和3的代码
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
我设置了一个game_active变量。
在window2运行过程中，若游戏结束，则game_active=False, 就进入了window3。
在window3运行过程中，若玩家点击再来一局按钮，则game_active=True, 就重回window2. 

这样游戏的大框架就搭建好了。接下去，我们来往里填细节。

### 2. window2：游戏运行
window2是整个游戏的主体。它包含以下这些元素：
| 内容 | 属性 |
|-----|------|
| 小鸟 | 具备翅膀震颤动画；会自然下落；按空格键向上飞行一次 |
| 管道 | 从右向左移动；每组管道分为上下两个，中间有间隔，间隔位置随机 |
| 游戏规则 | 若小鸟撞到障碍物，游戏结束 |
![Figure3. table of window2 elements]()<br>

#### 1. 小鸟
小鸟的飞行方式是：
a. 在没有任何操作方式时，小鸟自然下落
b. 当玩家按一次空格键，小鸟会向上飞行一段距离，之后又再次下落
我们将整个游戏窗口用坐标轴来表示，左上角为原点，横向为X轴，纵向为Y轴。
那么小鸟的位置就可以用两个数字(x,y)来表示。
小鸟自然下落，就可以看作y值增加；小鸟向上飞行，就是y值减小。
![Figure4. xy-system for the window and the bird movement]()<br>
因此，我用`bird_movement`来表示小鸟的运动情况，初始值为0. 
```
bird_movement = 0
```
接着，我用`gravity`来表示重力，小鸟始终受到重力因此会下落。这个值决定了游戏难度。经过多次调试，我将其设置为0.375. 
```
gravity = 0.375
```
当玩家按下空格键，小鸟向上运动一定的距离。这个值同样会影响游戏的难度。我最终将其设置为-7.5.
```
当玩家按下按键，并且这个键时空格键
if event.type == KEYDOWN and event.key == K_SPACE: 
    # 小鸟向上运动7.5
    bird_movement = -7.5 
```
接下去就是将这些变量组合在一起，实现小鸟飞行的动画效果。
首先，游戏的动画效果，其实就是系统循环式的在特定的位置绘制小鸟。
假设在初始时间t=0时，小鸟位于(100,100)，那么系统就会在(100,100)的位置绘制一个小鸟。
当t=1时，小鸟受到重力，x的值不变依然是100，y=100+0.375=100.375. 所以系统会在(100,100.375)的位置绘制一个小鸟. 
当t=2时，玩家按下空格键，x值不变，y=100.375+0.375-7.5=93.25. 所以系统会在(100,93.25)的位置绘制一个小鸟. 
因此，我们注意到：x值始终保持不变，而y取决于上一个时间点的y值，以及这一个时间点的运动情况。所以在绘制小鸟时，只需要不断更新现有的y值即可。
```
# 小鸟受到重力向下运动0.375
bird_movement += gravity 
# 小鸟的y值+小鸟在这个时间点的运动（若正，则下落；若负，则向上弹跳）
bird_rect.centery += int(bird_movement) 
# 在游戏界面绘制小鸟
windowSurface.blit(bird_surface, bird_rect) 
```

#### 2. 管道
管道运行的方式为：
a. 管道持续产生
b. 从右向左移动

首先，我们来实现管道持续产生的需求。
这里我用`USEREVENT`来定义一个特定的事件，将其取名为SPAWNPIPE。并设定一个时间间隔=1500毫秒。每过1500毫秒，就触发这个事件。
当游戏循环开始后，每当触发一次SPAWNPIPE，就往pipe_list里增添一个新的管道。
```
# 设置一个list，用来装管道。
pipe_list = []
# 自定义一个事件，用于持续生成管道
SPAWNPIPE = pygame.USEREVENT 
# 每过1500毫秒，就触发这个事件。
pygame.time.set_timer(SPAWNPIPE, 1500) 

# 当触发SPAWNPIPE事件时
if event.type == SPAWNPIPE：
    # 就往pipe_list里增添一个新的管道
    pipe_list.extend(create_pipe(pipe_gap))
```
这里我将生成管道的代码全都打包成一个函数：create_pipe(). 这样可以保持代码的整洁。
由于create_pipe()的代码中还嵌套了其他的函数，有点繁杂，在此不做赘述。有兴趣的可以去看我的源代码（源代码链接在文末）。

接着，我们来完成从右向左移动的需求。
其实这个概念和小鸟的运行类似，即改变x值的大小。从右向左移动，就是x值不断变小。
这里我设置管道运行速度为3. 接着将pipe_list中的管道每一个都提取出来，将它们原本的x值都减去3，就是当下这个时间点的x值。
确定位置后，我们将所有的管道全都绘制在游戏界面中。
```
# 管道运行速度
pipe_speed = 3
# 列举pipe_list中的每一个管道（pipe代表管道图片，pipe_rect代表管道位置, scored用于计分）
for pipe, pipe_rect, scored in pipe_list:
    # 管道的x值减去管道运行速度（即3）
    pipe_rect.centerx -= pipe_speed

# 列举所有的管道
for pipe, pipe_rect, _ in pipe_list:
    # 将每根管道绘制在其特定的位置上
    windowSurface.blit(pipe, pipe_rect)
```

#### 3. 游戏规则
在简易版游戏中，我们只考虑游戏结束的条件，即：当小鸟撞击障碍物时，游戏结束。
在第一部分构建大框架中，我们已经有了一个game_active变量，可以用来检测游戏是否结束。如今，我们需要设置小鸟撞击障碍物的代码。
这里我用到了pygame自带的一个函数：colliderect(). 它可以检测两个元素是否相撞。
具体来说，我将检测小鸟和管道相撞的代码打包写成了一个函数：check_collision(). 这个函数的输出是一个boolean，即True或False。
```
# 定义check_collision()函数，输入值是装有所有管道位置的pipe_list
def check_collision(pipe_list):
    # 列举pipe_list中的每一个管道（pipe代表管道图片，pipe_rect代表管道位置, scored用于计分）
    for pipe, pipe_rect, _ in pipe_list:
        # 若小鸟的位置与管道位置相撞
        if bird_rect.colliderect(pipe_rect):
            # 输出False
            return False
    # 若小鸟飞出天顶或撞击地面，同样死亡
    if bird_rect.top <= 0 or bird_rect.bottom >= GAMEHEIGHT:
        # 输出False
        return False 
    # 若以上情况均未发生，则输出True
    return True 

# 在游戏运行时，每次循环都检测小鸟与管道是否相撞，并将输出值赋予game_active变量
game_active = check_collision(pipe_list)
```

### 3. window3：游戏结束
当游戏结束，程序就会进入window3. 
在简易版游戏中，我们需要在window3设置一个按钮，当玩家点击时，重新回到window2.
想要设置这样一个按钮，具体来说，就是: 当鼠标在特定位置点击时，重启游戏。
因此，我们可以将代码分成：
a. 获取鼠标的位置
b. 获取按钮的位置
c. 检测鼠标的位置是否与按钮的位置重合
d. 检测鼠标是否点击
e. 当鼠标与按钮位置重合，并且鼠标点击时，重启游戏（game_active=True）

```
# 获取鼠标的位置
mouse_pos = pygame.mouse.get_pos()
# 设置mouse_click变量，用于检测鼠标是否点击。
mouse_click = False
# 检测鼠标与按钮的位置是否重合
hovered = restart_button_rect.collidepoint(mouse_pos)

# 检测程序运行时的玩家输入，若玩家点击鼠标，则mouse_click=True
for event in pygame.event.get():
    if event.type == MOUSEBUTTONDOWN:
        mouse_click = True

# window2和3的大框架
if game_active:
    code for window2
    game_active = check_collision(pipe_list)
else:
    code for window3
    # 当同时满足：a. 鼠标与按钮位置重合; b. 鼠标点击
    if hovered and mouse_click:
        reset_game()
        game_active = True
```

### 4. window1: 欢迎界面
现在回到最开头的window1. 
在简易版的游戏中，我只设置一个START按键。当玩家用鼠标点击后，进入window2. 
这个按键的程序设计和window3的按键是一样的。

综上，我们就可以得到一个简易版的飞扬的小鸟。
![Figure5. example of flappy bird v1]()<br>


## 第三步：优化细节
我具体在以下几个方面进行优化：
1. 绘制可爱的图片
2. 增加计分系统
3. 小鸟增加翅膀震颤和弹跳动画
4. 鼠标按键增加悬停动画

### 1. 绘制可爱的图片
简易版的游戏都只有方块，实在是太丑了。因此，我专门为这个游戏绘制了图片。
![Figure6. background+3 birds+2 pipes+2 buttons+scoreboard]()<br>

### 2. 增加计分系统
计分系统具体规则如下：
a. 每当小鸟穿过一组管道，得一分。
b. 游戏结束后，显示一个分数板，上面显示当局游戏的得分，以及历史最高分。

首先，来实现得分的需求。
具体来说，就是检测小鸟和管道的位置。当小鸟位于管道的右侧，则代表小鸟穿过管道，就得一分。
```
# 设置初始的分数为0
score = 0
# 在游戏运行时，当管道的x值小于小鸟的x值
if pipe_rect.centerx < bird_rect.centerx:
    # 分数+1
    score += 1
# 将目前的得分绘制在界面上
display_score(score)
```
这里我将绘制分数的代码打包成一个函数：display_score(). 具体不做赘述，有兴趣的可参考我的源代码。

接着，来实现计分板的需求。
将计分板图片导入，然后绘制在window3里合适的位置。
把当局游戏的分数与历史最高分作比较，若高于原有的历史最高分，则更新最高分。
```
# 导入分数板图片，并设定其位置
scoreboard_img = load_image("image/scoreboard.png", 144, 180).convert_alpha()
scoreboard_rect = scoreboard_img.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2-50))

# 当处于window3时，绘制分数板
windowSurface.blit(scoreboard_img, scoreboard_rect)
# 当本局游戏得分超过最高分，则更新最高分
if score > best_score:
    best_score = int(score)
# 将分数绘制在界面上
display_score(score, game_active, best_score)
```

### 3. 小鸟增加翅膀震颤和弹跳动画
我给window1的欢迎界面添加了一个具备翅膀震颤和弹跳动画的小鸟。

先来说翅膀震颤。
翅膀震颤的动画就是将三个小鸟的图片循环播放。
![Figure7. example of 3 bird images circular]()<br>
具体需要做的是：
a. 导入三张小鸟的图片，三张图的小鸟翅膀位置略微不同
b. 循环选取三张图片
c. 绘制小鸟

代码如下：
```
# 导入三张小鸟图片，并保存在一个list中
birds = [load_image(f"image/bird{i+1}.png", 51, 36).convert_alpha() for i in range(3)]
# 设置初始小鸟图片
bird_index = 0
bird_surface = birds[bird_index]
# 选定小鸟的位置
bird_rect = bird_surface.get_rect(center=(WINDOWWIDTH//2, GAMEHEIGHT//2))
# 设置循环速度
frame_count = 0

# 当显示window1时
while window1:
    frame_count += 1
    # 按照特定速率更新小鸟的图片
    if frame_count % 10 == 0:
        bird_index = (bird_index + 1) % len(birds)
    bird_surface = birds[bird_index]
    # 将小鸟绘制在界面上
    windowSurface.blit(bird_surface, bird_rect)
```

再来说弹跳。
弹跳动画就是小鸟的位置上下浮动。我通过一个sin()函数来实现。
```
# 导入math模块
imort math
# 运用sin()函数，设定小鸟上下浮动的距离
bounce_offset = math.sin(frame_count * 0.1) * 8
# 将上下浮动的距离整合到小鸟的位置中
bird_rect.centery = bird_base_y + int(bounce_offset)
```

### 4. 鼠标按键增加悬停动画
我为window1和3的按键设计了悬停动画。具体分为两步：
a. 当鼠标位于按键范围内时，显示手的图形；当鼠标位于界面其他位置时，显示箭头的图形。
b. 当鼠标位于按键范围时，按键放大

首先，先来完成箭头和手的图形切换。
由于系统自带箭头和手的图形，所以可以直接用函数口令设置。
```
# 当鼠标位置与按钮位置重合时
if start_button_rect.collidepoint(mouse_pos):
    # 光标为手的图形
    pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
else:
    # 否则，光标为箭头图形
    pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)
```

接着，添加按键放大的动画。
![Figure8. example of button hover]()<br>
我设置了一个放大系数：若鼠标与按键重合，则放大1.1倍；若不重合，则不放大。然后将放大系数与按键原本的图像相乘，就可以根据鼠标位置放大按键。
代码如下：
```
# 设置放大系数
scale_factor = 1.1 if hovered else 1.0
# 根据放大系数，设置按键的宽和高
start_button_width = int(start_button_img.get_width() * scale_factor)
start_button_height = int(start_button_img.get_height() * scale_factor)
# 根据宽和高，更新按键的图像和位置
start_button_img_scaled = pygame.transform.smoothscale(start_button_img, (start_button_width, start_button_height))
start_button_rect_scaled = start_button_img_scaled.get_rect(center=start_button_rect.center)
# 绘制按键
windowSurface.blit(start_button_img_scaled, start_button_rect_scaled)
```

经过细节优化，我们最终就可以得到一个更加可爱的游戏了。
![Figure9. example of flappy bird v2]()<br>


至此，飞扬的小鸟游戏制作完成！
谢谢阅读！


源代码：点击这里
我的电脑： Mac Pro
编程语言：Python
编程软件：VS code
游戏制作模块：pygame
