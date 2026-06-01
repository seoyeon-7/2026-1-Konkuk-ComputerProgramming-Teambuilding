import pygame, random, sys
from collections import deque

pygame.init()

# 화면 및 격자 설정 (UI 구조에 맞춰 조정)
WIDTH, HEIGHT = 800, 800
CELL = 24
MAZE_SIZE = 25  # DFS 미로 생성을 위해 반드시 홀수

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("도망쳐! 네모")
clock = pygame.time.Clock()

# 색상 사전 통합 및 정의
COLORS = {
    "빨강": (255, 0, 0), "주황": (255, 165, 0), "노랑": (255, 255, 0), 
    "초록": (0, 128, 0), "파랑": (0, 0, 255), "남색": (0, 0, 128), 
    "보라": (128, 0, 128), "핑크": (255, 192, 203), "민트": (62, 180, 137), 
    "차콜": (54, 69, 79), "화이트": (255, 255, 255), "블랙": (0, 0, 0),
    "그레이": (128, 128, 128), "연그레이": (211, 211, 211), "골드": (255, 215, 0)
}

SHAPES = ["네모", "동그라미", "세모", "역세모", "다이아", "오각형", "하트", "별", "육각형", "십자가"]

# 폰트 구성
try:
    FONT_BIG = pygame.font.SysFont("malgungothic", 36, bold=True)
    FONT_MID = pygame.font.SysFont("malgungothic", 20, bold=True)
    FONT_SMALL = pygame.font.SysFont("malgungothic", 14)
except:
    FONT_BIG = pygame.font.Font(None, 48)
    FONT_MID = pygame.font.Font(None, 28)
    FONT_SMALL = pygame.font.Font(None, 20)

