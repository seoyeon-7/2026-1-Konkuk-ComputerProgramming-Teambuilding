import pygame
import sys
import random
import math
import json
import os
from collections import deque

# 초기화 및 화면 크기 설정
pygame.init()
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("도망쳐! 네모 - 미로 탈출 (마스터 에디션 PRO 최종 완벽본)")
clock = pygame.time.Clock()

SAVE_FILE = "maze_save.json"

# ─────────────────────────────────────────
# 색상 / 폰트
# ─────────────────────────────────────────
COLORS = {
    "빨강": (220, 50, 50), "주황": (255, 165, 0), "노랑": (255, 220, 0),
    "초록": (34, 160, 34), "파랑": (30, 80, 220), "남색": (0, 0, 128),
    "보라": (128, 0, 180), "핑크": (255, 100, 180), "민트": (62, 180, 137),
    "차콜": (54, 69, 79), "화이트": (255, 255, 255), "블랙": (10, 10, 10),
    "그레이": (150, 150, 150), "연그레이": (220, 220, 220),
    "벽": (50, 65, 85),        
    "바닥": (240, 244, 248),    
    "출구": (46, 204, 113), "열쇠": (241, 196, 15), "HUD_BG": (20, 20, 30), "패널": (25, 25, 35),
    "아이템_원": (52, 152, 219), "함정_원": (231, 76, 60)
}

try:
    FONT_BIG = pygame.font.SysFont("malgungothic", 42, bold=True)
    FONT_MID = pygame.font.SysFont("malgungothic", 22, bold=True)
    FONT_SMALL = pygame.font.SysFont("malgungothic", 15, bold=True)
    FONT_TINY = pygame.font.SysFont("malgungothic", 13, bold=True)
except:
    FONT_BIG = pygame.font.Font(None, 54)
    FONT_MID = pygame.font.Font(None, 30)
    FONT_SMALL = pygame.font.Font(None, 22)
    FONT_TINY = pygame.font.Font(None, 18)

SHAPES = ["네모", "동그라미", "세모", "역세모", "다이아", "오각형", "하트", "별", "육각형", "십자가"]

# 난이도별 세팅 (몬스터 수: 이지 1, 보통 2, 하드 3 고정)
DIFFICULTY = {
    "Easy": {
        "monsters": 1, "time": 120, 
        "trap_rate": 0.015,   
        "item_rate": 0.07, "label": "쉬움", "monster_speed": 1.4, 
        "cols": 21, "rows": 21 
    },
    "Normal": {
        "monsters": 2, "time": 180, 
        "trap_rate": 0.035,   
        "item_rate": 0.05, "label": "보통", "monster_speed": 2.1, 
        "cols": 31, "rows": 31 
    },
    "Hard": {
        "monsters": 3, "time": 250, 
        "trap_rate": 0.05, "item_rate": 0.04, "label": "어려움", "monster_speed": 2.8, 
        "cols": 41, "rows": 41 
    },
}

# ─────────────────────────────────────────
# 세이브 시스템
# ─────────────────────────────────────────
def load_game_data():
    loaded_data = None
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
        except:
            pass

    default_unlocked = {}
    default_best_time = {}
    for diff in ["Easy", "Normal", "Hard"]:
        for stage in range(1, 6):
            key = f"{diff}_{stage}"
            default_unlocked[key] = True if stage == 1 else False
            default_best_time[key] = None

    if loaded_data is None:
        return {"unlocked": default_unlocked, "best_time": default_best_time}
    
    if "unlocked" not in loaded_data:
        loaded_data["unlocked"] = default_unlocked
    if "best_time" not in loaded_data:
        loaded_data["best_time"] = default_best_time
        
    for diff in ["Easy", "Normal", "Hard"]:
        loaded_data["unlocked"][f"{diff}_1"] = True
        
    return loaded_data

