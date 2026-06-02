import sys

print("python =", sys.executable)

try:
    import pygame
    print("pygame OK", pygame.version.ver)
except Exception as e:
    print("pygame ERROR:", e)

import pygame
import sys
import random
import math
from collections import deque

pygame.init()
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("도망쳐! 네모 - 미로 탈출")
clock = pygame.time.Clock()

# ─────────────────────────────────────────
# 색상 / 폰트
# ─────────────────────────────────────────
COLORS = {
    "빨강": (220, 50, 50), "주황": (255, 165, 0), "노랑": (255, 220, 0),
    "초록": (34, 160, 34), "파랑": (30, 80, 220), "남색": (0, 0, 128),
    "보라": (128, 0, 180), "핑크": (255, 100, 180), "민트": (62, 180, 137),
    "차콜": (54, 69, 79), "화이트": (255, 255, 255), "블랙": (10, 10, 10),
    "그레이": (150, 150, 150), "연그레이": (220, 220, 220),
    "배경": (245, 245, 240), "벽": (60, 60, 80), "바닥": (200, 195, 185),
    "출구": (80, 220, 120), "아이템": (255, 200, 0), "함정": (220, 80, 80),
    "열쇠": (255, 215, 0), "HUD_BG": (30, 30, 45),
}

#윈도우
# try:
#     FONT_BIG   = pygame.font.SysFont("AppleGothic", 42, bold=True)
#     FONT_MID   = pygame.font.SysFont("AppleGothic", 22, bold=True)
#     FONT_SMALL = pygame.font.SysFont("AppleGothic", 15)
#     FONT_TINY  = pygame.font.SysFont("AppleGothic", 13)

#맥북
try:
    FONT_BIG   = pygame.font.SysFont("AppleGothic", 42, bold=True)
    FONT_MID   = pygame.font.SysFont("AppleGothic", 22, bold=True)
    FONT_SMALL = pygame.font.SysFont("AppleGothic", 15)
    FONT_TINY  = pygame.font.SysFont("AppleGothic", 13)

except:
    FONT_BIG   = pygame.font.Font(None, 54)
    FONT_MID   = pygame.font.Font(None, 30)
    FONT_SMALL = pygame.font.Font(None, 22)
    FONT_TINY  = pygame.font.Font(None, 18)

SHAPES = ["네모", "동그라미", "세모", "역세모", "다이아", "오각형", "하트", "별", "육각형", "십자가"]

# ─────────────────────────────────────────
# 난이도 설정 (섹션 7)
# ─────────────────────────────────────────
DIFFICULTY = {
    "Easy":   {"monsters": 3,  "time": 120, "trap_rate": 0.04, "item_rate": 0.06, "label": "쉬움"},
    "Normal": {"monsters": 6,  "time": 180, "trap_rate": 0.06, "item_rate": 0.05, "label": "보통"},
    "Hard":   {"monsters": 99, "time": 300, "trap_rate": 0.08, "item_rate": 0.04, "label": "어려움"},
}