class Button:
    def __init__(self, x, y, w, h, text, bg_color, text_color, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS["블랙"], self.rect, 1, border_radius=5)
        
        txt_surf = FONT_MID.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_event(self, event):
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
        
        # 인게임 핵심 변수들
        self.difficulty = 1
        self.hp = 3
        self.vision_base = 6
        self.vision = 6
        self.player = [1, 1]
        self.maze = []
        self.treasure = [23, 23]
        self.monster_spawns = []
        self.monsters = []
        
        self.green_items_count = 1
        self.blue_items_count = 1
        self.is_map_revealed = False
        self.item_timer = 0
        
        self.green_items_pos = []
        self.blue_items_pos = []
        self.red_items_pos = []
        
        self.init_buttons()

    def set_state(self, new_state):
        self.state = new_state

    def set_color(self, color_tuple):
        self.character_color = color_tuple

    def set_shape(self, shape_name):
        self.character_shape = shape_name

    def start_game(self, diff):
        self.difficulty = diff
        self.hp = {1: 3, 2: 2, 3: 1}[diff]
        self.vision_base = {1: 6, 2: 4, 3: 2}[diff]
        self.vision = self.vision_base
        self.player = [1, 1]
        self.maze = self.make_maze()
        
        self.treasure = self.place_treasure()
        
        self.monster_spawns = [[23, 1], [1, 23], [23, 12]][:diff]
        self.monsters = [spawn[:] for spawn in self.monster_spawns]
        
        # 아이템 초기화 (기본 지급 1개씩)
        self.green_items_count = 1
        self.blue_items_count = 1
        self.is_map_revealed = False
        self.item_timer = 0
        
        self.green_items_pos = []
        self.blue_items_pos = []
        self.red_items_pos = []
        
        self.place_items(3)
        self.set_state("PLAY")

    def init_buttons(self):
        # 레이아웃을 800x800 화면 비율에 맞게 중앙 정렬
        cx = WIDTH // 2
        self.buttons = {
            "START": [
                Button(cx - 100, 260, 200, 50, "쉬움 (1단계)", COLORS["연그레이"], COLORS["블랙"], lambda: self.start_game(1)),
                Button(cx - 100, 325, 200, 50, "보통 (2단계)", COLORS["연그레이"], COLORS["블랙"], lambda: self.start_game(2)),
                Button(cx - 100, 390, 200, 50, "어려움 (3단계)", COLORS["연그레이"], COLORS["블랙"], lambda: self.start_game(3)),
                Button(cx - 100, 470, 200, 55, "커스터마이징", COLORS["차콜"], COLORS["화이트"], lambda: self.set_state("CUSTOM"))
            ],
            "CUSTOM": [
                Button(cx - 100, 680, 200, 50, "돌아가기", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "PLAY": [
                Button(625, 710, 140, 45, "포기하기", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "CLEAR": [
                Button(cx - 100, 450, 200, 50, "메인 메뉴로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "GAMEOVER": [
                Button(cx - 100, 450, 200, 50, "메인 메뉴로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ]
        }
        
        # 커스텀 창 색상 버튼 (5개씩 2줄 배치)
        color_list = [
            ("빨강", COLORS["빨강"]), ("주황", COLORS["주황"]), ("노랑", COLORS["노랑"]), 
            ("초록", COLORS["초록"]), ("파랑", COLORS["파랑"]), ("남색", COLORS["남색"]), 
            ("보라", COLORS["보라"]), ("핑크", COLORS["핑크"]), ("민트", COLORS["민트"]), 
            ("차콜", COLORS["차콜"])
        ]
        for i, (name, rgb) in enumerate(color_list):
            row = i // 5
            col = i % 5
            x = (WIDTH // 2 - 220) + col * 90
            y = 380 + row * 45
            btn = Button(x, y, 80, 35, name, rgb, COLORS["화이트"] if name in ["파랑", "남색", "보라", "차콜"] else COLORS["블랙"], lambda c=rgb: self.set_color(c))
            self.buttons["CUSTOM"].append(btn)

        # 커스텀 창 모양 버튼 (5개씩 2줄 배치)
        for i, name in enumerate(SHAPES):
            row = i // 5
            col = i % 5
            x = (WIDTH // 2 - 220) + col * 90
            y = 540 + row * 45
            btn = Button(x, y, 80, 35, name, COLORS["화이트"], COLORS["블랙"], lambda n=name: self.set_shape(n))
            self.buttons["CUSTOM"].append(btn)

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
        possible_spots = []
        for y in range(1, MAZE_SIZE-1):
            for x in range(1, MAZE_SIZE-1):
                if self.maze[y][x] == 0:
                    dist = abs(x - self.player[0]) + abs(y - self.player[1])
                    if dist >= 15:  
                        possible_spots.append([x, y])
        if possible_spots:
            return random.choice(possible_spots)
        return [23, 23]

    def place_items(self, count):
        available_spots = []
        for y in range(1, MAZE_SIZE-1):
            for x in range(1, MAZE_SIZE-1):
                if self.maze[y][x] == 0 and not (x == self.player[0] and y == self.player[1]) and not (x == self.treasure[0] and y == self.treasure[1]):
                    available_spots.append([x, y])
        
        random.shuffle(available_spots)
        for _ in range(count):
            if available_spots: self.green_items_pos.append(available_spots.pop())
        for _ in range(count):
            if available_spots: self.blue_items_pos.append(available_spots.pop())
        for _ in range(count):
            if available_spots: self.red_items_pos.append(available_spots.pop())

    def check_item_pickup(self):
        if self.player in self.green_items_pos:
            self.green_items_pos.remove(self.player)
            self.green_items_count += 1
        if self.player in self.blue_items_pos:
            self.blue_items_pos.remove(self.player)
            self.blue_items_count += 1
        if self.player in self.red_items_pos:
            self.red_items_pos.remove(self.player)
            self.hp += 1

    def use_green_item(self):
        if self.green_items_count > 0 and not self.is_map_revealed:
            self.green_items_count -= 1
            self.is_map_revealed = True
            self.item_timer = 3000  
            self.vision = 100       

    def use_blue_item(self, last_dx, last_dy):
        if self.blue_items_count > 0 and (last_dx != 0 or last_dy != 0):
            nx = self.player[0] + last_dx
            ny = self.player[1] + last_dy
            if 0 < nx < MAZE_SIZE-1 and 0 < ny < MAZE_SIZE-1:
                if self.maze[ny][nx] == 1:  
                    self.maze[ny][nx] = 0   
                    self.player = [nx, ny]
                    self.blue_items_count -= 1

    def find_next_step_bfs(self, start, target):
        if start == target:
            return start
        queue = deque([[start]])
        visited = [[False] * MAZE_SIZE for _ in range(MAZE_SIZE)]
        visited[start[1]][start[0]] = True

        while queue:
            path = queue.popleft()
            cx, cy = path[-1]
            if [cx, cy] == target:
                return path[1]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE:
                    if self.maze[ny][nx] == 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        new_path = list(path)
                        new_path.append([nx, ny])
                        queue.append(new_path)
        return start

    def move_monsters(self):
        for m in self.monsters:
            next_pos = self.find_next_step_bfs(m, self.player)
            m[0], m[1] = next_pos[0], next_pos[1]

            if m == self.player:
                self.hp -= 1
                # 캐릭터 고정, 몬스터만 초기 위치 우회 리젠
                self.monsters = [spawn[:] for spawn in self.monster_spawns]
                if self.hp <= 0:
                    self.state = "GAMEOVER"
                break

    def draw_maze(self, surface):
        ox, oy = 100, 100
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

        # 아이템들 그리기 (커스텀한 사용자 외형 모양 규칙에 연동)
        for g in self.green_items_pos:
            if abs(g[0]-self.player[0]) + abs(g[1]-self.player[1]) <= self.vision:
                draw_shape(surface, self.character_shape, COLORS["초록"], ox+g[0]*CELL+CELL//2, oy+g[1]*CELL+CELL//2, CELL//3)

        for b in self.blue_items_pos:
            if abs(b[0]-self.player[0]) + abs(b[1]-self.player[1]) <= self.vision:
                draw_shape(surface, self.character_shape, COLORS["파랑"], ox+b[0]*CELL+CELL//2, oy+b[1]*CELL+CELL//2, CELL//3)

        for r_item in self.red_items_pos:
            if abs(r_item[0]-self.player[0]) + abs(r_item[1]-self.player[1]) <= self.vision:
                draw_shape(surface, self.character_shape, COLORS["빨강"], ox+r_item[0]*CELL+CELL//2, oy+r_item[1]*CELL+CELL//2, CELL//3)

        # 황금 보물 상자
        tx, ty = self.treasure
        if abs(tx-self.player[0]) + abs(ty-self.player[1]) <= self.vision:
            pygame.draw.rect(surface, COLORS["골드"], (ox+tx*CELL+4, oy+ty*CELL+4, CELL-8, CELL-8))

        # 몬스터 (원형으로 고정)
        for m in self.monsters:
            if abs(m[0]-self.player[0]) + abs(m[1]-self.player[1]) <= self.vision:
                pygame.draw.circle(surface, COLORS["빨강"], (ox+m[0]*CELL+CELL//2, oy+m[1]*CELL+CELL//2), CELL//3)

        # 플레이어 캐릭터 (커스터마이징 데이터 실시간 반영)
        px, py = self.player
        draw_shape(surface, self.character_shape, self.character_color, ox+px*CELL+CELL//2, oy+py*CELL+CELL//2, CELL//2-2)

    def update_timers(self, dt):
        if self.is_map_revealed:
            self.item_timer -= dt
            if self.item_timer <= 0:
                self.is_map_revealed = False
                self.vision = self.vision_base

    def handle_events(self, event):
        # 버튼 이벤트 공통 연동
        for btn in self.buttons[self.state]:
            btn.handle_event(event)

    def update(self):
        if self.state == "PLAY":
            self.move_monsters()
            if self.player == self.treasure:
                self.state = "CLEAR"

    def draw(self, surface):
        surface.fill(COLORS["화이트"])
        cx = WIDTH // 2
        
        if self.state == "START":
            title_surf = FONT_BIG.render("🎮 도망쳐! 네모", True, COLORS["블랙"])
            title_rect = title_surf.get_rect(center=(cx, 130))
            surface.blit(title_surf, title_rect)
            
        elif self.state == "CUSTOM":
            title_surf = FONT_BIG.render("🎨 캐릭터 커스터마이징", True, COLORS["블랙"])
            title_rect = title_surf.get_rect(center=(cx, 60))
            surface.blit(title_surf, title_rect)
            
            # 미리보기 상자 내부 그리기
            pygame.draw.rect(surface, COLORS["화이트"], (cx-60, 120, 120, 120))
            pygame.draw.rect(surface, COLORS["그레이"], (cx-60, 120, 120, 120), 1)
            draw_shape(surface, self.character_shape, self.character_color, cx, 180, 40)
            
            color_label = FONT_MID.render("🎨 색상 선택 (10종)", True, COLORS["블랙"])
            surface.blit(color_label, (cx - 220, 340))
            
            shape_label = FONT_MID.render("⭐ 모양 선택 (10종)", True, COLORS["블랙"])
            surface.blit(shape_label, (cx - 220, 500))

        elif self.state == "PLAY":
            self.draw_maze(surface)
            
            # 하트 체력 표기
            for i in range(self.hp):
                draw_heart_hp(surface, COLORS["빨강"], 35 + i * 40, 35, 30)
                
            # 인벤토리 표시창 (우측 상단 상시 노출)
            draw_shape(surface, self.character_shape, COLORS["초록"], 630, 35, 10)
            surface.blit(FONT_SMALL.render(f"[X] 사용: {self.green_items_count}개", True, COLORS["블랙"]), (650, 25))
            draw_shape(surface, self.character_shape, COLORS["파랑"], 630, 65, 10)
            surface.blit(FONT_SMALL.render(f"[Z] 뚫기: {self.blue_items_count}개", True, COLORS["블랙"]), (650, 55))

        elif self.state == "CLEAR":
            clear_surf = FONT_BIG.render("🎉 대성공! 탈출 성공!", True, COLORS["초록"])
            clear_rect = clear_surf.get_rect(center=(cx, 320))
            surface.blit(clear_surf, clear_rect)

        elif self.state == "GAMEOVER":
            over_surf = FONT_BIG.render("💀 GAME OVER", True, COLORS["빨강"])
            over_rect = over_surf.get_rect(center=(cx, 320))
            surface.blit(over_surf, over_rect)

        for btn in self.buttons[self.state]:
            btn.draw(surface)

def main():
    controller = GameController()
    monster_timer = 0
    last_dx, last_dy = 0, 0 
    
    while True:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            controller.handle_events(event)
            
            # 인게임 플레이어 조작 입력 분리
            if controller.state == "PLAY" and event.type == pygame.KEYDOWN:
                dx = dy = 0
                if event.key == pygame.K_LEFT: dx = -1; last_dx, last_dy = -1, 0
                if event.key == pygame.K_RIGHT: dx = 1; last_dx, last_dy = 1, 0
                if event.key == pygame.K_UP: dy = -1; last_dx, last_dy = 0, -1
                if event.key == pygame.K_DOWN: dy = 1; last_dx, last_dy = 0, 1

                if event.key == pygame.K_x: 
                    controller.use_green_item()
                if event.key == pygame.K_z: 
                    controller.use_blue_item(last_dx, last_dy)

                nx = controller.player[0] + dx
                ny = controller.player[1] + dy

                if 0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE and controller.maze[ny][nx] == 0:
                    controller.player = [nx, ny]
                
                controller.check_item_pickup()

        if controller.state == "PLAY":
            controller.update_timers(dt)
            monster_timer += dt
            if monster_timer > 350:
                controller.update()
                monster_timer = 0
        else:
            # 보물 상자 도달 조건 상시 체크 리셋 방지
            controller.update()

        controller.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
