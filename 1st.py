import pygame, random, sys, math
from collections import deque

pygame.init()

# 다이어그램과 오른쪽 UI 패널 공간 확보를 위해 가로폭을 1000으로 설정
WIDTH, HEIGHT = 1000, 800
CELL = 24
MAZE_SIZE = 25 

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("미로 탈출 게임 시스템")
clock = pygame.time.Clock()

# 시스템 컬러 테이블
COLORS = {
    "빨강": (255, 0, 0), "주황": (255, 165, 0), "노랑": (255, 255, 0), 
    "초록": (0, 128, 0), "파랑": (0, 0, 255), "남색": (0, 0, 128), 
    "보라": (128, 0, 128), "핑크": (255, 192, 203), "민트": (62, 180, 137), 
    "차콜": (54, 69, 79), "화이트": (255, 255, 255), "블랙": (0, 0, 0),
    "그레이": (128, 128, 128), "연그레이": (211, 211, 211), "골드": (255, 215, 0),
    "자주": (162, 21, 21),
    "진한초록": (0, 100, 0),
    "진한파랑": (0, 0, 139),
    "진한빨강": (139, 0, 0)
}

SHAPES = ["네모", "동그라미", "세모", "역세모", "다이아", "오각형", "하트", "별", "육각형", "십자가"]

try:
    FONT_BIG = pygame.font.SysFont("malgungothic", 36, bold=True)
    FONT_MID = pygame.font.SysFont("malgungothic", 20, bold=True)
    FONT_SMALL = pygame.font.SysFont("malgungothic", 14, bold=True)
except:
    FONT_BIG = pygame.font.Font(None, 48)
    FONT_MID = pygame.font.Font(None, 28)
    FONT_SMALL = pygame.font.Font(None, 20)

