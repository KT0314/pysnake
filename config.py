# config.py

CELL_SIZE = 20
CELL_COUNT = 25
WINDOW_SIZE = CELL_SIZE * CELL_COUNT  # 500x500 像素

# 顏色定義 (RGB)
COLOR_BG = (30, 30, 30)
COLOR_SNAKE = (0, 255, 0)
COLOR_FOOD = (255, 50, 50)
COLOR_MONSTER = (255, 255, 255)  # 白色怪物
#例子效果
COLOR_PARTICLES = [
    (255, 255, 100),  # 亮黃
    (255, 150, 50),   # 橘色
    (255, 50, 50),    # 紅色（呼應食物顏色）
    (100, 255, 255)   # 亮藍
]