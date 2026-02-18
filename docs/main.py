import asyncio
import pygame
import random
import os
import json
import math

# --- 1. 基础配置 ---
CELL_SIZE = 40
GRID_WIDTH = 30
GRID_HEIGHT = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 60
FPS = 60

# --- 2. 主题配色配置 ---
THEMES = [
    {
        "name": "Classic Star",
        "bg": (20, 20, 40), "grid": (35, 35, 50), "text": (255, 255, 255),
        "p_head": (0, 255, 150), "p_body": (0, 100, 50),
        "e_head": (200, 50, 200), "e_body": (100, 0, 100)
    },
    {
        "name": "SpongeBob",
        "bg": (50, 150, 200), "grid": (60, 160, 210), "text": (255, 255, 0),
        "p_head": (255, 255, 0), "p_body": (139, 69, 19),
        "e_head": (255, 105, 180), "e_body": (200, 80, 150)
    },
    {
        "name": "Hello Kitty",
        "bg": (255, 240, 245), "grid": (255, 228, 225), "text": (255, 105, 180),
        "p_head": (255, 255, 255), "p_body": (255, 182, 193),
        "e_head": (50, 50, 50), "e_body": (100, 100, 100)
    },
    {
        "name": "Boonie Bears",
        "bg": (34, 139, 34), "grid": (0, 100, 0), "text": (255, 215, 0),
        "p_head": (139, 69, 19), "p_body": (205, 133, 63),
        "e_head": (255, 0, 0), "e_body": (200, 0, 0)
    },
    {
        "name": "Crayon Shin-chan",
        "bg": (255, 255, 224), "grid": (240, 230, 140), "text": (255, 0, 0),
        "p_head": (255, 200, 180), "p_body": (255, 0, 0),
        "e_head": (0, 0, 255), "e_body": (0, 0, 150)
    },
    {
        "name": "Nezha Mode",
        "bg": (139, 26, 26), "grid": (165, 42, 42), "text": (255, 215, 0),
        "p_head": (255, 218, 185), "p_body": (255, 69, 0),
        "e_head": (135, 206, 235), "e_body": (70, 130, 180)
    },
    {
        "name": "Pleasant Goat",
        "bg": (152, 251, 152), "grid": (143, 188, 143), "text": (0, 100, 0),
        "p_head": (255, 250, 250), "p_body": (135, 206, 250),
        "e_head": (80, 80, 80), "e_body": (105, 105, 105)
    },
    {
        "name": "Ultraman Mode",
        "bg": (25, 25, 112), "grid": (40, 40, 130), "text": (0, 255, 255),
        "p_head": (220, 220, 220), "p_body": (220, 20, 20),
        "e_head": (139, 69, 19), "e_body": (85, 107, 47)
    }
]

COLOR_FOOD_NORMAL = (255, 60, 60)
COLOR_FOOD_GOLD = (255, 215, 0)
COLOR_OVERLAY = (0, 0, 0, 180)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

DATA_FILE = "snake_data_v8.json"

DIFFICULTY_SETTINGS = {
    "EASY": {"speed": 200, "enemies": 1, "label": "EASY"},
    "NORMAL": {"speed": 130, "enemies": 3, "label": "NORMAL"},
    "HARD": {"speed": 90, "enemies": 6, "label": "HARD"}
}


# --- 3. 辅助绘制函数 ---
def draw_detailed_head(screen, x, y, size, color, direction, is_boosting=False):
    center_x = x + size // 2
    center_y = y + size // 2

    head_color = list(color)
    if is_boosting:
        head_color = [min(255, c + 50) for c in color]

    pygame.draw.circle(screen, head_color, (x + 6, y + 6), 10)
    if direction in [UP, DOWN]:
        pygame.draw.circle(screen, head_color, (x + size - 6, y + 6), 10)
    else:
        pygame.draw.circle(screen, head_color, (x + 6, y + size - 6), 10)

    pygame.draw.rect(screen, head_color, (x, y, size, size), border_radius=15)

    eye_radius = 7 if is_boosting else 6
    pupil_radius = 4 if is_boosting else 3

    eye_offset_x = direction[0] * 5
    eye_offset_y = direction[1] * 5

    left_eye = (center_x - 8 + eye_offset_x, center_y - 8 + eye_offset_y)
    right_eye = (center_x + 8 + eye_offset_x, center_y - 8 + eye_offset_y)

    if direction in [LEFT, RIGHT]:
        left_eye = (center_x + eye_offset_x, center_y - 8)
        right_eye = (center_x + eye_offset_x, center_y + 8)

    pygame.draw.circle(screen, (255, 255, 255), left_eye, eye_radius)
    pygame.draw.circle(screen, (0, 0, 0), (left_eye[0] + direction[0] * 2, left_eye[1] + direction[1] * 2),
                       pupil_radius)
    pygame.draw.circle(screen, (255, 255, 255), right_eye, eye_radius)
    pygame.draw.circle(screen, (0, 0, 0), (right_eye[0] + direction[0] * 2, right_eye[1] + direction[1] * 2),
                       pupil_radius)