def save_game_data(data):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ─────────────────────────────────────────
# 도형 그리기 함수
# ─────────────────────────────────────────
def draw_shape(surface, shape, color, cx, cy, r):
    cx, cy, r = int(cx), int(cy), int(r)
    outline = COLORS["블랙"]
    if shape == "네모":
        pygame.draw.rect(surface, color, (cx-r, cy-r, r*2, r*2))
        pygame.draw.rect(surface, outline, (cx-r, cy-r, r*2, r*2), 2)
    elif shape == "동그라미":
        pygame.draw.circle(surface, color, (cx, cy), r)
        pygame.draw.circle(surface, outline, (cx, cy), r, 2)
    elif shape == "세모":
        pts = [(cx, cy-r), (cx-r, cy+r), (cx+r, cy+r)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "역세모":
        pts = [(cx-r, cy-r), (cx+r, cy-r), (cx, cy+r)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "다이아":
        pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "오각형":
        pts = [(cx, cy-r), (cx+int(r*0.95), cy-int(r*0.31)),
               (cx+int(r*0.59), cy+int(r*0.81)), (cx-int(r*0.59), cy+int(r*0.81)),
               (cx-int(r*0.95), cy-int(r*0.31))]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "하트":
        pts = [(cx, cy+r), (cx-r, cy-int(0.2*r)), (cx-int(0.5*r), cy-r),
               (cx, cy-int(0.4*r)), (cx+int(0.5*r), cy-r), (cx+r, cy-int(0.2*r))]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "별":
        pts = [(cx, cy-r), (cx+int(0.25*r), cy-int(0.25*r)), (cx+r, cy-int(0.25*r)),
               (cx+int(0.4*r), cy+int(0.15*r)), (cx+int(0.6*r), cy+r), (cx, cy+int(0.4*r)),
               (cx-int(0.6*r), cy+r), (cx-int(0.4*r), cy+int(0.15*r)), (cx-r, cy-int(0.25*r)),
               (cx-int(0.25*r), cy-int(0.25*r))]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "육각형":
        pts = [(cx, cy-r), (cx+int(r*0.87), cy-r//2), (cx+int(r*0.87), cy+r//2),
               (cx, cy+r), (cx-int(r*0.87), cy+r//2), (cx-int(r*0.87), cy-r//2)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "십자가":
        t = int(r * 0.35)
        pts = [(cx-t,cy-r),(cx+t,cy-r),(cx+t,cy-t),(cx+r,cy-t),
               (cx+r,cy+t),(cx+t,cy+t),(cx+t,cy+r),(cx-t,cy+r),
               (cx-t,cy+t),(cx-r,cy+t),(cx-r,cy-t),(cx-t,cy-t)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)

# ─────────────────────────────────────────
# 버튼 클래스
# ─────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, bg, fg, cb, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.bg, self.fg, self.cb = text, bg, fg, cb
        self.hovered = False
        self.enabled = enabled

    def draw(self, surface):
        if not self.enabled:
            pygame.draw.rect(surface, (50, 50, 60), self.rect, border_radius=8)
            pygame.draw.rect(surface, (30, 30, 40), self.rect, 2, border_radius=8)
            s = FONT_MID.render(self.text, True, (100, 100, 110))
            surface.blit(s, s.get_rect(center=self.rect.center))
            lock_s = FONT_TINY.render("🔒 잠김", True, COLORS["빨강"])
            surface.blit(lock_s, (self.rect.right - 45, self.rect.top + 5))
            return

        col = tuple(min(255, c+30) for c in self.bg) if self.hovered else self.bg
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["블랙"], self.rect, 2, border_radius=8)
        s = FONT_MID.render(self.text, True, self.fg)
        surface.blit(s, s.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if not self.enabled: return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.cb()

# ─────────────────────────────────────────
# 미로 생성
# ─────────────────────────────────────────
def generate_maze(cols, rows):
    grid = [[1] * cols for _ in range(rows)]
    def carve(cx, cy):
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx+dx, cy+dy
            if 0 < nx < cols-1 and 0 < ny < rows-1 and grid[ny][nx] == 1:
                grid[cy+dy//2][cx+dx//2] = 0
                grid[ny][nx] = 0
                carve(nx, ny)
    grid[1][1] = 0
    carve(1, 1)
    
    grid[rows-2][cols-2] = 0
    if grid[rows-2][cols-3] == 1 and grid[rows-3][cols-2] == 1:
        grid[rows-2][cols-3] = 0
    return grid

# ─────────────────────────────────────────
# 플레이어 클래스
# ─────────────────────────────────────────
class Player:
    BASE_SPEED = 3.8
    def __init__(self, x, y, shape, color):
        self.x, self.y = float(x), float(y)
        self.shape, self.color = shape, color
        self.hp = 3
        self.speed = self.BASE_SPEED
        self.has_key = False
        self.invincible = 0
        self.slow_timer = 0
        self.vision_expand = 0
        self.speed_boost = 0
        self.hit_blindness = 0  
        self.size = 12.0

    def move(self, dx, dy, maze, tile):
        spd = self.speed
        if self.slow_timer > 0:
            spd *= 0.5
            self.slow_timer -= 1
        if self.speed_boost > 0:
            spd *= 1.5
            self.speed_boost -= 1

        move_x = dx * spd
        move_y = dy * spd
        s = self.size

        def passable(px, py):
            corners = [(px-s+2, py-s+2), (px+s-2, py-s+2),
                       (px-s+2, py+s-2), (px+s-2, py+s-2)]
            for cx, cy in corners:
                col_t = int(cx // tile)
                row_t = int(cy // tile)
                if row_t < 0 or row_t >= len(maze) or col_t < 0 or col_t >= len(maze[0]):
                    return False
                if maze[row_t][col_t] == 1:
                    return False
            return True

        new_x = self.x + move_x
        new_y = self.y + move_y

        if passable(new_x, self.y): self.x = new_x
        if passable(self.x, new_y): self.y = new_y

        if self.invincible > 0: self.invincible -= 1
        if self.hit_blindness > 0: self.hit_blindness -= 1

    def take_damage(self):
        if self.invincible == 0:
            self.hp -= 1
            self.invincible = 90
            self.hit_blindness = 60
            return True
        return False

    def draw(self, surface, ox, oy):
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return
        draw_shape(surface, self.shape, self.color, self.x - ox, self.y - oy, self.size)

# ─────────────────────────────────────────
# 몬스터 클래스
# ─────────────────────────────────────────
class Monster:
    def __init__(self, x, y, shape="동그라미", speed=1.5, is_chaser=False):
        self.x, self.y = float(x), float(y)
        self.shape = shape
        self.speed = speed
        self.is_chaser = is_chaser
        self.alive = True
        self.size = 12
        self.stun = 0
        self.path = []
        self.path_timer = 0

    def _bfs(self, maze, tile, tx, ty):
        sc = int(self.x // tile)
        sr = int(self.y // tile)
        tc = int(tx // tile)
        tr = int(ty // tile)
        sc = max(0, min(len(maze[0])-1, sc))
        sr = max(0, min(len(maze)-1, sr))
        tc = max(0, min(len(maze[0])-1, tc))
        tr = max(0, min(len(maze)-1, tr))
        if maze[sr][sc] == 1: return []
        visited = {(sr, sc)}
        q = deque([(sr, sc, [])])
        while q:
            r, c, path = q.popleft()
            if (r, c) == (tr, tc): return path
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] == 0 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc, path + [(nr, nc)]))
        return []

    def update(self, maze, tile, px, py):
        if not self.alive: return
        if self.stun > 0:
            self.stun -= 1
            return
        self.path_timer -= 1
        if self.path_timer <= 0:
            self.path = self._bfs(maze, tile, px, py)
            self.path_timer = 30 if self.is_chaser else 60
        if self.path:
            tr, tc = self.path[0]
            tx = tc * tile + tile // 2
            ty = tr * tile + tile // 2
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed + 1:
                if len(self.path) > 0: self.path.pop(0)
            else:
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed

    def draw(self, surface, ox, oy):
        if not self.alive: return
        color = (155, 89, 182) if self.is_chaser else (231, 76, 60)
        draw_shape(surface, self.shape, color, self.x - ox, self.y - oy, self.size)

# ─────────────────────────────────────────
# 아이템 / 함정 클래스
# ─────────────────────────────────────────
ITEM_TYPES = ["적처치", "속도증가", "시야확대", "적일시정지", "체력회복"]
TRAP_TYPES = ["이동감소", "생명-1", "시야제한", "랜덤이동"]

class MapObject:
    def __init__(self, x, y, kind, is_trap=False):
        self.x, self.y = x, y
        self.kind = kind
        self.is_trap = is_trap
        self.alive = True
        self.size = 11
        self.pulse = random.randint(0, 100)

    def draw(self, surface, ox, oy):
        if not self.alive: return
        self.pulse += 0.05
        pulse_r = self.size + math.sin(self.pulse) * 2
        tx, ty = self.x - ox, self.y - oy

        if self.is_trap:
            pygame.draw.circle(surface, COLORS["함정_원"], (int(tx), int(ty)), int(pulse_r), 2)
            draw_shape(surface, "세모", (50, 20, 20), tx, ty, pulse_r - 3)
        else:
            pygame.draw.circle(surface, COLORS["아이템_원"], (int(tx), int(ty)), int(pulse_r), 1)
            if self.kind == "체력회복":
                draw_shape(surface, "하트", (255, 100, 150), tx, ty, pulse_r - 2)
            else:
                draw_shape(surface, "다이아", (241, 196, 15), tx, ty, pulse_r - 2)

# ─────────────────────────────────────────
# 인게임 게임 씬 (GameScene)
# ─────────────────────────────────────────
class GameScene:
    TILE = 26 

    def __init__(self, difficulty, stage, shape, color, controller):
        self.ctrl = controller
        self.difficulty = difficulty
        self.stage = stage
        self.shape = shape
        self.color = color
        self.cfg = DIFFICULTY[difficulty]
        
        self.COLS = self.cfg["cols"] + (stage - 1) * 4
        self.ROWS = self.cfg["rows"] + (stage - 1) * 4
        
        self.maze = generate_maze(self.COLS, self.ROWS)
        self.exit_col = self.COLS - 2
        self.exit_row = self.ROWS - 2
        self.map_w = self.COLS * self.TILE
        self.map_h = self.ROWS * self.TILE

        sx = 1 * self.TILE + self.TILE // 2
        sy = 1 * self.TILE + self.TILE // 2
        self.player = Player(sx, sy, shape, color)

        # 몬스터 생성 수 수정: 난이도별 설정값 그대로 고정 (이지: 1, 보통: 2, 하드: 3)
        self.monsters = self._spawn_monsters(self.cfg["monsters"])
        self.objects = []
        self._place_items_traps()

        self.need_key = stage >= 2 
        self.key_pos = self._random_floor_pos(exclude_start=True)
        self.time_left = self.cfg["time"]
        self.frame_count = 0
        self.ox = 0
        self.oy = 0
        self.msg = ""
        self.msg_timer = 0
        self.base_vision = 120
        self.result = None
        self.flash_timer = 0
        self.shake_intensity = 0

    def _random_floor_pos(self, exclude_start=False):
        while True:
            r = random.randint(1, self.ROWS-2)
            c = random.randint(1, self.COLS-2)
            if self.maze[r][c] == 0:
                if exclude_start and r <= 4 and c <= 4: continue
                return (c * self.TILE + self.TILE//2, r * self.TILE + self.TILE//2)

    def _spawn_monsters(self, count):
        monsters = []
        m_speed = self.cfg["monster_speed"]
        for i in range(count):
            x, y = self._random_floor_pos(exclude_start=True)
            is_chaser = (i % 3 == 0) and (self.difficulty != "Easy") # 이지는 추격 형태 비활성화
            m = Monster(x, y, "동그라미" if not is_chaser else "육각형", speed=m_speed, is_chaser=is_chaser)
            monsters.append(m)
        return monsters

    def _place_items_traps(self):
        trap_r = self.cfg["trap_rate"]
        item_r = self.cfg["item_rate"]
        for r in range(1, self.ROWS-1):
            for c in range(1, self.COLS-1):
                if self.maze[r][c] == 0 and not (r <= 3 and c <= 3):
                    x = c * self.TILE + self.TILE//2
                    y = r * self.TILE + self.TILE//2
                    roll = random.random()
                    if roll < trap_r:
                        self.objects.append(MapObject(x, y, random.choice(TRAP_TYPES), is_trap=True))
                    elif roll < trap_r + item_r:
                        self.objects.append(MapObject(x, y, random.choice(ITEM_TYPES), is_trap=False))
        
        for _ in range(3):
            x, y = self._random_floor_pos(exclude_start=True)
            self.objects.append(MapObject(x, y, "체력회복", is_trap=False))

    def _camera(self):
        PLAY_ZONE_W = WIDTH - 160
        hx = PLAY_ZONE_W // 2
        hy = 45 + (HEIGHT - 45) // 2
        
        self.ox = int(self.player.x - hx)
        self.oy = int(self.player.y - hy)
        
        self.ox = max(0, min(self.ox, self.map_w - PLAY_ZONE_W))
        self.oy = max(-45, min(self.oy, self.map_h - (HEIGHT - 45)))
        
        if self.shake_intensity > 0:
            self.ox += random.randint(-self.shake_intensity, self.shake_intensity)
            self.oy += random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity -= 1

    def _check_collisions(self):
        p = self.player
        pr = p.size
        
        for obj in self.objects:
            if not obj.alive: continue
            if abs(p.x - obj.x) < pr + obj.size and abs(p.y - obj.y) < pr + obj.size:
                obj.alive = False
                if obj.is_trap:
                    if obj.kind == "생명-1":
                        if p.take_damage():
                            self.flash_timer = 12
                            self.shake_intensity = 15
                            self._show_msg("💔 치명적 함정! 생명 -1")
                    else:
                        self.shake_intensity = 8
                        if obj.kind == "이동감소":
                            p.slow_timer = 150
                            self._show_msg("🐢 점성 늪! 이동속도 저하")
                        elif obj.kind == "시야제한":
                            p.vision_expand = -70
                            self._show_msg("🌑 암흑 가스! 시야 축소")
                        elif obj.kind == "랜덤이동":
                            p.x, p.y = self._random_floor_pos()
                            self._show_msg("🌀 공간 왜곡! 무작위 텔레포트")
                else:
                    if obj.kind == "체력회복":
                        p.hp = min(3, p.hp + 1)
                        self._show_msg("❤️ 메디킷 회복 완료")
                    elif obj.kind == "적처치":
                        for m in self.monsters: m.alive = False
                        self._show_msg("⚡ EMP 폭발! 모든 적 소멸")
                    elif obj.kind == "속도증가":
                        p.speed_boost = 200
                        self._show_msg("💨 과부하 주입! 이동속도 증가")
                    elif obj.kind == "시야확대":
                        p.vision_expand = 130
                        self._show_msg("👁 서치라이트 가동! 시야 전개")
                    elif obj.kind == "적일시정지":
                        for m in self.monsters: m.stun = 180
                        self._show_msg("⏸ 시공간 정지! 적 행동 불능")

        if self.need_key and not p.has_key:
            kx, ky = self.key_pos
            if abs(p.x - kx) < pr + 14 and abs(p.y - ky) < pr + 14:
                p.has_key = True
                self._show_msg("🔑 데이터 열쇠 확보! 출구 봉쇄 해제")

        ex = self.exit_col * self.TILE + self.TILE//2
        ey = self.exit_row * self.TILE + self.TILE//2
        if abs(p.x - ex) < pr + 16 and abs(p.y - ey) < pr + 16:
            if not self.need_key or p.has_key:
                self.result = "WIN"

        for m in self.monsters:
            if not m.alive: continue
            if abs(p.x - m.x) < pr + m.size and abs(p.y - m.y) < pr + m.size:
                if p.take_damage():
                    self.flash_timer = 15
                    self.shake_intensity = 22
                    self._show_msg("💥 크리티컬 히트! 몬스터 충돌")

        if p.hp <= 0: self.result = "LOSE"

    def _show_msg(self, text):
        self.msg = text
        self.msg_timer = 100

    def update(self, keys):
        if self.result: return
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        if dx != 0 and dy != 0: dx *= 0.707; dy *= 0.707

        self.player.move(dx, dy, self.maze, self.TILE)
        for m in self.monsters:
            m.update(self.maze, self.TILE, self.player.x, self.player.y)

        self.frame_count += 1
        if self.frame_count % 60 == 0:
            self.time_left -= 1
            if self.time_left <= 0: self.result = "LOSE"

        self._check_collisions()
        self._camera()
        if self.msg_timer > 0: self.msg_timer -= 1
        if self.flash_timer > 0: self.flash_timer -= 1

    def draw(self, surface):
        surface.fill(COLORS["바닥"])
        T = self.TILE
        ox, oy = self.ox, self.oy
        PLAY_ZONE_W = WIDTH - 160

        for r in range(self.ROWS):
            for c in range(self.COLS):
                rx, ry = c * T - ox, r * T - oy
                if -T < rx < PLAY_ZONE_W and 45 - T < ry < HEIGHT:
                    if self.maze[r][c] == 1:
                        pygame.draw.rect(surface, COLORS["벽"], (rx, ry, T, T))
                        pygame.draw.rect(surface, (40, 50, 65), (rx, ry, T, T), 1)

        ex, ey = self.exit_col * T - ox, self.exit_row * T - oy
        if -T < ex < PLAY_ZONE_W and 45 - T < ey < HEIGHT:
            pygame.draw.rect(surface, COLORS["출구"], (ex, ey, T, T))
            label = "EXIT" if (not self.need_key or self.player.has_key) else "🔒"
            s = FONT_TINY.render(label, True, COLORS["블랙"])
            surface.blit(s, s.get_rect(center=(ex+T//2, ey+T//2)))

        if self.need_key and not self.player.has_key:
            kx, ky = self.key_pos
            if -T < kx - ox < PLAY_ZONE_W and 45 - T < ky - oy < HEIGHT:
                draw_shape(surface, "다이아", COLORS["열쇠"], kx - ox, ky - oy, 11)

        for obj in self.objects:
            if -T < obj.x - ox < PLAY_ZONE_W and 45 - T < obj.y - oy < HEIGHT:
                obj.draw(surface, ox, oy)

        for m in self.monsters:
            if -T < m.x - ox < PLAY_ZONE_W and 45 - T < m.y - oy < HEIGHT:
                m.draw(surface, ox, oy)
                
        if 45 - self.player.size < self.player.y - oy < HEIGHT:
            self.player.draw(surface, ox, oy)

        # 전장 안개
        vision = self.base_vision
        if self.player.vision_expand > 0:
            vision += 70
            self.player.vision_expand -= 1
        elif self.player.vision_expand < 0:
            vision -= 50
            self.player.vision_expand += 1
        
        if self.player.hit_blindness > 0:
            vision = max(15, vision * 0.15)

        if self.difficulty == "Easy":
            vision = int(vision * 2.5)

        px_screen, py_screen = self.player.x - ox, self.player.y - oy
        
        fog = pygame.Surface((PLAY_ZONE_W, HEIGHT - 45), pygame.SRCALPHA)
        fog_alpha = 50 if self.difficulty == "Easy" else 100
        fog.fill((10, 15, 25, fog_alpha)) 
        
        pygame.draw.circle(fog, (0, 0, 0, 0), (int(px_screen), int(py_screen - 45)), int(vision))
        surface.blit(fog, (0, 45))

        if self.flash_timer > 0:
            flash = pygame.Surface((PLAY_ZONE_W, HEIGHT - 45), pygame.SRCALPHA)
            flash.fill((231, 76, 60, 110))
            surface.blit(flash, (0, 45))

        # 상단 HUD 바 (무조건 맨 위에 덮어 씌우기)
        pygame.draw.rect(surface, COLORS["HUD_BG"], (0, 0, PLAY_ZONE_W, 45))
        pygame.draw.line(surface, COLORS["그레이"], (0, 45), (PLAY_ZONE_W, 45), 2)
        for i in range(3):
            col = COLORS["빨강"] if i < self.player.hp else (40, 40, 45)
            pygame.draw.circle(surface, col, (30 + i*30, 22), 10)
            pygame.draw.circle(surface, COLORS["화이트"], (30 + i*30, 22), 10, 1)

        t_color = COLORS["빨강"] if self.time_left <= 25 else COLORS["화이트"]
        t_surf = FONT_MID.render(f"⏱ {self.time_left}s", True, t_color)
        surface.blit(t_surf, t_surf.get_rect(center=(PLAY_ZONE_W//2, 22)))

        info = FONT_SMALL.render(f"ST {self.stage} | {self.cfg['label']}", True, COLORS["연그레이"])
        surface.blit(info, info.get_rect(midright=(PLAY_ZONE_W - 15, 22)))

        # 우측 고정 설명 패널
        panel_x = WIDTH - 160
        pygame.draw.rect(surface, COLORS["패널"], (panel_x, 0, 160, HEIGHT))
        pygame.draw.line(surface, COLORS["연그레이"], (panel_x, 0), (panel_x, HEIGHT), 2)
        
        surface.blit(FONT_SMALL.render("레이더 정보 고지", True, COLORS["노랑"]), (panel_x + 12, 68))

        pygame.draw.circle(surface, COLORS["아이템_원"], (panel_x + 20, 105), 7, 1)
        draw_shape(surface, "하트", (255, 100, 150), panel_x + 20, 105, 5)
        surface.blit(FONT_TINY.render("체력 회복", True, COLORS["화이트"]), (panel_x + 36, 98))

        pygame.draw.circle(surface, COLORS["아이템_원"], (panel_x + 20, 130), 7, 1)
        draw_shape(surface, "다이아", (241, 196, 15), panel_x + 20, 130, 5)
        surface.blit(FONT_TINY.render("스페셜 이펙트", True, COLORS["화이트"]), (panel_x + 36, 123))

        pygame.draw.circle(surface, COLORS["함정_원"], (panel_x + 20, 175), 7, 2)
        draw_shape(surface, "세모", (50, 20, 20), panel_x + 20, 175, 4)
        surface.blit(FONT_TINY.render("생명 차감 위험", True, COLORS["연그레이"]), (panel_x + 36, 168))

        pygame.draw.circle(surface, COLORS["함정_원"], (panel_x + 20, 200), 7, 2)
        draw_shape(surface, "세모", (50, 20, 20), panel_x + 20, 200, 4)
        surface.blit(FONT_TINY.render("디버프/워프", True, COLORS["연그레이"]), (panel_x + 36, 193))

        if self.need_key:
            draw_shape(surface, "다이아", COLORS["열쇠"], panel_x + 20, 245, 7)
            surface.blit(FONT_TINY.render("데이터 키(필수)", True, COLORS["열쇠"]), (panel_x + 36, 238))

        if self.msg_timer > 0:
            ms = FONT_MID.render(self.msg, True, COLORS["노랑"])
            msg_rect = ms.get_rect(center=(PLAY_ZONE_W//2, HEIGHT//2 - 100))
            pygame.draw.rect(surface, (10,10,20,180), msg_rect.inflate(20, 10), border_radius=6)
            surface.blit(ms, msg_rect)

        if self.result:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((10, 10, 15, 210))
            surface.blit(ov, (0, 0))
            msg = "🎉 미로 탈출 성공!" if self.result == "WIN" else "💀 차단 및 작전 실패"
            col = COLORS["출구"] if self.result == "WIN" else COLORS["빨강"]
            rs = FONT_BIG.render(msg, True, col)
            surface.blit(rs, rs.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            hint = FONT_MID.render("[ 아무 키나 누르면 정산 화면으로 ]", True, COLORS["화이트"])
            surface.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

# ─────────────────────────────────────────
# 통합 게임 매니저 컨트롤러 (GameController)
# ─────────────────────────────────────────
class GameController:
    def __init__(self):
        self.state = "START"
        self.character_color = COLORS["민트"]
        self.character_shape = "네모"
        self.selected_difficulty = "Normal"
        self.selected_stage = 1
        self.scene = None
        self.result_data = {}
        self.save_data = load_game_data()
        self._build_buttons()

    def _set(self, s):
        self.state = s
        self._build_buttons()

    def _start_game(self):
        self.scene = GameScene(self.selected_difficulty, self.selected_stage, self.character_shape, self.character_color, self)
        self.state = "PLAY"

    def _build_buttons(self):
        self.buttons = {
            "START": [
                Button(240, 280, 220, 55, "미로 진입 하기", (46, 204, 113), COLORS["화이트"], lambda: self._set("DIFFICULTY")),
                Button(240, 360, 220, 55, "플레이어 외형 변경", (52, 152, 219), COLORS["화이트"], lambda: self._set("CUSTOM")),
            ],
            "CUSTOM": [
                *[Button(60 + (i%5)*120, 240 + (i//5)*60, 100, 45, sh, (70, 75, 90), COLORS["화이트"], 
                         (lambda s: lambda: setattr(self, 'character_shape', s))(sh)) for i, sh in enumerate(SHAPES)],
                Button(250, 580, 200, 50, "외형 설정 후 복귀", COLORS["연그레이"], COLORS["블랙"], lambda: self._set("START"))
            ],
            "DIFFICULTY": [
                Button(240, 210, 220, 55, "Easy (쉬움)", (39, 174, 96), COLORS["화이트"], lambda: (setattr(self,'selected_difficulty','Easy'), self._set("STAGE"))),
                Button(240, 290, 220, 55, "Normal (보통)", (241, 196, 15), COLORS["블랙"], lambda: (setattr(self,'selected_difficulty','Normal'), self._set("STAGE"))),
                Button(240, 370, 220, 55, "Hard (어려움)", (192, 41, 43), COLORS["화이트"], lambda: (setattr(self,'selected_difficulty','Hard'), self._set("STAGE"))),
                Button(240, 480, 220, 48, "이전 화면으로", COLORS["연그레이"], COLORS["블랙"], lambda: self._set("START")),
            ],
            "STAGE": [
                *[Button(80 + i*110, 280, 90, 80, f"ST {i+1}", (41, 128, 185), COLORS["화이트"], 
                         (lambda n: lambda: (setattr(self,'selected_stage',n), self._start_game()))(i+1), 
                         enabled=self.save_data["unlocked"].get(f"{self.selected_difficulty}_{i+1}", False)) for i in range(5)],
                Button(240, 450, 220, 48, "난이도 재선택", COLORS["연그레이"], COLORS["블랙"], lambda: self._set("DIFFICULTY")),
            ],
            "RESULT": []
        }

        if self.state == "RESULT":
            st_str = str(self.result_data.get("stage", 1))
            is_win = self.result_data.get("result") == "WIN"
            if is_win and self.result_data.get("stage", 1) < 5:
                self.buttons["RESULT"].append(
                    Button(130, 480, 200, 55, "다음 스테이지 넥스트", (46, 204, 113), COLORS["화이트"], self._next_stage_go)
                )
                self.buttons["RESULT"].append(
                    Button(370, 480, 200, 55, "메인 타이틀 이동", COLORS["연그레이"], COLORS["블랙"], lambda: self._set("START"))
                )
            else:
                self.buttons["RESULT"].append(
                    Button(250, 480, 200, 55, "메인 타이틀 이동", COLORS["연그레이"], COLORS["블랙"], lambda: self._set("START"))
                )

    def _next_stage_go(self):
        self.selected_stage = min(5, self.result_data.get("stage", 1) + 1)
        self._start_game()

    def handle_event(self, event):
        if self.state == "PLAY" and self.scene and self.scene.result:
            if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                res = self.scene.result
                st = self.scene.stage
                diff = self.selected_difficulty
                taken = self.scene.cfg["time"] - self.scene.time_left
                
                self.result_data = {"result": res, "stage": st, "diff": diff, "time": taken}
                
                current_key = f"{diff}_{st}"
                if res == "WIN":
                    next_key = f"{diff}_{st + 1}"
                    if next_key in self.save_data["unlocked"]:
                        self.save_data["unlocked"][next_key] = True
                    
                    cur_b = self.save_data["best_time"].get(current_key)
                    if cur_b is None or taken < cur_b:
                        self.save_data["best_time"][current_key] = taken
                    save_game_data(self.save_data)
                
                self._set("RESULT")
                return

        for btn in self.buttons.get(self.state, []):
            btn.handle_event(event)

    def update(self):
        if self.state == "PLAY" and self.scene:
            keys = pygame.key.get_pressed()
            self.scene.update(keys)

    def draw(self, surface):
        if self.state == "PLAY" and self.scene:
            self.scene.draw(surface)
            return

        surface.fill(COLORS["HUD_BG"])
        
        if self.state == "START":
            txt = FONT_BIG.render("도망쳐! 네모 미로", True, COLORS["노랑"])
            surface.blit(txt, txt.get_rect(center=(WIDTH//2, 140)))
            sub = FONT_SMALL.render(f"현재 선택된 세팅 외형: [{self.character_shape}]", True, COLORS["연그레이"])
            surface.blit(sub, sub.get_rect(center=(WIDTH//2, 210)))
            
        elif self.state == "CUSTOM":
            txt = FONT_MID.render("플레이어 외형 변경 커스터마이징", True, COLORS["파랑"])
            surface.blit(txt, txt.get_rect(center=(WIDTH//2, 80)))
            draw_shape(surface, self.character_shape, self.character_color, WIDTH//2, 160, 25)
            
        elif self.state == "DIFFICULTY":
            txt = FONT_BIG.render("작전 난이도 선택", True, COLORS["화이트"])
            surface.blit(txt, txt.get_rect(center=(WIDTH//2, 120)))
            
        elif self.state == "STAGE":
            txt = FONT_BIG.render(f"진입 구역 섹터 해금 ({self.selected_difficulty})", True, COLORS["민트"])
            surface.blit(txt, txt.get_rect(center=(WIDTH//2, 140)))
            
        elif self.state == "RESULT":
            is_win = self.result_data.get("result") == "WIN"
            title_txt = "🎉 구역 돌파 및 탈출 성공!" if is_win else "💀 신호 차단 - 작전 실패"
            title_col = COLORS["출구"] if is_win else COLORS["빨강"]
            
            surface.blit(FONT_BIG.render(title_txt, True, title_col), (110, 110))
            
            st_text = f"진입 섹터: 스테이지 {self.result_data.get('stage')}"
            df_text = f"설정 난이도: {self.result_data.get('diff')}"
            tm_text = f"소요 시간: {self.result_data.get('time')} 초" if is_win else "기록 합산 불가"
            
            current_key = f"{self.result_data.get('diff')}_{self.result_data.get('stage')}"
            best_rec = self.save_data["best_time"].get(current_key)
            bs_text = f"이 난이도 최고 기록: {best_rec} 초" if best_rec else "최고 기록: 없음"
            
            surface.blit(FONT_MID.render(st_text, True, COLORS["화이트"]), (180, 230))
            surface.blit(FONT_MID.render(df_text, True, COLORS["화이트"]), (180, 275))
            surface.blit(FONT_MID.render(tm_text, True, COLORS["노랑"]), (180, 320))
            surface.blit(FONT_SMALL.render(bs_text, True, COLORS["민트"]), (180, 380))

        for btn in self.buttons.get(self.state, []):
            btn.draw(surface)

# ─────────────────────────────────────────
# 메인 루프 실행부
# ─────────────────────────────────────────
controller = GameController()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        controller.handle_event(event)

    controller.update()
    controller.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
