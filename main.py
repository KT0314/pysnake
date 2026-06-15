# main.py
import pygame
import random
import sys
import config
from detector import ColorDetector


# --- 自訂粒子特效類別 ---
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.lifetime = 20
        self.color = random.choice(config.COLOR_PARTICLES)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.size, self.size))


# --- 初始化 Pygame ---
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((config.WINDOW_SIZE, config.WINDOW_SIZE))
pygame.display.set_caption("視覺貪食蛇 - 15分通關版")
clock = pygame.time.Clock()

# 建立遊戲字型（新增支援中文的微軟正黑體）
game_font = pygame.font.SysFont("Microsoft JhengHei", 24)
big_font = pygame.font.SysFont("Microsoft JhengHei", 48, bold=True)  # 用於結算畫面的大字

# --- 初始化遊戲變數 ---
snake = [[10, 10], [10, 11], [10, 12]]
direction = "UP"
food = [random.randint(0, config.CELL_COUNT - 1), random.randint(0, config.CELL_COUNT - 1)]
score = 0
game_over = False
game_win = False  # 新增：記錄是否通關

# 基礎遊戲速度 (FPS)
base_speed = 7

# 怪物相關變數
monster = None
monster_dir = "RIGHT"
last_monster_move_time = 0

# 存放目前畫面上所有粒子的清單
particles_list = []

# --- 初始化視覺偵測器 ---
detector = ColorDetector()
print("遊戲即時啟動！請在鏡頭前舉起【綠色物體】控制蛇的移動。")
print("提示：遊戲中隨時按下鍵盤的【ESC】鍵即可退出遊戲。")

