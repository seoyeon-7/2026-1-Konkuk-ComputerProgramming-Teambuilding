import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 650, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("도망쳐! 네모")
clock = pygame.time.Clock()

COLORS = {
    "빨강": (255, 0, 0), "주황": (255, 165, 0), "노랑": (255, 255, 0), 
    "초록": (0, 128, 0), "파랑": (0, 0, 255), "남색": (0, 0, 128), 
    "보라": (128, 0, 128), "핑크": (255, 192, 203), "민트": (62, 180, 137), 
    "차콜": (54, 69, 79), "화이트": (255, 255, 255), "블랙": (0, 0, 0),
    "그레이": (128, 128, 128), "연그레이": (211, 211, 211)
}

SHAPES = ["네모", "동그라미", "세모", "역세모", "다이아", "오각형", "하트", "별", "육각형", "십자가"]

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

class GameController:
    def __init__(self):
        self.state = "START"
        self.character_color = COLORS["빨강"]
        self.character_shape = "네모"
        self.init_buttons()

    def set_state(self, new_state):
        self.state = new_state
        print(f"[로그] 화면 전환 -> {new_state}")

    def set_color(self, color_tuple):
        self.character_color = color_tuple

    def set_shape(self, shape_name):
        self.character_shape = shape_name

    def init_buttons(self):
        self.buttons = {
            "START": [
                Button(225, 250, 200, 60, "게임 시작", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("PLAY")),
                Button(225, 340, 200, 60, "커스터마이징", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("CUSTOM"))
            ],
            "CUSTOM": [
                Button(225, 560, 200, 50, "돌아가기", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ],
            "PLAY": [
                Button(225, 500, 200, 50, "메인으로", COLORS["연그레이"], COLORS["블랙"], lambda: self.set_state("START"))
            ]
        }
        
        color_list = [
            ("빨강", COLORS["빨강"]), ("주황", COLORS["주황"]), ("노랑", COLORS["노랑"]), 
            ("초록", COLORS["초록"]), ("파랑", COLORS["파랑"]), ("남색", COLORS["남색"]), 
            ("보라", COLORS["보라"]), ("핑크", COLORS["핑크"]), ("민트", COLORS["민트"]), 
            ("차콜", COLORS["차콜"])
        ]
        for i, (name, rgb) in enumerate(color_list):
            row = i // 5
            col = i % 5
            x = 100 + col * 90
            y = 320 + row * 45
            btn = Button(x, y, 80, 35, name, rgb, COLORS["화이트"] if name in ["파랑", "남색", "보라", "차콜"] else COLORS["블랙"], lambda c=rgb: self.set_color(c))
            self.buttons["CUSTOM"].append(btn)

        for i, name in enumerate(SHAPES):
            row = i // 5
            col = i % 5
            x = 100 + col * 90
            y = 460 + row * 45
            btn = Button(x, y, 80, 35, name, COLORS["화이트"], COLORS["블랙"], lambda n=name: self.set_shape(n))
            self.buttons["CUSTOM"].append(btn)

    def handle_events(self, event):
        for btn in self.buttons[self.state]:
            btn.handle_event(event)

    def draw(self, surface):
        surface.fill(COLORS["화이트"])
        
        if self.state == "START":
            title_surf = FONT_BIG.render("🎮 도망쳐! 네모", True, COLORS["블랙"])
            title_rect = title_surf.get_rect(center=(WIDTH//2, 120))
            surface.blit(title_surf, title_rect)
            
        elif self.state == "CUSTOM":
            title_surf = FONT_BIG.render("🎨 캐릭터 커스터마이징", True, COLORS["블랙"])
            title_rect = title_surf.get_rect(center=(WIDTH//2, 50))
            surface.blit(title_surf, title_rect)
            
            pygame.draw.rect(surface, COLORS["화이트"], (265, 100, 120, 120))
            pygame.draw.rect(surface, COLORS["그레이"], (265, 100, 120, 120), 1)
            
            draw_shape(surface, self.character_shape, self.character_color, 325, 160, 40)
            
            color_label = FONT_MID.render("🎨 색상 선택 (10종)", True, COLORS["블랙"])
            surface.blit(color_label, (100, 285))
            
            shape_label = FONT_MID.render("⭐ 모양 선택 (10종)", True, COLORS["블랙"])
            surface.blit(shape_label, (100, 425))

        elif self.state == "PLAY":
            title_surf = FONT_BIG.render("🚀 게임 플레이 화면", True, COLORS["블랙"])
            title_rect = title_surf.get_rect(center=(WIDTH//2, 60))
            surface.blit(title_surf, title_rect)
            
            pygame.draw.rect(surface, COLORS["연그레이"], (175, 150, 300, 300))
            draw_shape(surface, self.character_shape, self.character_color, 325, 300, 50)

        for btn in self.buttons[self.state]:
            btn.draw(surface)

def main():
    controller = GameController()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            controller.handle_events(event)
            
        controller.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    