# --- 4. 敌方AI类 ---
class EnemySnake:
    def __init__(self, game):
        self.game = game
        self.alive = True
        self.respawn()

    def respawn(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if x < 10: continue
            self.body = [(x, y), (x + 1, y), (x + 2, y)]
            self.prev_body = list(self.body)
            self.direction = LEFT
            break

    def move(self):
        if not self.alive: return
        self.prev_body = list(self.body)
        head = self.body[0]

        target = None
        min_dist = 9999
        all_foods = self.game.foods + self.game.golden_foods
        if not all_foods:
            target = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        else:
            for f in all_foods:
                d = abs(head[0] - f[0]) + abs(head[1] - f[1])
                if d < min_dist: min_dist, target = d, f

        possible_moves = []
        if target:
            if target[0] < head[0]:
                possible_moves.append(LEFT)
            elif target[0] > head[0]:
                possible_moves.append(RIGHT)
            if target[1] < head[1]:
                possible_moves.append(UP)
            elif target[1] > head[1]:
                possible_moves.append(DOWN)

        random.shuffle(DIRECTIONS)
        for d in DIRECTIONS:
            if d not in possible_moves: possible_moves.append(d)

        move_found = False
        for move_dir in possible_moves:
            if (move_dir[0] + self.direction[0] == 0) and (move_dir[1] + self.direction[1] == 0): continue
            new_head = (head[0] + move_dir[0], head[1] + move_dir[1])
            if self.is_safe(new_head):
                self.direction = move_dir
                self.body.insert(0, new_head)
                move_found = True
                break

        if not move_found:
            self.alive = False
            return

        head = self.body[0]
        if head in self.game.foods:
            self.game.foods.remove(head)
            self.game.add_food()
        elif head in self.game.golden_foods:
            self.game.golden_foods.remove(head)
        else:
            self.body.pop()

    def is_safe(self, pos):
        x, y = pos
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT: return False
        if pos in self.game.snake: return False
        if pos in self.body: return False
        for enemy in self.game.enemies:
            if enemy == self: continue
            if enemy.alive and pos in enemy.body: return False
        return True

    def check_player_collision(self):
        if not self.alive: return
        if self.body[0] in self.game.snake:
            self.alive = False
            self.game.score += 100
            self.game.create_particles(self.body[0], self.game.get_theme()["e_head"], count=15)

    def draw(self, screen, offset_y, alpha):
        if not self.alive: return
        theme = self.game.get_theme()
        for i in range(len(self.body)):
            curr, prev = self.body[i], self.prev_body[min(i, len(self.prev_body) - 1)]
            dx = prev[0] * CELL_SIZE + (curr[0] - prev[0]) * CELL_SIZE * alpha
            dy = prev[1] * CELL_SIZE + (curr[1] - prev[1]) * CELL_SIZE * alpha
            if i == 0:
                draw_detailed_head(screen, dx + 2, dy + 2 + offset_y, CELL_SIZE - 4, theme["e_head"], self.direction)
            else:
                pygame.draw.rect(screen, theme["e_body"], (dx + 2, dy + 2 + offset_y, CELL_SIZE - 4, CELL_SIZE - 4),
                                 border_radius=8)


# --- 5. 游戏主类 ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake V8.0 Web Edition")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # --- 字体设置 ---
        font_names = ['simhei', 'microsoftyahei', 'stheitirelight', 'arialunicode']
        target_font = None
        available_fonts = pygame.font.get_fonts()
        for f in font_names:
            if f in available_fonts:
                target_font = f
                break

        self.font = pygame.font.SysFont(target_font, 24)
        self.big_font = pygame.font.SysFont(target_font, 56, bold=True)
        self.cartoon_font = pygame.font.SysFont(target_font, 40, bold=True)

        # UI 初始化
        btn_w, btn_h = 340, 50
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2

        self.btn_easy = pygame.Rect(cx - btn_w // 2, cy - 80, btn_w, btn_h)
        self.btn_normal = pygame.Rect(cx - btn_w // 2, cy - 15, btn_w, btn_h)
        self.btn_hard = pygame.Rect(cx - btn_w // 2, cy + 50, btn_w, btn_h)
        self.btn_theme_menu = pygame.Rect(cx - btn_w // 2, cy + 115, btn_w, btn_h)

        self.btn_restart = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.btn_menu = pygame.Rect(cx - 100, cy + 90, 200, 50)

        self.btn_theme_back = pygame.Rect(cx - 100, WINDOW_HEIGHT - 80, 200, 50)

        self.state = "MENU"
        self.stats = self.load_data()
        self.current_difficulty = DIFFICULTY_SETTINGS["NORMAL"]
        self.theme_index = 0

        self.theme_card_rects = []
        self.init_theme_rects()

        self.reset_game()

    def init_theme_rects(self):
        card_w, card_h = 240, 160
        gap_x, gap_y = 30, 30
        cols = 4
        start_x = (WINDOW_WIDTH - (card_w * cols + gap_x * (cols - 1))) // 2
        start_y = 150

        self.theme_card_rects = []
        for i in range(len(THEMES)):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            self.theme_card_rects.append(pygame.Rect(x, y, card_w, card_h))

    def get_theme(self):
        return THEMES[self.theme_index]

    def load_data(self):
        default = {"high_score": 0, "games_played": 0}
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f: return {**default, **json.load(f)}
        except:
            pass
        return default

    def save_data(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.stats, f)
        except:
            pass

    def start_game(self, difficulty_key):
        self.current_difficulty = DIFFICULTY_SETTINGS[difficulty_key]
        self.reset_game()
        self.state = "PLAYING"

    def reset_game(self):
        sx, sy = 4, GRID_HEIGHT // 2
        self.snake = [(sx, sy), (sx - 1, sy), (sx - 2, sy)]
        self.snake_prev = list(self.snake)
        self.direction = RIGHT
        self.next_direction = RIGHT

        self.score = 0
        self.base_speed = self.current_difficulty["speed"]
        self.move_delay = self.base_speed
        self.last_move_time = pygame.time.get_ticks()
        self.is_boosting = False

        self.foods = []
        self.golden_foods = []
        self.foods = [self.get_random_pos() for _ in range(5)]

        self.enemies = []
        for _ in range(self.current_difficulty["enemies"]):
            self.enemies.append(EnemySnake(self))

        self.particles = []
        self.flash_effect = 0
        self.combo_count = 0
        self.last_gold_time = 0
        self.floating_texts = []

    def get_random_pos(self):
        while True:
            x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake and (x, y) not in self.foods and (x, y) not in self.golden_foods: return (x, y)

    def add_food(self):
        self.foods.append(self.get_random_pos())

    def add_golden_food(self):
        if len(self.golden_foods) < 3: self.golden_foods.append(self.get_random_pos())

    def handle_input(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if self.state == "MENU":
                    if self.btn_easy.collidepoint(mouse_pos):
                        self.start_game("EASY")
                    elif self.btn_normal.collidepoint(mouse_pos):
                        self.start_game("NORMAL")
                    elif self.btn_hard.collidepoint(mouse_pos):
                        self.start_game("HARD")
                    elif self.btn_theme_menu.collidepoint(mouse_pos):
                        self.state = "THEME_SELECT"

                elif self.state == "THEME_SELECT":
                    if self.btn_theme_back.collidepoint(mouse_pos): self.state = "MENU"
                    for i, rect in enumerate(self.theme_card_rects):
                        if rect.collidepoint(mouse_pos):
                            self.theme_index = i

                elif self.state == "GAMEOVER":
                    if self.btn_restart.collidepoint(mouse_pos):
                        self.reset_game()
                        self.state = "PLAYING"
                    elif self.btn_menu.collidepoint(mouse_pos):
                        self.state = "MENU"

            if event.type == pygame.KEYDOWN and self.state == "PLAYING":
                if event.key == pygame.K_SPACE:
                    self.state = "PAUSED"
                elif event.key == pygame.K_UP and self.direction != DOWN:
                    self.next_direction = UP
                elif event.key == pygame.K_DOWN and self.direction != UP:
                    self.next_direction = DOWN
                elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                    self.next_direction = LEFT
                elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                    self.next_direction = RIGHT
            elif event.type == pygame.KEYDOWN and self.state == "PAUSED":
                if event.key == pygame.K_SPACE: self.state = "PLAYING"

        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_UP] and self.direction == UP) or \
                    (keys[pygame.K_DOWN] and self.direction == DOWN) or \
                    (keys[pygame.K_LEFT] and self.direction == LEFT) or \
                    (keys[pygame.K_RIGHT] and self.direction == RIGHT):
                self.is_boosting = True
                self.move_delay = max(50, int(self.base_speed * 0.5))
            else:
                self.is_boosting = False
                self.move_delay = self.base_speed

        return True

    def update(self):
        if self.state != "PLAYING": return
        current_time = pygame.time.get_ticks()
        if random.random() < 0.005: self.add_golden_food()

        if current_time - self.last_move_time > self.move_delay:
            self.snake_prev = list(self.snake)
            self.direction = self.next_direction
            self.last_move_time = current_time

            head_x, head_y = self.snake[0]
            dx, dy = self.direction
            new_head = (head_x + dx, head_y + dy)

            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                self.game_over()
                return
            if new_head in self.snake:
                self.game_over()
                return
            for enemy in self.enemies:
                if enemy.alive and new_head in enemy.body:
                    self.game_over()
                    return

            self.snake.insert(0, new_head)
            should_shrink = False

            if new_head in self.foods:
                self.score += 10
                self.foods.remove(new_head)
                self.add_food()
                self.create_particles(new_head, COLOR_FOOD_NORMAL)

            elif new_head in self.golden_foods:
                self.score += 50
                self.golden_foods.remove(new_head)
                self.flash_effect = 10
                self.create_confetti(new_head)
                if current_time - self.last_gold_time < 5000:
                    self.combo_count += 1
                else:
                    self.combo_count = 1
                self.last_gold_time = current_time
                msgs = ["Awesome!", "Amazing!", "Unstoppable!", "Godlike!"]
                self.add_floating_text(f"Combo x{self.combo_count}! {random.choice(msgs)}",
                                       (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
            else:
                should_shrink = True

            if should_shrink: self.snake.pop()

            while len(self.snake_prev) < len(self.snake): self.snake_prev.append(self.snake_prev[-1])
            if len(self.snake_prev) > len(self.snake): self.snake_prev = self.snake_prev[:len(self.snake)]

            for enemy in self.enemies:
                enemy.move()
                enemy.check_player_collision()

            if self.is_boosting:
                self.create_particles(self.snake[-1], self.get_theme()["p_body"], count=2)

        for p in self.particles[:]:
            p['life'] -= 1
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['life'] <= 0: self.particles.remove(p)

        for ft in self.floating_texts[:]:
            ft['life'] -= 1
            ft['y'] -= 2
            if ft['life'] <= 0: self.floating_texts.remove(ft)

    def game_over(self):
        self.draw()
        pygame.display.flip()
        self.state = "GAMEOVER"
        self.stats["games_played"] += 1
        if self.score > self.stats["high_score"]: self.stats["high_score"] = self.score
        self.save_data()

    def create_particles(self, pos, color, count=10):
        px, py = pos[0] * CELL_SIZE + CELL_SIZE // 2, pos[1] * CELL_SIZE + CELL_SIZE // 2 + 60
        for _ in range(count):
            self.particles.append({
                'type': 'circle', 'x': px, 'y': py,
                'vx': random.uniform(-3, 3), 'vy': random.uniform(-3, 3),
                'life': random.randint(10, 20), 'color': color, 'size': random.randint(3, 6)
            })

    def create_confetti(self, pos):
        px, py = pos[0] * CELL_SIZE + CELL_SIZE // 2, pos[1] * CELL_SIZE + CELL_SIZE // 2 + 60
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]
        for _ in range(40):
            self.particles.append({
                'type': 'rect', 'x': px, 'y': py,
                'vx': random.uniform(-8, 8), 'vy': random.uniform(-8, 8),
                'life': random.randint(30, 50), 'color': random.choice(colors), 'size': random.randint(4, 8)
            })

    def add_floating_text(self, text, pos):
        self.floating_texts.append({
            'text': text, 'x': pos[0], 'y': pos[1], 'life': 60,
            'color': (random.randint(200, 255), random.randint(200, 255), 0)
        })

    def draw_button(self, rect, text, mouse_pos, base_color=(70, 70, 90)):
        color = (100, 100, 200) if rect.collidepoint(mouse_pos) else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=15)
        txt = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def lerp(self, start, end, alpha):
        return start + (end - start) * alpha

    def draw_theme_selection(self):
        self.screen.fill((30, 30, 40))

        title = self.big_font.render("THEME GALLERY", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 70)))

        mouse_pos = pygame.mouse.get_pos()

        for i, theme in enumerate(THEMES):
            rect = self.theme_card_rects[i]
            pygame.draw.rect(self.screen, theme["bg"], rect, border_radius=10)
            if i == self.theme_index:
                pygame.draw.rect(self.screen, (255, 215, 0), rect, 4, border_radius=10)
                sel_txt = self.font.render("SELECTED", True, (255, 215, 0))
                self.screen.blit(sel_txt,
                                 (rect.right - sel_txt.get_width() - 5, rect.bottom - sel_txt.get_height() - 5))
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=10)

            name_txt = self.font.render(theme["name"], True, theme["text"])
            self.screen.blit(name_txt, (rect.x + 10, rect.y + 10))

            preview_cx = rect.x + rect.width // 2
            preview_cy = rect.y + rect.height // 2 + 10
            draw_detailed_head(self.screen, preview_cx + 20, preview_cy, 30, theme["p_head"], RIGHT)
            pygame.draw.rect(self.screen, theme["p_body"], (preview_cx - 15, preview_cy, 30, 30), border_radius=5)
            pygame.draw.rect(self.screen, theme["p_body"], (preview_cx - 50, preview_cy, 30, 30), border_radius=5)
            pygame.draw.line(self.screen, theme["grid"], (rect.x, preview_cy), (rect.right, preview_cy), 1)
            pygame.draw.line(self.screen, theme["grid"], (preview_cx, rect.y), (preview_cx, rect.bottom), 1)

        self.draw_button(self.btn_theme_back, "Back to Menu", mouse_pos)

    def draw(self):
        theme = self.get_theme()

        if self.state == "THEME_SELECT":
            self.draw_theme_selection()
            return

        self.screen.fill(theme["bg"])
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "MENU":
            title = self.big_font.render("SNAKE BATTLE", True, theme["p_head"])
            self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 80)))
            stats = self.font.render(f"High: {self.stats['high_score']} | Games: {self.stats['games_played']}", True,
                                     theme["text"])
            self.screen.blit(stats, stats.get_rect(center=(WINDOW_WIDTH // 2, 130)))

            self.draw_button(self.btn_easy, "EASY (Slow, 1 Enemy)", mouse_pos, (50, 150, 50))
            self.draw_button(self.btn_normal, "NORMAL (Med, 3 Enemies)", mouse_pos, (50, 100, 150))
            self.draw_button(self.btn_hard, "HARD (Fast, 6 Enemies)", mouse_pos, (150, 50, 50))
            self.draw_button(self.btn_theme_menu, "Theme Gallery (Select Style)", mouse_pos, (100, 50, 150))

            # --- English Advice for Healthy Gaming ---

            # Title
            advice_title = self.font.render("Advice for Healthy Gaming", True, (200, 200, 200))
            self.screen.blit(advice_title, advice_title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 145)))

            # Content
            advice_lines = [
                "Resist bad games and refuse pirated games.",
                "Pay attention to self-protection and beware of being deceived.",
                "Playing games in moderation benefits the brain, while excessive gaming harms the body.",
                "Arrange your time reasonably and enjoy a healthy life."
            ]

            start_y = WINDOW_HEIGHT - 120
            for i, line in enumerate(advice_lines):
                advice_surf = self.font.render(line, True, (160, 160, 160))
                advice_rect = advice_surf.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 25))
                self.screen.blit(advice_surf, advice_rect)

            hint = self.font.render("Hold Direction Key to BOOST!", True, (255, 200, 0))
            self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))
            return

        offset_y = 60
        pygame.draw.rect(self.screen, (30, 30, 50), (0, 0, WINDOW_WIDTH, 60))
        score_txt = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        mode_txt = self.font.render(f"Mode: {self.current_difficulty['label']}", True, (200, 200, 200))
        self.screen.blit(score_txt, (20, 15))
        self.screen.blit(mode_txt, (WINDOW_WIDTH - 250, 15))

        if self.combo_count > 1:
            combo_txt = self.cartoon_font.render(f"Combo: {self.combo_count}", True, (255, 215, 0))
            self.screen.blit(combo_txt, (WINDOW_WIDTH // 2 - combo_txt.get_width() // 2, 10))

        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, theme["grid"], (x, offset_y), (x, WINDOW_HEIGHT))
        for y in range(offset_y, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, theme["grid"], (0, y), (WINDOW_WIDTH, y))

        for fx, fy in self.foods:
            pygame.draw.rect(self.screen, COLOR_FOOD_NORMAL,
                             (fx * CELL_SIZE + 4, fy * CELL_SIZE + 4 + offset_y, CELL_SIZE - 8, CELL_SIZE - 8),
                             border_radius=10)
        for gx, gy in self.golden_foods:
            glow = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 4
            pygame.draw.rect(self.screen, COLOR_FOOD_GOLD,
                             (gx * CELL_SIZE + 2 - glow, gy * CELL_SIZE + 2 + offset_y - glow, CELL_SIZE - 4 + glow * 2,
                              CELL_SIZE - 4 + glow * 2), border_radius=12)

        curr_time = pygame.time.get_ticks()
        alpha = min((curr_time - self.last_move_time) / self.move_delay, 1.0)

        for enemy in self.enemies: enemy.draw(self.screen, offset_y, alpha)

        for i, (cx, cy) in enumerate(self.snake):
            prev = self.snake_prev[i] if i < len(self.snake_prev) else (cx, cy)
            dx = self.lerp(prev[0] * CELL_SIZE, cx * CELL_SIZE, alpha)
            dy = self.lerp(prev[1] * CELL_SIZE, cy * CELL_SIZE, alpha)

            if i == 0:
                draw_detailed_head(self.screen, dx + 2, dy + 2 + offset_y, CELL_SIZE - 4, theme["p_head"],
                                   self.direction, self.is_boosting)
            else:
                body_color = [min(255, c + 40) for c in theme["p_body"]] if self.is_boosting else theme["p_body"]
                pygame.draw.rect(self.screen, body_color, (dx + 2, dy + 2 + offset_y, CELL_SIZE - 4, CELL_SIZE - 4),
                                 border_radius=8)

        for p in self.particles:
            if p['type'] == 'circle':
                pygame.draw.circle(self.screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
            elif p['type'] == 'rect':
                rect_size = p['size']
                if (pygame.time.get_ticks() // 50) % 2 == 0:
                    w, h = rect_size, rect_size / 2
                else:
                    w, h = rect_size / 2, rect_size
                pygame.draw.rect(self.screen, p['color'], (p['x'], p['y'], w, h))

        for ft in self.floating_texts:
            txt_surf = self.cartoon_font.render(ft['text'], True, ft['color'])
            outline = self.cartoon_font.render(ft['text'], True, (0, 0, 0))
            self.screen.blit(outline, (ft['x'] - txt_surf.get_width() // 2 + 2, ft['y'] + 2))
            self.screen.blit(txt_surf, (ft['x'] - txt_surf.get_width() // 2, ft['y']))

        if self.flash_effect > 0:
            s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            s.set_alpha(100)
            s.fill((255, 255, 255))
            self.screen.blit(s, (0, 0))
            self.flash_effect -= 1

        if self.state == "PAUSED":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            self.screen.blit(overlay, (0, 0))
            txt = self.big_font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

        if self.state == "GAMEOVER":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            self.screen.blit(overlay, (0, 0))
            panel = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 120, 300, 280)
            pygame.draw.rect(self.screen, (50, 50, 70), panel, border_radius=15)
            pygame.draw.rect(self.screen, (255, 255, 255), panel, 2, border_radius=15)
            over_txt = self.big_font.render("GAME OVER", True, (255, 100, 100))
            score_txt = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(over_txt, over_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80)))
            self.screen.blit(score_txt, score_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))
            self.draw_button(self.btn_restart, "Play Again", mouse_pos)
            self.draw_button(self.btn_menu, "Main Menu", mouse_pos)

    async def run(self):
        waiting_for_click = True
        while waiting_for_click:
            self.screen.fill((20, 20, 30))
            msg = self.font.render("Click Anywhere to Start Game", True, (255, 255, 255))
            self.screen.blit(msg, msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting_for_click = False

            await asyncio.sleep(0.05)

        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            pygame.display.flip()
            await asyncio.sleep(0)
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())