class Button:
    def __init__(self, x, y, w, h, text, bg_color, text_color, callback, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.callback = callback
        self.enabled = enabled

    def draw(self, surface):
        bg = self.bg_color if self.enabled else COLORS["연그레이"]
        text_c = self.text_color if self.enabled else COLORS["그레이"]
        pygame.draw.rect(surface, bg, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS["블랙"], self.rect, 1, border_radius=5)
        txt_surf = FONT_MID.render(self.text, True, text_c)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if not self.enabled: return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

def draw_shape(surface, shape, color, cx, cy, r):
    if shape == "네모":
        pygame.draw.rect(surface, color, (cx-r, cy-r, r*2, r*2))
        pygame.draw.rect(surface, COLORS["블랙"], (cx-r, cy-r, r*2, r*2), 2)
    elif shape == "동그라미":
        pygame.draw.circle(surface, color, (cx, cy), r)
        pygame.draw.circle(surface, COLORS["블랙"], (cx, cy), r, 2)
    elif shape == "세모":
        points = [(cx, cy-r), (cx-r, cy+r), (cx+r, cy+r)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "역세모":
        points = [(cx-r, cy-r), (cx+r, cy-r), (cx, cy+r)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "다이아":
        points = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "오각형":
        points = [(cx, cy-r), (cx+r, cy-int(0.3*r)), (cx+int(0.6*r), cy+r), (cx-int(0.6*r), cy+r), (cx-r, cy-int(0.3*r))]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "하트":
        points = [(cx, cy+r), (cx-r, cy-int(0.2*r)), (cx-int(0.5*r), cy-r), (cx, cy-int(0.4*r)), (cx+int(0.5*r), cy-r), (cx+r, cy-int(0.2*r))]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "별":
        points = [
            (cx, cy-r), (cx+int(0.25*r), cy-int(0.25*r)), (cx+r, cy-int(0.25*r)), 
            (cx+int(0.4*r), cy+int(0.15*r)), (cx+int(0.6*r), cy+r), (cx, cy+int(0.4*r)), 
            (cx-int(0.6*r), cy+r), (cx-int(0.4*r), cy+int(0.15*r)), (cx-r, cy-int(0.25*r)), 
            (cx-int(0.25*r), cy-int(0.25*r))
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "육각형":
        points = [(cx, cy-r), (cx+r, cy-int(0.5*r)), (cx+r, cy+int(0.5*r)), (cx, cy+r), (cx-r, cy+int(0.5*r)), (cx-r, cy-int(0.5*r))]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)
    elif shape == "십자가":
        points = [
            (cx-int(0.3*r), cy-r), (cx+int(0.3*r), cy-r), (cx+int(0.3*r), cy-int(0.3*r)),
            (cx+r, cy-int(0.3*r)), (cx+r, cy+int(0.3*r)), (cx+int(0.3*r), cy+int(0.3*r)),
            (cx+int(0.3*r), cy+r), (cx-int(0.3*r), cy+r), (cx-int(0.3*r), cy+int(0.3*r)),
            (cx-r, cy+int(0.3*r)), (cx-r, cy-int(0.3*r)), (cx-int(0.3*r), cy-int(0.3*r))
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, COLORS["블랙"], points, 2)

def draw_heart_hp(surface, color, x, y, size):
    r = size // 4
    pygame.draw.circle(surface, color, (x - r, y - r // 2), r)
    pygame.draw.circle(surface, color, (x + r, y - r // 2), r)
    pygame.draw.polygon(surface, color, [
        (x - 2 * r, y - r // 2),
        (x + 2 * r, y - r // 2),
        (x, y + size // 2)
    ])

class GameController:
    def __init__(self):
        self.state = "START"
        self.character_color = COLORS["빨강"]
        self.character_shape = "네모"
        
        self.difficulty = 1  # 1: Easy, 2: Normal, 3: Hard
        self.stage = 1
        
        # 🔥 [수정] 난이도별(1, 2, 3)로 클리어 기록을 완전 분리한 2차원 구조 데이터
        self.cleared_stages = {
            1: [False] * 6,  # Easy 난이도의 1~5 스테이지
            2: [False] * 6,  # Normal 난이도의 1~5 스테이지
            3: [False] * 6   # Hard 난이도의 1~5 스테이지
        }
        
        self.hp = 3
        self.vision_base = 6
        self.vision = 6
        self.player = [1, 1]
        self.maze = []
        self.treasure = [23, 23]
        self.monster_spawns = []
        self.monsters = []
        
        self.time_limit = 120.0
        self.time_left = 120.0
        
        self.green_inventory = 1
        self.blue_inventory = 1
        self.red_inventory = 0
        
        self.green_items_pos = []
        self.blue_items_pos = []
        self.red_items_pos = []
        self.traps_pos = []
        
        self.is_map_revealed = False
        self.map_reveal_timer = 0.0
        self.monster_spawn_cooldown = 0.0
        
        self.log_msg = "시스템 준비 완료"
        self.log_timer = 0.0

        self.init_buttons()

    def set_state(self, new_state):
        self.state = new_state
        if new_state == "STAGE":
            self.update_stage_buttons()

    def select_difficulty(self, diff):
        self.difficulty = diff
        self.set_state("STAGE")

    def start_game(self, stage_num):
        self.stage = stage_num
        
        if self.difficulty == 1:
            self.hp = 3
            self.time_limit = 120.0
            self.vision_base = 7
        elif self.difficulty == 2:
            self.hp = 2
            self.time_limit = 180.0
            self.vision_base = 5
        else:
            self.hp = 1
            self.time_limit = 300.0
            self.vision_base = 3

        self.time_left = self.time_limit
        self.vision = self.vision_base
        self.player = [1, 1]
        self.maze = self.make_maze()
        self.treasure = self.place_treasure()
        
        self.monster_spawns = [[23, 1], [1, 23], [23, 12]]
        if self.difficulty == 1:
            self.monsters = [self.monster_spawns[0][:]]
        else:
            self.monsters = [spawn[:] for spawn in self.monster_spawns[:2]]
            
        self.monster_spawn_cooldown = 8.0
        
        self.green_items_pos = []
        self.blue_items_pos = []
        self.red_items_pos = []
        self.traps_pos = []
        self.place_elements(count=2)
        
        self.is_map_revealed = False
        self.map_reveal_timer = 0
        
        self.log_msg = f"스테이지 {self.stage} 시작! 보물을 찾아 탈출하세요."
        self.log_timer = 2.5
        self.set_state("PLAY")

    def init_buttons(self):
        cx = 400  
        self.buttons = {
            "START": [
                Button(cx - 100, 300, 200, 55, "게임 시작", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("DIFFICULTY")),
                Button(cx - 100, 380, 200, 55, "커스터마이징", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("CUSTOM"))
            ],
            "CUSTOM": [
                Button(cx - 100, 680, 200, 50, "저장 후 돌아가기", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "DIFFICULTY": [
                Button(cx - 100, 280, 200, 50, "Easy (기본 난이도)", COLORS["초록"], COLORS["화이트"], lambda: self.select_difficulty(1)),
                Button(cx - 100, 350, 200, 50, "Normal (아이템 다양화)", COLORS["주황"], COLORS["블랙"], lambda: self.select_difficulty(2)),
                Button(cx - 100, 420, 200, 50, "Hard (무한/확률 증가)", COLORS["빨강"], COLORS["화이트"], lambda: self.select_difficulty(3)),
                Button(cx - 100, 520, 200, 45, "이전으로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "STAGE": [], 
            "PLAY": [
                Button(cx - 70, 730, 140, 40, "포기하기", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "CLEAR": [
                Button(cx - 100, 480, 200, 50, "다음 단계 진행", COLORS["민트"], COLORS["블랙"], self.proceed_next_stage),
                Button(cx - 100, 545, 200, 50, "메인 화면으로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "GAMEOVER": [
                Button(cx - 100, 480, 200, 50, "메인 화면으로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ]
        }
        
        color_list = [
            ("빨강", COLORS["빨강"]), ("주황", COLORS["주황"]), ("노랑", COLORS["노랑"]), 
            ("초록", COLORS["초록"]), ("파랑", COLORS["파랑"]), ("남색", COLORS["남색"]), 
            ("보라", COLORS["보라"]), ("핑크", COLORS["핑크"]), ("민트", COLORS["민트"]), 
            ("차콜", COLORS["차콜"])
        ]
        for i, (name, rgb) in enumerate(color_list):
            row, col = i // 5, i % 5
            self.buttons["CUSTOM"].append(
                Button((cx - 220) + col*90, 380 + row*45, 80, 35, name, rgb, 
                       COLORS["화이트"] if name in ["파랑", "남색", "보라", "차콜"] else COLORS["블랙"], 
                       lambda c=rgb: setattr(self, 'character_color', c))
            )
        for i, name in enumerate(SHAPES):
            row, col = i // 5, i % 5
            self.buttons["CUSTOM"].append(
                Button((cx - 220) + col*90, 540 + row*45, 80, 35, name, COLORS["화이트"], COLORS["블랙"], 
                       lambda n=name: setattr(self, 'character_shape', n))
            )

    def update_stage_buttons(self):
        cx = 400
        self.buttons["STAGE"] = []
        
        # 🔥 [수정] 현재 선택한 난이도(self.difficulty)에 해당하는 세이브 데이터만 정확히 대조
        current_difficulty_clears = self.cleared_stages[self.difficulty]
        
        for s in range(1, 6):
            enabled = True
            if s > 1 and not current_difficulty_clears[s-1]:
                enabled = False
                
            text = f"{s} [완료]" if current_difficulty_clears[s] else f"{s}"
            btn = Button((cx - 210) + (s-1)*85, 340, 75, 55, text, COLORS["연그레이"], COLORS["블랙"], 
                         lambda num=s: self.start_game(num), enabled=enabled)
            self.buttons["STAGE"].append(btn)
            
        self.buttons["STAGE"].append(Button(cx - 100, 460, 200, 45, "이전으로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("DIFFICULTY")))

    def proceed_next_stage(self):
        next_s = self.stage + 1
        if next_s <= 5:
            self.start_game(next_s)
        else:
            self.log_msg = "현재 난이도의 모든 스테이지를 정복했습니다!"
            self.set_state("START")

    def make_maze(self):
        maze = [[1] * MAZE_SIZE for _ in range(MAZE_SIZE)]
        visited = [[False] * MAZE_SIZE for _ in range(MAZE_SIZE)]
        def dfs(cx, cy):
            visited[cy][cx] = True
            maze[cy][cx] = 0
            dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < MAZE_SIZE-1 and 0 < ny < MAZE_SIZE-1:
                    if not visited[ny][nx]:
                        maze[cy + dy//2][cx + dx//2] = 0
                        dfs(nx, ny)
        dfs(1, 1)
        maze[1][1] = 0
        return maze

    def place_treasure(self):
        spots = []
        for y in range(1, MAZE_SIZE-1):
            for x in range(1, MAZE_SIZE-1):
                if self.maze[y][x] == 0 and (x != 1 or y != 1):
                    spots.append([x, y])
        return random.choice(spots) if spots else [23, 23]

    def place_elements(self, count):
        spots = []
        for y in range(1, MAZE_SIZE-1):
            for x in range(1, MAZE_SIZE-1):
                if self.maze[y][x] == 0 and [x, y] != self.player and [x, y] != self.treasure:
                    spots.append([x, y])
        random.shuffle(spots)
        
        for _ in range(min(count, len(spots))): self.green_items_pos.append(spots.pop())
        for _ in range(min(count, len(spots))): self.blue_items_pos.append(spots.pop())
        for _ in range(min(count, len(spots))): self.red_items_pos.append(spots.pop())
        for _ in range(min(count + 1, len(spots))): self.traps_pos.append(spots.pop())

    def use_green_item(self):
        if self.green_inventory > 0 and not self.is_map_revealed:
            self.green_inventory -= 1
            self.is_map_revealed = True
            self.map_reveal_timer = 3.0
            self.log_msg = "[아이템 사용] 3초간 미로의 전경을 밝힙니다!"
            self.log_timer = 2.0

    def use_blue_item(self, dx, dy):
        if self.blue_inventory > 0 and (dx != 0 or dy != 0):
            nx, ny = self.player[0] + dx, self.player[1] + dy
            if 0 < nx < MAZE_SIZE-1 and 0 < ny < MAZE_SIZE-1:
                if self.maze[ny][nx] == 1:
                    self.maze[ny][nx] = 0  
                    self.player = [nx, ny]
                    self.blue_inventory -= 1
                    self.log_msg = "[아이템 사용] 단단한 벽을 파괴하고 전진했습니다!"
                    self.log_timer = 2.0

    def move_player(self, dx, dy):
        nx, ny = self.player[0] + dx, self.player[1] + dy
        if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE and self.maze[ny][nx] == 0:
            self.player = [nx, ny]
            
            if self.player in self.green_items_pos:
                self.green_items_pos.remove(self.player)
                self.green_inventory += 1
                self.log_msg = "[획득] 초록 아이템 수집! (X 키로 사용 가능)"
                self.log_timer = 1.5
            elif self.player in self.blue_items_pos:
                self.blue_items_pos.remove(self.player)
                self.blue_inventory += 1
                self.log_msg = "[획득] 파랑 아이템 수집! (Z 키로 사용 가능)"
                self.log_timer = 1.5
            elif self.player in self.red_items_pos:
                self.red_items_pos.remove(self.player)
                self.hp += 1
                self.log_msg = "[획득] 빨강 아이템 수집! 생명력 즉시 +1 가산"
                self.log_timer = 1.5
                
            if self.player in self.traps_pos:
                self.traps_pos.remove(self.player)
                self.hp -= 1
                self.log_msg = "[함정 피격] 생명력이 1 감소했습니다!"
                self.log_timer = 2.0
                if self.hp <= 0: self.state = "GAMEOVER"
                
            if self.player == self.treasure:
                # 🔥 [수정] 클리어 시 현재 활성화된 난이도 딕셔너리에만 스탬프가 찍히도록 제한
                self.cleared_stages[self.difficulty][self.stage] = True  
                self.state = "CLEAR"

    def find_next_step_bfs(self, start, target):
        if start == target: return start
        queue = deque([[start]])
        visited = [[False] * MAZE_SIZE for _ in range(MAZE_SIZE)]
        visited[start[1]][start[0]] = True
        while queue:
            path = queue.popleft()
            cx, cy = path[-1]
            if [cx, cy] == target: return path[1]
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
                    if self.maze[ny][nx] == 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        new_path = list(path)
                        new_path.append([nx, ny])
                        queue.append(new_path)
        return start

    def update_core_engine(self, dt):
        if self.state != "PLAY": return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.state = "GAMEOVER"
            return

        if self.log_timer > 0: self.log_timer -= dt

        if self.is_map_revealed:
            self.map_reveal_timer -= dt
            self.vision = 100
            if self.map_reveal_timer <= 0:
                self.is_map_revealed = False
                self.vision = self.vision_base
        else:
            self.vision = self.vision_base

        if self.difficulty in [2, 3]:
            self.monster_spawn_cooldown -= dt
            if self.monster_spawn_cooldown <= 0:
                spawn_spots = [[23,1], [1,23], [23,23]]
                self.monsters.append(random.choice(spawn_spots)[:])
                self.monster_spawn_cooldown = 10.0 if self.difficulty == 2 else 6.0

    def move_monsters(self):
        if self.state != "PLAY": return

        for m in self.monsters:
            next_pos = self.find_next_step_bfs(m, self.player)
            m[0], m[1] = next_pos[0], next_pos[1]
            
            if m == self.player:
                self.hp -= 1
                self.monsters = [[23, 1], [1, 23], [23, 12]][:len(self.monsters)]
                self.log_msg = "[피격] 몬스터 충돌! 적들이 초기 위치로 퇴격합니다."
                self.log_timer = 2.0
                if self.hp <= 0: self.state = "GAMEOVER"
                break

    def draw_maze(self, surface):
        ox, oy = 60, 100
        for y in range(MAZE_SIZE):
            for x in range(MAZE_SIZE):
                dist = abs(x - self.player[0]) + abs(y - self.player[1])
                rect = (ox + x * CELL, oy + y * CELL, CELL, CELL)

                if dist > self.vision:
                    pygame.draw.rect(surface, COLORS["블랙"], rect)
                    continue

                color = COLORS["화이트"] if self.maze[y][x] == 0 else COLORS["그레이"]
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, COLORS["블랙"], rect, 1)

        for item in self.green_items_pos:
            if abs(item[0]-self.player[0]) + abs(item[1]-self.player[1]) <= self.vision:
                draw_shape(surface, self.character_shape, COLORS["진한초록"], ox+item[0]*CELL+CELL//2, oy+item[1]*CELL+CELL//2, CELL//3)
        for item in self.blue_items_pos:
            if abs(item[0]-self.player[0]) + abs(item[1]-self.player[1]) <= self.vision:
                draw_shape(surface, self.character_shape, COLORS["진한파랑"], ox+item[0]*CELL+CELL//2, oy+item[1]*CELL+CELL//2, CELL//3)
        for item in self.red_items_pos:
            if abs(item[0]-self.player[0]) + abs(item[1]-self.player[1]) <= self.vision:
                draw_shape(surface, self.character_shape, COLORS["진한빨강"], ox+item[0]*CELL+CELL//2, oy+item[1]*CELL+CELL//2, CELL//3)

        for trap in self.traps_pos:
            if abs(trap[0]-self.player[0]) + abs(trap[1]-self.player[1]) <= self.vision:
                pygame.draw.rect(surface, COLORS["핑크"], (ox+trap[0]*CELL+5, oy+trap[1]*CELL+5, CELL-10, CELL-10))

        tx, ty = self.treasure
        if abs(tx-self.player[0]) + abs(ty-self.player[1]) <= self.vision:
            pygame.draw.rect(surface, COLORS["골드"], (ox+tx*CELL+3, oy+ty*CELL+3, CELL-6, CELL-6))

        for m in self.monsters:
            if abs(m[0]-self.player[0]) + abs(m[1]-self.player[1]) <= self.vision:
                pygame.draw.circle(surface, COLORS["자주"], (ox+m[0]*CELL+CELL//2, oy+m[1]*CELL+CELL//2), CELL//3)

        px, py = self.player
        draw_shape(surface, self.character_shape, self.character_color, ox+px*CELL+CELL//2, oy+py*CELL+CELL//2, CELL//2-2)

    def draw_right_panel(self, surface):
        rx = 690
        pygame.draw.rect(surface, COLORS["연그레이"], (rx, 0, WIDTH - rx, HEIGHT))
        pygame.draw.line(surface, COLORS["블랙"], (rx, 0), (rx, HEIGHT), 2)
        
        surface.blit(FONT_MID.render("🎒 인벤토리 & 정보", True, COLORS["블랙"]), (rx + 20, 40))
        pygame.draw.line(surface, COLORS["그레이"], (rx + 20, 75), (WIDTH - 20, 75), 1)
        
        draw_shape(surface, self.character_shape, COLORS["진한초록"], rx + 40, 120, 14)
        surface.blit(FONT_MID.render(f"보유: {self.green_inventory}개", True, COLORS["블랙"]), (rx + 75, 110))
        surface.blit(FONT_SMALL.render("[X 키] 전체 맵 보기 뷰어", True, COLORS["진한초록"]), (rx + 30, 150))
        surface.blit(FONT_SMALL.render("3초간 모든 미로 안개 제거", True, COLORS["블랙"]), (rx + 30, 172))
        
        draw_shape(surface, self.character_shape, COLORS["진한파랑"], rx + 40, 240, 14)
        surface.blit(FONT_MID.render(f"보유: {self.blue_inventory}개", True, COLORS["블랙"]), (rx + 75, 230))
        surface.blit(FONT_SMALL.render("[Z 키] 인스턴트 벽 뚫기", True, COLORS["진한파랑"]), (rx + 30, 270))
        surface.blit(FONT_SMALL.render("바라보는 앞의 벽 1칸 파괴", True, COLORS["블랙"]), (rx + 30, 292))
        
        draw_shape(surface, self.character_shape, COLORS["진한빨강"], rx + 40, 360, 14)
        surface.blit(FONT_SMALL.render("패시브: 생명력 즉시 가산", True, COLORS["진한빨강"]), (rx + 30, 390))
        surface.blit(FONT_SMALL.render("습득 시 라이프 하트 1개 충전", True, COLORS["블랙"]), (rx + 30, 412))
        
        pygame.draw.line(surface, COLORS["그레이"], (rx + 20, 460), (WIDTH - 20, 460), 1)
        surface.blit(FONT_SMALL.render("■ 분홍색 사각형: 위험 함정", True, COLORS["자주"]), (rx + 20, 485))
        surface.blit(FONT_SMALL.render("■ 황금색 사각형: 최종 탈출구", True, COLORS["블랙"]), (rx + 20, 515))

    def draw(self, surface):
        surface.fill(COLORS["화이트"])
        cx = 400
        
        if self.state == "START":
            title_surf = FONT_BIG.render("🎮 도망쳐! 네모 시스템", True, COLORS["블랙"])
            surface.blit(title_surf, title_surf.get_rect(center=(cx, 160)))
            
        elif self.state == "CUSTOM":
            title_surf = FONT_BIG.render("🎨 캐릭터 커스터마이징", True, COLORS["블랙"])
            surface.blit(title_surf, title_surf.get_rect(center=(cx, 60)))
            
            pygame.draw.rect(surface, COLORS["화이트"], (cx-60, 120, 120, 120))
            pygame.draw.rect(surface, COLORS["그레이"], (cx-60, 120, 120, 120), 1)
            draw_shape(surface, self.character_shape, self.character_color, cx, 180, 40)
            
            surface.blit(FONT_MID.render("🎨 색상 선택 (10종)", True, COLORS["블랙"]), (cx - 220, 340))
            surface.blit(FONT_MID.render("⭐ 모양 선택 (10종)", True, COLORS["블랙"]), (cx - 220, 500))

        elif self.state == "DIFFICULTY":
            title_surf = FONT_BIG.render("난이도 선택 단계", True, COLORS["블랙"])
            surface.blit(title_surf, title_surf.get_rect(center=(cx, 180)))

        elif self.state == "STAGE":
            diff_names = {1: "Easy", 2: "Normal", 3: "Hard"}
            title_surf = FONT_BIG.render(f"스테이지 선택 [{diff_names[self.difficulty]}]", True, COLORS["블랙"])
            surface.blit(title_surf, title_surf.get_rect(center=(cx, 200)))
            
            tip_surf = FONT_SMALL.render("※ 해당 난이도의 이전 단계를 깨야 다음 단계 진입이 가능합니다.", True, COLORS["차콜"])
            surface.blit(tip_surf, tip_surf.get_rect(center=(cx, 260)))

        elif self.state == "PLAY":
            self.draw_maze(surface)
            self.draw_right_panel(surface)
            
            mins, secs = int(self.time_left // 60), int(self.time_left % 60)
            time_str = f"⏱️ {mins:02d}:{secs:02d}"
            surface.blit(FONT_BIG.render(time_str, True, COLORS["블랙"]), (530, 30))
            
            surface.blit(FONT_MID.render(f"STAGE {self.stage}", True, COLORS["블랙"]), (60, 735))
            
            for i in range(max(0, self.hp)):
                draw_heart_hp(surface, COLORS["빨강"], 35 + i * 40, 35, 30)

            if self.log_timer > 0:
                log_surf = FONT_SMALL.render(self.log_msg, True, COLORS["남색"])
                surface.blit(log_surf, (60, 75))

        elif self.state == "CLEAR":
            clear_surf = FONT_BIG.render("🎉 STAGE CLEAR! 탈출 성공", True, COLORS["초록"])
            surface.blit(clear_surf, clear_surf.get_rect(center=(cx, 260)))
            
            score_surf = FONT_MID.render(f"보너스 스코어 타임 레코더: {int(self.time_left)}초 남음", True, COLORS["블랙"])
            surface.blit(score_surf, score_surf.get_rect(center=(cx, 340)))

        elif self.state == "GAMEOVER":
            over_surf = FONT_BIG.render("💀 GAME OVER (탈출 실패)", True, COLORS["빨강"])
            surface.blit(over_surf, over_surf.get_rect(center=(cx, 320)))

        for btn in self.buttons[self.state]:
            btn.draw(surface)

def main():
    controller = GameController()
    monster_move_timer = 0.0
    last_dx, last_dy = 0, 1  
    
    while True:
        dt = clock.tick(60) / 1000.0 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in controller.buttons[controller.state]:
                    btn.handle_event(event)
            
            if controller.state == "PLAY" and event.type == pygame.KEYDOWN:
                dx = dy = 0
                if event.key == pygame.K_LEFT:  dx = -1; last_dx, last_dy = -1, 0
                if event.key == pygame.K_RIGHT: dx = 1;  last_dx, last_dy = 1, 0
                if event.key == pygame.K_UP:    dy = -1; last_dx, last_dy = 0, -1
                if event.key == pygame.K_DOWN:  dy = 1;  last_dx, last_dy = 0, 1

                if event.key == pygame.K_x:
                    controller.use_green_item()
                if event.key == pygame.K_z:
                    controller.use_blue_item(last_dx, last_dy)

                if dx != 0 or dy != 0:
                    controller.move_player(dx, dy)

        if controller.state == "PLAY":
            controller.update_core_engine(dt)
            
            monster_move_timer += dt
            if monster_move_timer > 0.35:
                controller.move_monsters()
                monster_move_timer = 0.0

        controller.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