# --- 遊戲主迴圈 ---
while not game_over and not game_win:
    # A. 處理視窗關閉與 ESC
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_over = True
                break

    if game_over:
        break

    # B. 透過偵測器模組獲取新方向
    direction = detector.get_direction(direction)

    # C. 更新蛇的位置
    head = snake[0].copy()
    if direction == "UP":
        head[1] -= 1
    elif direction == "DOWN":
        head[1] += 1
    elif direction == "LEFT":
        head[0] -= 1
    elif direction == "RIGHT":
        head[0] += 1

    # 蛇穿牆邏輯
    head[0] = head[0] % config.CELL_COUNT
    head[1] = head[1] % config.CELL_COUNT

    # 檢查是否撞到白色怪物
    if monster and head == monster:
        print(f"遊戲結束！你撞到了白色怪物。最終得分: {score}")
        game_over = True
        break

    # 檢查是否撞到自己
    if head in snake:
        print(f"遊戲結束！你撞到自己了。最終得分: {score}")
        game_over = True
        break

    snake.insert(0, head)

    # D. 碰撞偵測（吃到食物）
    if head == food:
        score += 1
        print(f"得分！目前分數: {score}")

        # 吃到食物時炸出粒子
        food_center_x = food[0] * config.CELL_SIZE + config.CELL_SIZE // 2
        food_center_y = food[1] * config.CELL_SIZE + config.CELL_SIZE // 2
        for _ in range(25):
            particles_list.append(Particle(food_center_x, food_center_y))

        # 🌟【關鍵修改：檢查是否達到 15 分通關門檻】🌟
        if score >= 15:
            print("恭喜通關！！")
            game_win = True
            break

        food = [random.randint(0, config.CELL_COUNT - 1), random.randint(0, config.CELL_COUNT - 1)]
    else:
        snake.pop()

    # E. 怪物巡邏邏輯
    current_time = pygame.time.get_ticks()

    if score >= 5:
        # 如果剛滿 5 分，生成初始怪物
        if monster is None:
            while True:
                monster = [random.randint(0, config.CELL_COUNT - 1), random.randint(0, config.CELL_COUNT - 1)]
                if monster not in snake and monster != food:
                    break
            monster_dir = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            last_monster_move_time = current_time

        # 每過 1000 毫秒 (1秒) 移動一格
        elif current_time - last_monster_move_time >= 1000:
            if random.random() < 0.30:
                if monster_dir in ["UP", "DOWN"]:
                    monster_dir = random.choice(["LEFT", "RIGHT"])
                else:
                    monster_dir = random.choice(["UP", "DOWN"])

            if monster_dir == "UP":
                monster[1] -= 1
            elif monster_dir == "DOWN":
                monster[1] += 1
            elif monster_dir == "LEFT":
                monster[0] -= 1
            elif monster_dir == "RIGHT":
                monster[0] += 1

            # 怪物穿牆
            monster[0] = monster[0] % config.CELL_COUNT
            monster[1] = monster[1] % config.CELL_COUNT
            last_monster_move_time = current_time

            # 移動後檢查是否撞上蛇頭
            if monster == snake[0]:
                print(f"遊戲結束！白色怪物主動撞上了你。最終得分: {score}")
                game_over = True
                break

    # 更新粒子狀態
    for p in particles_list[:]:
        p.update()
        if p.lifetime <= 0:
            particles_list.remove(p)

    # F. 繪製遊戲畫面
    screen.fill(config.COLOR_BG)

    # 1. 畫食物
    pygame.draw.rect(screen, config.COLOR_FOOD,
                     (food[0] * config.CELL_SIZE, food[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE))

    # 2. 畫白色怪物
    if monster:
        pygame.draw.rect(screen, config.COLOR_MONSTER,
                         (monster[0] * config.CELL_SIZE, monster[1] * config.CELL_SIZE, config.CELL_SIZE,
                          config.CELL_SIZE))

    # 3. 畫蛇身
    for block in snake:
        pygame.draw.rect(screen, config.COLOR_SNAKE,
                         (block[0] * config.CELL_SIZE, block[1] * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE))

    # 4. 畫粒子
    for p in particles_list:
        p.draw(screen)

    # 5. 畫右上角計分板
    score_surface = game_font.render(f"SCORE: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (config.WINDOW_SIZE - 130, 15))

    pygame.display.flip()

    # 5分後才開始慢慢加速的邏輯
    if score < 5:
        current_fps = base_speed
    else:
        current_fps = base_speed + ((score - 5) // 2)
        current_fps = min(current_fps, 15)

    clock.tick(current_fps)

# 🌟【全新擴充：遊戲結束/通關的「凍結結算畫面」】🌟
# 當跳出上面的迴圈後，程式不會立刻關閉，而是定格並在畫面上顯示結果，直到玩家按下 ESC 或關閉視窗。
waiting_for_exit = True
while waiting_for_exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting_for_exit = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                waiting_for_exit = False

    # 根據是「通關」還是「輸掉」來決定要顯示的文字與顏色
    if game_win:
        text_str = "恭喜通關！"
        text_color = (0, 255, 128)  # 耀眼的綠色
    else:
        text_str = "GAME OVER"
        text_color = (255, 80, 80)  # 警示的紅色

    # 渲染主標題文字
    result_surface = big_font.render(text_str, True, text_color)
    result_rect = result_surface.get_rect(center=(config.WINDOW_SIZE // 2, config.WINDOW_SIZE // 2 - 30))

    # 渲染提示結束的副標題文字
    tip_surface = game_font.render("按下 [ESC] 或 [空白鍵] 關閉遊戲", True, (200, 200, 200))
    tip_rect = tip_surface.get_rect(center=(config.WINDOW_SIZE // 2, config.WINDOW_SIZE // 2 + 40))

    # 繪製半透明的黑色遮罩，讓結算文字更清晰
    overlay = pygame.Surface((config.WINDOW_SIZE, config.WINDOW_SIZE))
    overlay.set_alpha(3)  # 微調漸層感
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # 把文字貼上螢幕
    screen.blit(result_surface, result_rect)
    screen.blit(tip_surface, tip_rect)
    pygame.display.flip()
    clock.tick(10)

# --- 釋放資源與關閉 ---
detector.release()
pygame.quit()
sys.exit()