import pygame
import asyncio
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nutrition Survival 100")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
C_YELLOW = (255, 255, 0)
P_RED = (255, 50, 50)
V_GREEN = (50, 255, 50)
GRAY = (100, 100, 100)
PURPLE = (150, 0, 255)
MAGENTA = (255, 0, 255)

FPS = 60
PLAYER_SPEED = 5
AGE_LIMIT = 100 
GAUGE_DECREASE_BASE = 0.12

def reset_game():
    return {
        "player_pos": [WIDTH // 2, HEIGHT // 2],
        "items": [], 
        "enemies": [], 
        "age": 0,
        "gauges": {"C": 100.0, "P": 100.0, "V": 100.0},
        "game_over": False,
        "cleared": False
    }

def get_player_color(gauges):
    min_val = min(gauges.values())
    if min_val >= 80: return (255, 105, 180)
    if min_val >= 50: return (255, 255, 0)
    if min_val >= 20: return (144, 238, 144)
    return (100, 100, 255)

async def main():
    state = reset_game()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("sans-serif", 32)
    big_font = pygame.font.SysFont("sans-serif", 64)

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if (state["game_over"] or state["cleared"]) and event.type == pygame.MOUSEBUTTONDOWN:
                state = reset_game()

        if not state["game_over"] and not state["cleared"]:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and state["player_pos"][0] > 0: state["player_pos"][0] -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and state["player_pos"][0] < WIDTH - 40: state["player_pos"][0] += PLAYER_SPEED
            if keys[pygame.K_UP] and state["player_pos"][1] > 0: state["player_pos"][1] -= PLAYER_SPEED
            if keys[pygame.K_DOWN] and state["player_pos"][1] < HEIGHT - 40: state["player_pos"][1] += PLAYER_SPEED

            diff = 1.0 + (state["age"] / 100)
            for k in state["gauges"]:
                state["gauges"][k] -= GAUGE_DECREASE_BASE * diff
                if state["gauges"][k] <= 0:
                    state["game_over"] = True

            state["age"] += 1/FPS 
            if state["age"] >= AGE_LIMIT: state["cleared"] = True

            if random.random() < 0.06:
                state["items"].append({"pos": [random.randint(20, WIDTH-20), random.randint(20, HEIGHT-20)], "type": random.choice(["C", "P", "V"])})
            
            if random.random() < 0.008:
                state["enemies"].append({"pos": [random.choice([0, WIDTH]), random.randint(0, HEIGHT)], "type": "v", "vel": [random.choice([-3, 3]), random.choice([-3, 3])]})
            
            if state["age"] > 40 and random.random() < 0.005:
                state["enemies"].append({"pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)], "type": "c", "vel": [random.choice([-1, 1]), random.choice([-1, 1])]})

            p_rect = pygame.Rect(state["player_pos"][0], state["player_pos"][1], 40, 40)
            for it in state["items"][:]:
                if p_rect.colliderect(pygame.Rect(it["pos"][0], it["pos"][1], 20, 20)):
                    state["gauges"][it["type"]] = min(100, state["gauges"][it["type"]] + 20)
                    state["items"].remove(it)

            for en in state["enemies"][:]:
                en["pos"][0] += en["vel"][0]
                en["pos"][1] += en["vel"][1]
                if en["pos"][0] < 0 or en["pos"][0] > WIDTH: en["vel"][0] *= -1
                if en["pos"][1] < 0 or en["pos"][1] > HEIGHT: en["vel"][1] *= -1
                if p_rect.colliderect(pygame.Rect(en["pos"][0], en["pos"][1], 20, 20)):
                    for k in state["gauges"]: state["gauges"][k] -= 15
                    state["enemies"].remove(en)

            p_color = get_player_color(state["gauges"])
            pygame.draw.rect(screen, p_color, p_rect) 
            for it in state["items"]:
                color = C_YELLOW if it["type"]=="C" else P_RED if it["type"]=="P" else V_GREEN
                pygame.draw.circle(screen, color, (int(it["pos"][0]+10), int(it["pos"][1]+10)), 10)
            for en in state["enemies"]:
                ecol = PURPLE if en["type"] == "v" else MAGENTA
                pygame.draw.rect(screen, ecol, (en["pos"][0], en["pos"][1], 20, 20))

            screen.blit(font.render(f"Age: {int(state['age'])}", True, WHITE), (20, 20))
            for i, (k, col) in enumerate([("C", C_YELLOW), ("P", P_RED), ("V", V_GREEN)]):
                pygame.draw.rect(screen, GRAY, (WIDTH-160, 20 + i*25, 140, 15))
                pygame.draw.rect(screen, col, (WIDTH-160, 20 + i*25, int(max(0, state["gauges"][k]) * 1.4), 15))

        else:
            title = "HAPPY 100!" if state["cleared"] else "GAME OVER"
            screen.blit(big_font.render(title, True, WHITE), (WIDTH//2 - 150, HEIGHT//2 - 50))
            screen.blit(font.render("Click to Restart", True, WHITE), (WIDTH//2 - 100, HEIGHT//2 + 50))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
    
