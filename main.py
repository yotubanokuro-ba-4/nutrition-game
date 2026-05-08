import pygame
import asyncio
import random
import math

# Initialize
pygame.init()

# Screen Settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nutrition Survival 100")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
C_YELLOW = (255, 255, 0)
P_RED = (255, 50, 50)
V_GREEN = (50, 255, 50)
GRAY = (100, 100, 100)
PURPLE = (150, 0, 255)
MAGENTA = (255, 0, 255)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)

# --- Final Balancing Params ---
FPS = 60
PLAYER_SPEED = 5
AGE_LIMIT = 100 
GAUGE_DECREASE_BASE = 0.08
# 食べ物の量を0.85倍に修正 (0.03 -> 0.0255)
ITEM_SPAWN_RATE = 0.0255
ENEMY_SPAWN_RATE = 0.0067
VIRUS_SPEED = 1.8           
RECOVERY_AMOUNT = 35        
VIRUS_DAMAGE = 10           

def reset_game():
    return {
        "player_pos": [WIDTH // 2, HEIGHT // 2],
        "items": [], 
        "enemies": [], 
        "age": 0,
        "gauges": {"C": 100.0, "P": 100.0, "V": 100.0},
        "state": "TITLE",
        "cleared": False
    }

def draw_player(surf, pos, color, gauges):
    x, y = int(pos[0]), int(pos[1])
    min_val = min(gauges.values())
    pygame.draw.circle(surf, color, (x + 20, y + 20), 20)
    eye_color = BLACK
    if min_val < 20:
        pygame.draw.line(surf, eye_color, (x+12, y+12), (x+18, y+18), 3)
        pygame.draw.line(surf, eye_color, (x+18, y+12), (x+12, y+18), 3)
        pygame.draw.line(surf, eye_color, (x+22, y+12), (x+28, y+18), 3)
        pygame.draw.line(surf, eye_color, (x+28, y+12), (x+22, y+18), 3)
    else:
        pygame.draw.circle(surf, WHITE, (x + 13, y + 15), 6)
        pygame.draw.circle(surf, eye_color, (x + 13, y + 15), 3)
        pygame.draw.circle(surf, WHITE, (x + 27, y + 15), 6)
        pygame.draw.circle(surf, eye_color, (x + 27, y + 15), 3)

def draw_food(surf, pos, n_type, food_id, show_frame=True):
    x, y = int(pos[0]), int(pos[1])
    if show_frame:
        frame_col = C_YELLOW if n_type == "C" else P_RED if n_type == "P" else V_GREEN
        pygame.draw.circle(surf, frame_col, (x + 10, y + 10), 15, 3)

    if n_type == "C":
        if food_id == 0: # おにぎり
            pygame.draw.polygon(surf, WHITE, [(x+10, y), (x, y+20), (x+20, y+20)])
            pygame.draw.rect(surf, BLACK, (x+7, y+14, 6, 6))
        elif food_id == 1: # パン
            pygame.draw.rect(surf, (245, 222, 179), (x+2, y+2, 16, 16))
            pygame.draw.rect(surf, BROWN, (x+2, y+2, 16, 16), 2)
        else: # ラーメン
            pygame.draw.arc(surf, P_RED, (x, y+8, 20, 12), math.pi, 0, 10)
            pygame.draw.line(surf, C_YELLOW, (x+4, y+6), (x+16, y+6), 3)

    elif n_type == "P":
        if food_id == 0: # お肉
            pygame.draw.ellipse(surf, BROWN, (x, y+5, 20, 12))
            pygame.draw.rect(surf, WHITE, (x-2, y+8, 5, 5))
        elif food_id == 1: # 魚
            pygame.draw.ellipse(surf, (255, 192, 203), (x, y+5, 20, 10))
            pygame.draw.line(surf, WHITE, (x+4, y+6), (x+10, y+14), 2)
        else: # 卵
            pygame.draw.circle(surf, WHITE, (x+10, y+10), 9)
            pygame.draw.circle(surf, ORANGE, (x+10, y+10), 4)

    elif n_type == "V":
        if food_id == 0: # リンゴ
            pygame.draw.circle(surf, P_RED, (x+10, y+12), 8)
            pygame.draw.line(surf, V_GREEN, (x+10, y+4), (x+13, y), 2)
        elif food_id == 1: # ブロッコリー
            pygame.draw.circle(surf, V_GREEN, (x+10, y+7), 7)
            pygame.draw.rect(surf, (34, 139, 34), (x+8, y+12, 4, 8))
        else: # バナナ
            pygame.draw.arc(surf, C_YELLOW, (x+2, y+2, 15, 20), 0, math.pi/1.2, 5)

def draw_enemy(surf, en_type, pos, size):
    x, y = int(pos[0]), int(pos[1])
    cx, cy = x + size//2, y + size//2
    if en_type == "v":
        color = PURPLE
        points = []
        for i in range(12):
            angle = i * (math.pi / 6)
            dist = size//2 if i % 2 == 0 else size//3
            points.append((cx + math.cos(angle)*dist, cy + math.sin(angle)*dist))
        pygame.draw.polygon(surf, color, points)
        pygame.draw.circle(surf, P_RED, (cx - 5, cy), 3)
        pygame.draw.circle(surf, P_RED, (cx + 5, cy), 3)
    elif en_type == "c":
        color = MAGENTA
        num_circles = 5
        for i in range(num_circles):
            off_x = random.randint(-size//4, size//4)
            off_y = random.randint(-size//4, size//4)
            c_size = random.randint(size//3, size//2)
            pygame.draw.circle(surf, color, (cx + off_x, cy + off_y), c_size)
        pygame.draw.circle(surf, BLACK, (cx - 6, cy - 4), 3)
        pygame.draw.circle(surf, BLACK, (cx + 6, cy - 4), 3)

def get_player_color(gauges):
    min_val = min(gauges.values())
    if min_val >= 80: return (255, 105, 180)
    if min_val >= 50: return (255, 255, 0)
    if min_val >= 20: return (144, 238, 144)
    return (100, 100, 255)

async def main():
    state_data = reset_game()
    clock = pygame.time.Clock()
    font_s = pygame.font.SysFont("sans-serif", 20)
    font_m = pygame.font.SysFont("sans-serif", 28)
    font_l = pygame.font.SysFont("sans-serif", 64)

    running = True
    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state_data["state"] == "TITLE": state_data["state"] = "PLAYING"
                elif state_data["state"] == "RESULT":
                    state_data = reset_game()
                    state_data["state"] = "PLAYING"

        if state_data["state"] == "TITLE":
            screen.blit(font_l.render("NUTRITION SURVIVAL 100", True, GOLD), (WIDTH//2 - 320, 50))
            
            y_off = 150
            groups = [
                ("C", C_YELLOW, "Yellow: Energy"),
                ("P", P_RED, "Red: Muscle"),
                ("V", V_GREEN, "Green: Condition")
            ]
            
            for g_type, col, label in groups:
                screen.blit(font_m.render(label, True, col), (50, y_off))
                # 各グループの食べ物アイコンを表示
                for i in range(3):
                    draw_food(screen, (250 + i*40, y_off), g_type, i, show_frame=False)
                y_off += 50
            
            y_off += 20
            # 敵の説明
            draw_enemy(screen, "v", (50, y_off), 30)
            screen.blit(font_s.render("Purple Virus: Steals your nutrition!", True, PURPLE), (100, y_off + 5))
            y_off += 45
            draw_enemy(screen, "c", (50, y_off), 30)
            screen.blit(font_s.render("Magenta Cancer: High damage! (From age 50)", True, MAGENTA), (100, y_off + 5))

            # 操作説明（スマホを考慮）
            y_off += 60
            screen.blit(font_m.render("How to Move:", True, WHITE), (WIDTH//2 - 300, y_off))
            screen.blit(font_s.render("- PC: Arrow Keys", True, WHITE), (WIDTH//2 - 300, y_off + 35))
            screen.blit(font_s.render("- Mobile: Tap On-Screen Buttons", True, WHITE), (WIDTH//2 - 300, y_off + 60))

            screen.blit(font_m.render(">> CLICK TO START <<", True, V_GREEN), (WIDTH//2 - 140, 520))

        elif state_data["state"] == "PLAYING":
            # --- Mobile Buttons Setup (Re-defined for drawing) ---
            BTN_SIZE = 60
            b_list = {
                "UP":    pygame.Rect(100, 400, BTN_SIZE, BTN_SIZE),
                "DOWN":  pygame.Rect(100, 520, BTN_SIZE, BTN_SIZE),
                "LEFT":  pygame.Rect(40, 460, BTN_SIZE, BTN_SIZE),
                "RIGHT": pygame.Rect(160, 460, BTN_SIZE, BTN_SIZE)
            }

            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or (mouse_pressed and b_list["LEFT"].collidepoint(mouse_pos)): dx = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or (mouse_pressed and b_list["RIGHT"].collidepoint(mouse_pos)): dx = PLAYER_SPEED
            if keys[pygame.K_UP] or (mouse_pressed and b_list["UP"].collidepoint(mouse_pos)): dy = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or (mouse_pressed and b_list["DOWN"].collidepoint(mouse_pos)): dy = PLAYER_SPEED

            state_data["player_pos"][0] = max(0, min(WIDTH-40, state_data["player_pos"][0] + dx))
            state_data["player_pos"][1] = max(0, min(HEIGHT-40, state_data["player_pos"][1] + dy))

            diff = 1.0 + (state_data["age"] / 150)
            for k in state_data["gauges"]:
                state_data["gauges"][k] -= GAUGE_DECREASE_BASE * diff
                if state_data["gauges"][k] <= 0: state_data["state"] = "RESULT"

            state_data["age"] += 1/FPS 
            if state_data["age"] >= AGE_LIMIT:
                state_data["cleared"] = True
                state_data["state"] = "RESULT"

            if random.random() < ITEM_SPAWN_RATE:
                state_data["items"].append({"pos": [random.randint(20, WIDTH-20), random.randint(20, HEIGHT-20)], "type": random.choice(["C", "P", "V"]), "f_id": random.randint(0, 2)})
            
            if random.random() < ENEMY_SPAWN_RATE:
                cancer_prob = 0.3 if state_data["age"] > 50 else 0
                e_type = "c" if (random.random() < cancer_prob) else "v"
                vx = random.choice([-VIRUS_SPEED, VIRUS_SPEED])
                vy = random.choice([-VIRUS_SPEED, VIRUS_SPEED])
                state_data["enemies"].append({"pos": [random.choice([0, WIDTH]), random.randint(0, HEIGHT)], "type": e_type, "vel": [vx, vy]})

            p_rect = pygame.Rect(state_data["player_pos"][0], state_data["player_pos"][1], 40, 40)
            for it in state_data["items"][:]:
                if p_rect.colliderect(pygame.Rect(it["pos"][0], it["pos"][1], 20, 20)):
                    state_data["gauges"][it["type"]] = min(100, state_data["gauges"][it["type"]] + RECOVERY_AMOUNT)
                    state_data["items"].remove(it)
            for en in state_data["enemies"][:]:
                en["pos"][0] += en["vel"][0]; en["pos"][1] += en["vel"][1]
                if en["pos"][0] < 0 or en["pos"][0] > WIDTH: en["vel"][0] *= -1
                if en["pos"][1] < 0 or en["pos"][1] > HEIGHT: en["vel"][1] *= -1
                en_size = 30 if en["type"] == "c" else 20
                if p_rect.colliderect(pygame.Rect(en["pos"][0], en["pos"][1], en_size, en_size)):
                    dmg = 35 if en["type"] == "c" else VIRUS_DAMAGE
                    for k in state_data["gauges"]: state_data["gauges"][k] -= dmg
                    state_data["enemies"].remove(en)

            draw_player(screen, state_data["player_pos"], get_player_color(state_data["gauges"]), state_data["gauges"])
            for it in state_data["items"]: draw_food(screen, it["pos"], it["type"], it["f_id"])
            for en in state_data["enemies"]: draw_enemy(screen, en["type"], en["pos"], 30 if en["type"]=="c" else 20)
            
            for label, rect in b_list.items():
                pygame.draw.rect(screen, GRAY, rect, 2)
            screen.blit(font_m.render(f"Age: {int(state_data['age'])}", True, WHITE), (20, 20))
            for i, (k, col) in enumerate([("C", C_YELLOW), ("P", P_RED), ("V", V_GREEN)]):
                pygame.draw.rect(screen, GRAY, (WIDTH-160, 20 + i*25, 140, 15))
                bar_w = int(max(0, state_data["gauges"][k]) * 1.4)
                pygame.draw.rect(screen, col, (WIDTH-160, 20 + i*25, bar_w, 15))

        elif state_data["state"] == "RESULT":
            res_txt = "HAPPY 100 YEARS!" if state_data["cleared"] else "GAME OVER"
            screen.blit(font_l.render(res_txt, True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 50))
            screen.blit(font_m.render(f"Final Age: {int(state_data['age'])}", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 + 20))
            screen.blit(font_m.render("Click to Try Again", True, GOLD), (WIDTH//2 - 120, HEIGHT//2 + 80))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
