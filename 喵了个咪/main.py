import pgzrun
import random
import pygame
import math

# 定义游戏相关属性
TITLE = '喵了个咪'
WIDTH = 600
HEIGHT = 720

# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66

# 下方牌堆的位置
DOCK = Rect((90, 564), (T_WIDTH * 8, T_HEIGHT))  # 缓冲栏最多容纳8个

# 上方的所有牌
tiles = []
# 牌堆里的牌（缓冲栏）
docks = []

# 游戏状态
STATE_MAIN_MENU = 1
STATE_PLAYING = 2
STATE_GAME_OVER = 3

# 当前游戏状态
game_state = STATE_MAIN_MENU

# 加载字体
pygame.font.init()
font = pygame.font.Font('C:/Windows/fonts/msyh.ttc', 50)  # 指定字体文件和字号

# 倒计时相关变量
countdown = 60  # 倒计时60秒

def initialize_game():
    global tiles, docks, game_state, countdown
    # 初始化牌组，每种类型图片的数量要相等且为3的倍数
    ts = list(range(1, 7)) * (total_tiles // 6)  # 6种图案，确保牌的数量足够
    random.shuffle(ts)

    # 五角星的顶点和中心点的计算
    def get_star_points(center_x, center_y, outer_radius, inner_radius, num_points=5):
        points = []
        angle = math.pi / num_points
        for i in range(num_points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center_x + math.cos(i * angle) * radius
            y = center_y + math.sin(i * angle) * radius
            points.append((x, y))
        return points

    # 生成五角星的顶点
    center_x, center_y = WIDTH // 2, HEIGHT // 2 - 100
    outer_radius = 200
    inner_radius = 100
    star_points = get_star_points(center_x, center_y, outer_radius, inner_radius)

    # 在五角星路径上均匀排列牌
    tiles = []
    n = 0
    for x, y in star_points:
        t = ts[n % len(ts)]  # 获取牌种类
        n += 1
        tile = Actor(f'pattern{t}')  # 使用 patternX 图片创建 Actor 对象
        tile.pos = x, y  # 设定位置
        tile.tag = t  # 记录种类
        tile.status = 1  # 全部设置为可点击
        tiles.append(tile)

    # 补充五角星内部的牌，使总牌数超过50
    for i in range(50 - len(tiles)):
        x = random.randint(center_x - inner_radius, center_x + inner_radius)
        y = random.randint(center_y - inner_radius, center_y + inner_radius)
        t = ts[n % len(ts)]
        tile = Actor(f'pattern{t}')
        tile.pos = x, y
        tile.tag = t
        tile.status = 1
        tiles.append(tile)
        n += 1

    docks = []
    game_state = STATE_PLAYING
    countdown = 60  # 重置倒计时
    clock.schedule_interval(update_countdown, 1.0)  # 每秒更新一次倒计时

# 计算总牌数
total_tiles = 54  # 设定牌数大于50

# 加载背景图片
background = Actor('background.png')

def draw_main_menu():
    screen.clear()
    background.draw()
    draw_text('喵了个咪', WIDTH // 2, HEIGHT // 2 - 100)
    draw_text('开始游戏', WIDTH // 2, HEIGHT // 2)
    draw_text('退出游戏', WIDTH // 2, HEIGHT // 2 + 50)

def draw_game_over():
    screen.clear()
    background.draw()
    if len(docks) >= 8 or countdown <= 0:  # 缓冲栏满或时间到，游戏失败
        draw_text('失败', WIDTH // 2, HEIGHT // 2 - 50)
    elif len(tiles) == 0:  # 所有牌被消除，游戏胜利
        draw_text('胜利', WIDTH // 2, HEIGHT // 2 - 50)
    draw_text('重新开始', WIDTH // 2, HEIGHT // 2 + 50)
    draw_text('退出游戏', WIDTH // 2, HEIGHT // 2 + 100)

def draw():
    global game_state
    if game_state == STATE_MAIN_MENU:
        draw_main_menu()
    elif game_state == STATE_PLAYING:
        screen.clear()
        background.draw()
        for tile in tiles:
            tile.draw()
        for i, tile in enumerate(docks):
            tile.left = DOCK.x + i * T_WIDTH
            tile.top = DOCK.y
            tile.draw()
        draw_text(f'时间: {countdown}', WIDTH // 2, HEIGHT - 50)  # 显示倒计时在屏幕下方
        if len(docks) >= 8 or countdown <= 0:
            game_state = STATE_GAME_OVER
        elif len(tiles) == 0:
            game_state = STATE_GAME_OVER
    elif game_state == STATE_GAME_OVER:
        draw_game_over()

def draw_text(text, x, y):
    text_surface = font.render(text, True, (255, 255, 255))
    screen.surface.blit(text_surface, (x - text_surface.get_width() // 2, y - text_surface.get_height() // 2))

def on_mouse_down(pos):
    global docks, game_state
    if game_state == STATE_MAIN_MENU:
        if Rect((WIDTH // 2 - 100, HEIGHT // 2 - 30), (200, 50)).collidepoint(pos):
            initialize_game()  # 初始化游戏
        elif Rect((WIDTH // 2 - 100, HEIGHT // 2 + 20), (200, 50)).collidepoint(pos):
            exit()
    elif game_state == STATE_PLAYING:
        if len(docks) >= 8 or len(tiles) == 0:  # 游戏结束时不响应点击
            return
        for tile in reversed(tiles):
            if tile.status == 1 and tile.collidepoint(pos):
                tile.status = 2
                tiles.remove(tile)

                diff = [t for t in docks if t.tag != tile.tag]
                if len(docks) - len(diff) < 2:
                    docks.append(tile)
                else:
                    docks = diff

                for down in tiles:
                    if down.colliderect(tile):
                        down.status = 1
                return
    elif game_state == STATE_GAME_OVER:
        if Rect((WIDTH // 2 - 100, HEIGHT // 2 + 50), (200, 50)).collidepoint(pos):
            initialize_game()
        elif Rect((WIDTH // 2 - 100, HEIGHT // 2 + 100), (200, 50)).collidepoint(pos):
            exit()

def update_countdown():
    global countdown, game_state
    if game_state == STATE_PLAYING:
        countdown -= 1
        if countdown <= 0:
            game_state = STATE_GAME_OVER

# 运行游戏
pgzrun.go()