# ─────────────────────────────────────────
# 도형 그리기
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
        pts = [(cx, cy-r), (cx+int(0.25*r), cy-int(0.25*r)),
               (cx+r, cy-int(0.25*r)), (cx+int(0.4*r), cy+int(0.15*r)),
               (cx+int(0.6*r), cy+r), (cx, cy+int(0.4*r)),
               (cx-int(0.6*r), cy+r), (cx-int(0.4*r), cy+int(0.15*r)),
               (cx-r, cy-int(0.25*r)), (cx-int(0.25*r), cy-int(0.25*r))]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, outline, pts, 2)
    elif shape == "육각형":
        pts = [(cx, cy-r), (cx+int(r*0.87), cy-r//2),
               (cx+int(r*0.87), cy+r//2), (cx, cy+r),
               (cx-int(r*0.87), cy+r//2), (cx-int(r*0.87), cy-r//2)]
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
    def __init__(self, x, y, w, h, text, bg, fg, cb, border=2, radius=8):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.bg, self.fg, self.cb = text, bg, fg, cb
        self.border, self.radius = border, radius
        self.hovered = False

    def draw(self, surface):
        col = tuple(min(255, c+30) for c in self.bg) if self.hovered else self.bg
        pygame.draw.rect(surface, col, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, COLORS["블랙"], self.rect, self.border, border_radius=self.radius)
        s = FONT_MID.render(self.text, True, self.fg)
        surface.blit(s, s.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.cb()

# ─────────────────────────────────────────
# 미로 생성 (DFS)
# ─────────────────────────────────────────
def generate_maze(cols, rows):
    """1=벽, 0=통로. DFS recursive backtracker."""
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
    grid[rows-2][cols-2] = 0  # 출구 열기
    return grid

# ─────────────────────────────────────────
# 플레이어
# ─────────────────────────────────────────
class Player:
    BASE_SPEED = 3.5

    def __init__(self, x, y, shape, color):
        self.x, self.y = float(x), float(y)
        self.shape, self.color = shape, color
        self.hp = 3
        self.speed = self.BASE_SPEED
        self.has_key = False
        self.invincible = 0      # 무적 프레임
        self.slow_timer = 0
        self.vision_expand = 0
        self.speed_boost = 0
        self.size = 14

    def move(self, dx, dy, maze, tile):
        spd = self.speed
        if self.slow_timer > 0:
            spd *= 0.5
            self.slow_timer -= 1
        if self.speed_boost > 0:
            spd *= 1.6
            self.speed_boost -= 1

        nx = self.x + dx * spd
        ny = self.y + dy * spd
        s = self.size
        def passable(px, py):
            for corner in [(px-s, py-s), (px+s-1, py-s), (px-s, py+s-1), (px+s-1, py+s-1)]:
                col_t = int(corner[0] // tile)
                row_t = int(corner[1] // tile)
                if row_t < 0 or row_t >= len(maze) or col_t < 0 or col_t >= len(maze[0]):
                    return False
                if maze[row_t][col_t] == 1:
                    return False
            return True

        if passable(nx, self.y): self.x = nx
        if passable(self.x, ny): self.y = ny

        if self.invincible > 0: self.invincible -= 1

    def take_damage(self):
        if self.invincible == 0:
            self.hp -= 1
            self.invincible = 90
            return True
        return False

    def draw(self, surface, ox, oy):
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return
        draw_shape(surface, self.shape, self.color,
                   self.x - ox, self.y - oy, self.size)

# ─────────────────────────────────────────
# 몬스터 (섹션 3 AI)
# ─────────────────────────────────────────
class Monster:
    def __init__(self, x, y, shape="동그라미"):
        self.x, self.y = float(x), float(y)
        self.shape = shape
        self.speed = random.uniform(1.0, 1.8)
        self.hp = 1
        self.alive = True
        self.size = 12
        self.stun = 0        # 일시 정지 타이머
        self.path = []
        self.path_timer = 0

    def _bfs(self, maze, tile, tx, ty):
        sc = int(self.x // tile)
        sr = int(self.y // tile)

        sc = max(0, min(sc, len(maze[0]) - 1))
        sr = max(0, min(sr, len(maze) - 1))

        tc = int(tx // tile)
        tr = int(ty // tile)

        tc = max(0, min(tc, len(maze[0]) - 1))
        tr = max(0, min(tr, len(maze) - 1))

        if maze[sr][sc] == 1:
            return []

        visited = {(sr, sc)}
        q = deque([(sr, sc, [])])

    def _safe_random_pos(self):
        while True:
            x, y = self._random_floor_pos()

            safe = True
            for m in self.monsters:
                if not m.alive:
                    continue

                dist = math.hypot(x - m.x, y - m.y)

                if dist < 80:
                    safe = False
                    break

            if safe:
                return x, y

    def update(self, maze, tile, px, py):
        if not self.alive: return
        if self.stun > 0:
            self.stun -= 1
            return

        self.path_timer -= 1
        if self.path_timer <= 0:
            self.path = self._bfs(maze, tile, px, py)
            self.path_timer = 45

        if self.path:
            tr, tc = self.path[0]
            tx = tc * tile + tile // 2
            ty = tr * tile + tile // 2
            dx = tx - self.x; dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed + 1:
                self.path.pop(0)
            else:
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed

    def draw(self, surface, ox, oy):
        if not self.alive: return
        draw_shape(surface, self.shape, COLORS["빨강"],
                   self.x - ox, self.y - oy, self.size)
        # HP bar (always 1 hp, show as red dot indicator)

# ─────────────────────────────────────────
# 아이템 / 함정 (섹션 4)
# ─────────────────────────────────────────
ITEM_TYPES  = ["적처치", "속도증가", "시야확대", "적일시정지"]
TRAP_TYPES  = ["이동감소", "생명-1", "시야제한", "랜덤이동"]

class Item:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind = kind   # ITEM_TYPES 중 하나
        self.alive = True
        self.size = 9

class Trap:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind = kind   # TRAP_TYPES 중 하나
        self.alive = True
        self.size = 9

# ─────────────────────────────────────────
# 시야 (안개)
# ─────────────────────────────────────────
def make_fog(surface, cx, cy, radius):
    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog.fill((0, 0, 0, 210))
    pygame.draw.circle(fog, (0, 0, 0, 0), (int(cx), int(cy)), int(radius))
    surface.blit(fog, (0, 0))

# ─────────────────────────────────────────
# 게임 플레이 씬
# ─────────────────────────────────────────
class GameScene:
    TILE = 28
    COLS = 23
    ROWS = 23

    def __init__(self, difficulty, stage, shape, color, controller):
        self.ctrl = controller
        self.difficulty = difficulty
        self.stage = stage
        self.shape = shape
        self.color = color
        self.cfg = DIFFICULTY[difficulty]

        # 미로
        self.maze = generate_maze(self.COLS, self.ROWS)
        # 출구 위치
        self.exit_col = self.COLS - 2
        self.exit_row = self.ROWS - 2

        # 타일 크기에 맞춘 맵 픽셀 크기
        self.map_w = self.COLS * self.TILE
        self.map_h = self.ROWS * self.TILE

        # 플레이어 시작
        sx = 1 * self.TILE + self.TILE // 2
        sy = 1 * self.TILE + self.TILE // 2
        self.player = Player(sx, sy, shape, color)

        # 몬스터 생성
        cfg_monsters = self.cfg["monsters"]
        monster_count = cfg_monsters if cfg_monsters < 20 else random.randint(6, 10)
        self.monsters = self._spawn_monsters(monster_count)

        # 아이템 / 함정 배치
        self.items = []
        self.traps = []
        self._place_items_traps()

        # 열쇠 (스테이지 >= 3 이면 열쇠 필요)
        self.need_key = stage >= 3
        self.key_pos = self._random_floor_pos(exclude_start=True)

        # 타이머
        self.time_left = self.cfg["time"] + (stage - 1) * 30
        self.frame_count = 0

        # 카메라 오프셋
        self.ox = 0; self.oy = 0

        # HUD 메시지
        self.msg = ""
        self.msg_timer = 0

        # 시야 반경
        self.base_vision = 110

        self.result = None  # "WIN" or "LOSE"

    def _random_floor_pos(self, exclude_start=False):
        while True:
            r = random.randint(1, self.ROWS-2)
            c = random.randint(1, self.COLS-2)
            if self.maze[r][c] == 0:
                if exclude_start and r <= 3 and c <= 3:
                    continue
                return (c * self.TILE + self.TILE//2, r * self.TILE + self.TILE//2)

    def _spawn_monsters(self, count):
        monsters = []
        shapes = ["동그라미", "세모", "다이아", "별", "오각형"]
        for _ in range(count):
            x, y = self._random_floor_pos(exclude_start=True)
            m = Monster(x, y, random.choice(shapes))
            monsters.append(m)
        return monsters

    def _place_items_traps(self):
        trap_r = self.cfg["trap_rate"]
        item_r = self.cfg["item_rate"]
        for r in range(1, self.ROWS-1):
            for c in range(1, self.COLS-1):
                if self.maze[r][c] == 0 and not (r <= 2 and c <= 2):
                    x = c * self.TILE + self.TILE//2
                    y = r * self.TILE + self.TILE//2
                    roll = random.random()
                    if roll < trap_r:
                        self.traps.append(Trap(x, y, random.choice(TRAP_TYPES)))
                    elif roll < trap_r + item_r:
                        self.items.append(Item(x, y, random.choice(ITEM_TYPES)))

    def _camera(self):
        hx = WIDTH // 2;  hy = HEIGHT // 2
        self.ox = int(self.player.x - hx)
        self.oy = int(self.player.y - hy)
        self.ox = max(0, min(self.ox, self.map_w - WIDTH))
        self.oy = max(0, min(self.oy, self.map_h - HEIGHT))

    def _check_collisions(self):
        p = self.player
        pr = p.size

        # 함정
        for trap in self.traps:
            if not trap.alive: continue
            if abs(p.x - trap.x) < pr + trap.size and abs(p.y - trap.y) < pr + trap.size:
                trap.alive = False
                if trap.kind == "이동감소":
                    p.slow_timer = 180
                    self._show_msg("🐢 이동 속도 감소!")
                elif trap.kind == "생명-1":
                    if p.take_damage():
                        self._show_msg("💔 생명 -1!")
                elif trap.kind == "시야제한":
                    p.vision_expand -= 120
                    self._show_msg("🌑 시야 제한!")
                elif trap.kind == "랜덤이동":
                    p.x, p.y = self._random_floor_pos()
                    self._show_msg("🌀 랜덤 이동!")

        # 아이템
        for item in self.items:
            if not item.alive: continue
            if abs(p.x - item.x) < pr + item.size and abs(p.y - item.y) < pr + item.size:
                item.alive = False
                if item.kind == "적처치":
                    for m in self.monsters:
                        if m.alive:
                            m.alive = False
                    self._show_msg("⚡ 화면 내 모든 적 제거!")
                elif item.kind == "속도증가":
                    p.speed_boost = 240
                    self._show_msg("💨 속도 증가!")
                elif item.kind == "시야확대":
                    p.vision_expand += 120
                    self._show_msg("👁 시야 확대!")
                elif item.kind == "적일시정지":
                    for m in self.monsters:
                        m.stun = 180
                    self._show_msg("⏸ 적 일시 정지!")

        # 열쇠
        if self.need_key and not p.has_key:
            kx, ky = self.key_pos
            if abs(p.x - kx) < pr + 12 and abs(p.y - ky) < pr + 12:
                p.has_key = True
                self._show_msg("🔑 열쇠 획득!")

        # 출구
        ex = self.exit_col * self.TILE + self.TILE//2
        ey = self.exit_row * self.TILE + self.TILE//2
        if abs(p.x - ex) < pr + 16 and abs(p.y - ey) < pr + 16:
            if not self.need_key or p.has_key:
                self.result = "WIN"

        # 몬스터 충돌
        for m in self.monsters:
            if not m.alive: continue
            if abs(p.x - m.x) < pr + m.size and abs(p.y - m.y) < pr + m.size:
                if p.take_damage():
                    self._show_msg("💥 몬스터에게 피해!")

        # HP 소진
        if p.hp <= 0:
            self.result = "LOSE"

    def _show_msg(self, text):
        self.msg = text
        self.msg_timer = 120

    def update(self, keys):
        if self.result:
            return

        # 플레이어 이동
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  1
        if dx != 0 and dy != 0:
            dx *= 0.707; dy *= 0.707
        self.player.move(dx, dy, self.maze, self.TILE)

        # 몬스터 AI
        for m in self.monsters:
            m.update(self.maze, self.TILE, self.player.x, self.player.y)

        # 타이머
        self.frame_count += 1
        if self.frame_count % 60 == 0:
            self.time_left -= 1
            if self.time_left <= 0:
                self.result = "LOSE"

        # 충돌
        self._check_collisions()

        # 카메라
        self._camera()

        # 메시지 타이머
        if self.msg_timer > 0:
            self.msg_timer -= 1

    def draw(self, surface):
        surface.fill(COLORS["바닥"])
        T = self.TILE
        ox, oy = self.ox, self.oy

        # 미로 그리기
        for r in range(self.ROWS):
            for c in range(self.COLS):
                rx = c * T - ox
                ry = r * T - oy
                if rx > WIDTH or ry > HEIGHT or rx + T < 0 or ry + T < 0:
                    continue
                if self.maze[r][c] == 1:
                    pygame.draw.rect(surface, COLORS["벽"], (rx, ry, T, T))
                    pygame.draw.rect(surface, (40,40,55), (rx, ry, T, T), 1)
                else:
                    pygame.draw.rect(surface, COLORS["바닥"], (rx, ry, T, T))

        # 출구
        ex = self.exit_col * T - ox
        ey = self.exit_row * T - oy
        pygame.draw.rect(surface, COLORS["출구"], (ex, ey, T, T))
        s = FONT_TINY.render("출구" if (not self.need_key or self.player.has_key) else "🔒", True, COLORS["블랙"])
        surface.blit(s, (ex+2, ey+6))

        # 열쇠
        if self.need_key and not self.player.has_key:
            kx, ky = self.key_pos
            draw_shape(surface, "다이아", COLORS["열쇠"], kx - ox, ky - oy, 10)

        # 함정
        for trap in self.traps:
            if not trap.alive: continue
            tx = trap.x - ox; ty = trap.y - oy
            if -20 < tx < WIDTH+20 and -20 < ty < HEIGHT+20:
                draw_shape(surface, "별", COLORS["함정"], tx, ty, trap.size)

        # 아이템
        for item in self.items:
            if not item.alive: continue
            ix = item.x - ox; iy = item.y - oy
            if -20 < ix < WIDTH+20 and -20 < iy < HEIGHT+20:
                draw_shape(surface, "육각형", COLORS["아이템"], ix, iy, item.size)

        # 몬스터
        for m in self.monsters:
            m.draw(surface, ox, oy)

        # 플레이어
        self.player.draw(surface, ox, oy)

        # 안개 (시야)
        vision = self.base_vision
        if self.player.vision_expand > 0:
            vision += 60; self.player.vision_expand -= 1
        elif self.player.vision_expand < 0:
            vision -= 50; self.player.vision_expand += 1
        px_screen = self.player.x - ox
        py_screen = self.player.y - oy
        make_fog(surface, px_screen, py_screen, vision)

        # HUD 상단 바
        hud_h = 42
        pygame.draw.rect(surface, COLORS["HUD_BG"], (0, 0, WIDTH, hud_h))

        # HP
        for i in range(3):
            col = COLORS["빨강"] if i < self.player.hp else COLORS["그레이"]
            pygame.draw.circle(surface, col, (20 + i*28, 21), 10)
            pygame.draw.circle(surface, COLORS["블랙"], (20 + i*28, 21), 10, 2)

        # 타이머
        t_color = (255,80,80) if self.time_left <= 30 else COLORS["화이트"]
        t_surf = FONT_MID.render(f"⏱ {self.time_left}s", True, t_color)
        surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 21)))

        # 스테이지 / 난이도
        info = FONT_SMALL.render(f"스테이지 {self.stage}  |  {self.difficulty}", True, COLORS["연그레이"])
        surface.blit(info, info.get_rect(midright=(WIDTH-10, 21)))

        # 열쇠 상태
        if self.need_key:
            key_s = FONT_SMALL.render("🔑 획득" if self.player.has_key else "🔑 필요", True,
                                       COLORS["노랑"] if self.player.has_key else COLORS["그레이"])
            surface.blit(key_s, (100, 27))

        # 메시지
        if self.msg_timer > 0:
            alpha = min(255, self.msg_timer * 4)
            ms = FONT_MID.render(self.msg, True, COLORS["노랑"])
            mr = ms.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
            surface.blit(ms, mr)

        # 결과 오버레이
        if self.result:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            surface.blit(ov, (0, 0))
            if self.result == "WIN":
                msg = "🎉 탈출 성공!"
                col = COLORS["출구"]
            else:
                msg = "💀 게임 오버"
                col = COLORS["빨강"]
            rs = FONT_BIG.render(msg, True, col)
            surface.blit(rs, rs.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
            hint = FONT_MID.render("아무 키를 누르면 계속", True, COLORS["화이트"])
            surface.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))

# ─────────────────────────────────────────
# 메인 컨트롤러 (섹션 8 상태 전이도)
# ─────────────────────────────────────────
class GameController:
    STATES = ["START", "CUSTOM", "DIFFICULTY", "STAGE", "PLAY", "RESULT"]

    def __init__(self):
        self.state = "START"
        self.character_color = COLORS["빨강"]
        self.character_shape = "네모"
        self.selected_difficulty = "Normal"
        self.selected_stage = 1
        self.scene = None
        self.result_data = {}
        self._build_buttons()

    def _set(self, s):
        self.state = s

    def _start_game(self):
        self.scene = GameScene(
            self.selected_difficulty,
            self.selected_stage,
            self.character_shape,
            self.character_color,
            self
        )
        self._set("PLAY")

    def _build_buttons(self):
        B = Button
        LG = COLORS["연그레이"]; BK = COLORS["블랙"]; WH = COLORS["화이트"]

        self.buttons = {
            "START": [
                B(250, 270, 200, 55, "게임 시작", (80,160,80), WH, lambda: self._set("DIFFICULTY")),
                B(250, 345, 200, 55, "커스터마이징", (80,120,200), WH, lambda: self._set("CUSTOM")),
            ],
            "CUSTOM": [
                B(250, 610, 200, 48, "돌아가기", LG, BK, lambda: self._set("START")),
            ],
            "DIFFICULTY": [
                B(175, 260, 160, 60, "Easy",   (80,200,100), BK, lambda: (setattr(self,'selected_difficulty','Easy'),   self._set("STAGE"))),
                B(270, 260, 160, 60, "Normal", (255,200,60),  BK, lambda: (setattr(self,'selected_difficulty','Normal'), self._set("STAGE"))),
                B(365, 260, 160, 60, "Hard",   (220,60,60),   WH, lambda: (setattr(self,'selected_difficulty','Hard'),   self._set("STAGE"))),
                B(250, 380, 200, 48, "돌아가기", LG, BK, lambda: self._set("START")),
            ],
            "STAGE": [
                *[B(100 + i*100, 280, 80, 80, f"{i+1}", (100,140,220), WH,
                    (lambda n: lambda: (setattr(self,'selected_stage',n), self._start_game()))(i+1))
                  for i in range(5)],
                B(250, 400, 200, 48, "돌아가기", LG, BK, lambda: self._set("DIFFICULTY")),
            ],
            "PLAY": [],
            "RESULT": [
                B(180, 430, 160, 55, "다시 플레이", (80,160,80), WH, self._start_game),
                B(360, 430, 160, 55, "메인으로",    (80,80,180),  WH, lambda: self._set("START")),
            ],
        }

        # 커스텀 화면 - 색상 버튼
        color_list = [
            ("빨강",COLORS["빨강"]),("주황",COLORS["주황"]),("노랑",COLORS["노랑"]),
            ("초록",COLORS["초록"]),("파랑",COLORS["파랑"]),("남색",COLORS["남색"]),
            ("보라",COLORS["보라"]),("핑크",COLORS["핑크"]),("민트",COLORS["민트"]),
            ("차콜",COLORS["차콜"]),
        ]
        for i, (name, rgb) in enumerate(color_list):
            r, c = i//5, i%5
            x = 75 + c*110; y = 300 + r*50
            fg = WH if name in ["파랑","남색","보라","차콜"] else BK
            self.buttons["CUSTOM"].append(
                B(x, y, 95, 38, name, rgb, fg, (lambda col=rgb: setattr(self,'character_color',col))))

        # 커스텀 화면 - 모양 버튼
        for i, name in enumerate(SHAPES):
            r, c = i//5, i%5
            x = 75 + c*110; y = 420 + r*50
            self.buttons["CUSTOM"].append(
                B(x, y, 95, 38, name, WH, BK, (lambda n=name: setattr(self,'character_shape',n))))

    def handle_event(self, event):
        if self.state in self.buttons:
            for btn in self.buttons[self.state]:
                btn.handle_event(event)
        if self.state == "PLAY" and self.scene and self.scene.result:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # 결과 화면으로
                self.result_data = {
                    "result": self.scene.result,
                    "stage": self.scene.stage,
                    "diff": self.scene.difficulty,
                    "time": self.scene.cfg["time"] + (self.scene.stage-1)*30 - self.scene.time_left,
                }
                self._set("RESULT")

    def draw_start(self, surface):
        surface.fill((20, 24, 40))
        # 격자 배경
        for i in range(0, WIDTH, 40):
            pygame.draw.line(surface, (35,40,60), (i,0), (i,HEIGHT), 1)
        for j in range(0, HEIGHT, 40):
            pygame.draw.line(surface, (35,40,60), (0,j), (WIDTH,j), 1)

        title = FONT_BIG.render("🏃 도망쳐! 네모", True, (255,220,50))
        surface.blit(title, title.get_rect(center=(WIDTH//2, 140)))
        sub = FONT_MID.render("미로 탈출 어드벤처", True, (180,180,220))
        surface.blit(sub, sub.get_rect(center=(WIDTH//2, 200)))

        draw_shape(surface, self.character_shape, self.character_color, WIDTH//2, 220, 28)

    def draw_custom(self, surface):
        surface.fill((240, 242, 248))
        title = FONT_BIG.render("🎨 캐릭터 커스터마이징", True, COLORS["블랙"])
        surface.blit(title, title.get_rect(center=(WIDTH//2, 45)))

        # 미리보기
        pygame.draw.rect(surface, COLORS["화이트"], (295, 90, 110, 110), border_radius=8)
        pygame.draw.rect(surface, COLORS["그레이"],  (295, 90, 110, 110), 2, border_radius=8)
        draw_shape(surface, self.character_shape, self.character_color, 350, 145, 38)

        lbl_c = FONT_MID.render("색상 선택 (10종)", True, COLORS["블랙"])
        surface.blit(lbl_c, (75, 268))
        lbl_s = FONT_MID.render("모양 선택 (10종)", True, COLORS["블랙"])
        surface.blit(lbl_s, (75, 388))

    def draw_difficulty(self, surface):
        surface.fill((30, 35, 55))
        title = FONT_BIG.render("⚙ 난이도 선택", True, COLORS["노랑"])
        surface.blit(title, title.get_rect(center=(WIDTH//2, 140)))

        info = [
            ("Easy",   "몬스터 3마리 / 2분",   (80,200,100)),
            ("Normal", "무한 생성 / 3분",        (255,200,60)),
            ("Hard",   "무한 생성 / 5분 (함정↑)",(220,60,60)),
        ]
        for i, (lv, desc, col) in enumerate(info):
            ds = FONT_SMALL.render(desc, True, col)
            surface.blit(ds, ds.get_rect(center=(175 + i*95 + 80, 335)))

    def draw_stage(self, surface):
        surface.fill((25, 30, 50))
        title = FONT_BIG.render("🗺 스테이지 선택", True, COLORS["민트"])
        surface.blit(title, title.get_rect(center=(WIDTH//2, 160)))
        diff_s = FONT_MID.render(f"난이도: {self.selected_difficulty}", True, COLORS["연그레이"])
        surface.blit(diff_s, diff_s.get_rect(center=(WIDTH//2, 225)))

    def draw_result(self, surface):
        surface.fill((15, 15, 25))
        rd = self.result_data
        if rd.get("result") == "WIN":
            r_text = "🎉 탈출 성공!"
            r_col = COLORS["출구"]
        else:
            r_text = "💀 게임 오버"
            r_col = COLORS["빨강"]

        rs = FONT_BIG.render(r_text, True, r_col)
        surface.blit(rs, rs.get_rect(center=(WIDTH//2, 180)))

        details = [
            f"스테이지: {rd.get('stage', '-')}",
            f"난이도: {rd.get('diff', '-')}",
            f"플레이 시간: {rd.get('time', 0)}초",
        ]
        for i, d in enumerate(details):
            ds = FONT_MID.render(d, True, COLORS["화이트"])
            surface.blit(ds, ds.get_rect(center=(WIDTH//2, 280 + i*40)))

    def update_and_draw(self, surface, keys):
        if self.state == "START":
            self.draw_start(surface)
        elif self.state == "CUSTOM":
            self.draw_custom(surface)
        elif self.state == "DIFFICULTY":
            self.draw_difficulty(surface)
        elif self.state == "STAGE":
            self.draw_stage(surface)
        elif self.state == "PLAY":
            if self.scene:
                self.scene.update(keys)
                self.scene.draw(surface)
            return  # no extra buttons
        elif self.state == "RESULT":
            self.draw_result(surface)

        for btn in self.buttons.get(self.state, []):
            btn.draw(surface)

# ─────────────────────────────────────────
# 메인 루프
# ─────────────────────────────────────────
def main():
    ctrl = GameController()
    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ctrl.handle_event(event)

        ctrl.update_and_draw(screen, keys)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
