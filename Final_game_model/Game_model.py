import pygame
import random
import math

pygame.init()


def load_word_list(filename):
    words = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if w:
                    words.append(w)
    except FileNotFoundError:
        print(f"Warning: {filename} not found, using empty list.")
    return words


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Text or Die")


WHITE = (255, 255, 255)
BLACK = (10, 12, 24)
BLUE = (30, 70, 200, 200)
LIGHT_BLUE = (100, 180, 255)
GREY = (180, 180, 180)
RED = (255, 80, 80)
GREEN = (80, 255, 120)
YELLOW = (255, 255, 120)

FONT = pygame.font.SysFont("arial", 28)
BIG = pygame.font.SysFont("arial", 56)
clock = pygame.time.Clock()
questions = {
    "Name a fruit": load_word_list("fruits.txt"),
    "Name a country": load_word_list("countries.txt"),
    "Name an animal": load_word_list("animals.txt")
}

pygame.mixer.init()
pygame.mixer.music.load("music.mp3") 
pygame.mixer.music.play(-1,0.0)

# ขนาดบล็อกกกกกกก
block_width = 50
block_height = 30


class Block:
    def __init__(self, x, y, letter, color=GREY):
        self.x = x
        self.y = y
        self.letter = letter.upper()
        self.width = block_width
        self.height = block_height
        self.color = color

    def draw(self, screen, camera_y):
        rect = pygame.Rect(self.x, self.y - camera_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2)
        text = FONT.render(self.letter, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)


class Water:
    def __init__(self, screen_h, start_level=None, anim_dur=0.9, color=BLUE):
        self.screen_h = screen_h
        self.level = float(start_level if start_level is not None else screen_h)  # world y

        self.start_y = self.level
        self.target_y = self.level
        self.anim_time = 0.0
        self.anim_dur = anim_dur
        self.animating = False
        self.color = color

        self.word_lengths = []

    def rise(self, amount_px):
        if amount_px <= 0:
            return

        self.start_y = float(self.level)

        self.target_y = self.start_y - float(amount_px)
        self.anim_time = 0.0
        self.animating = True


    def update(self, dt):
        if not self.animating:
            return
        self.anim_time += dt
        t = min(1.0, self.anim_time / self.anim_dur)
        # smoothstep easing
        t_ease = t * t * (3 - 2 * t)
        self.level = self.start_y + (self.target_y - self.start_y) * t_ease
        if t >= 1.0:
            self.level = self.target_y
            self.animating = False

    def draw(self, surface, camera_y=0):

        screen_y = int(self.level - camera_y)
        height = max(0, self.screen_h - screen_y)
        if height <= 0:
            return

        # เปลี่ยนน้ำเป็นแบบพื้นเรียบนะค๊ะพี่
        water_surf = pygame.Surface((WIDTH, height), pygame.SRCALPHA)
        if len(self.color) == 3:
            fill_color = (*self.color, 200)
        else:
            fill_color = self.color
        water_surf.fill(fill_color)
        surface.blit(water_surf, (0, screen_y))

        # เส้นคลื่นหลัง
        t = pygame.time.get_ticks() / 1000.0
        points_back = []
        amp_back = 14
        wave_len_back = 150
        speed_back = 2.0
        for x in range(0, WIDTH + 8, 8):
            y = screen_y + math.sin((x / wave_len_back) + t * speed_back) * amp_back
            points_back.append((x, y))
        if len(points_back) > 1:
            pygame.draw.lines(surface, (120, 180, 255), False, points_back, 2)

        # เส้นคลื่นหน้า
        points_front = []
        amp_front = 16
        wave_len_front = 240
        speed_front = 2.0
        for x in range(0, WIDTH + 6, 6):
            y = screen_y + math.sin((x / wave_len_front) + t * speed_front) * amp_front - 2
            points_front.append((x, y))
        if len(points_front) > 1:
            pygame.draw.lines(surface, (180, 220, 255), False, points_front, 2)


        hl_points = []
        for x in range(0, WIDTH + 6, 12):
            y = screen_y + math.sin((x / 60.0) + t * 2.0) * 2.0 - 6
            hl_points.append((x, y))
        if len(hl_points) > 1:
            s = pygame.Surface((WIDTH, 24), pygame.SRCALPHA)
            pygame.draw.lines(
                s,
                (255, 255, 255, 60),
                False,
                [(p[0], p[1] - screen_y + 6) for p in hl_points],
                3
            )
            surface.blit(s, (0, screen_y - 12))

    def is_animating(self):
                return self.animating

    def reset(self, start_level=None):
            start = start_level if start_level is not None else self.screen_h
            self.level = float(start)
            self.start_y = self.level
            self.target_y = self.level
            self.anim_time = 0.0
            self.animating = False
            self.word_lengths = []



blocks = []


def add_word_blocks(word):
    word = word.strip()
    if word == "":
        return
    if len(blocks) == 0:
        base_top_y = HEIGHT - 130 - block_height
    else:
        current_top = min(b.y for b in blocks)
        base_top_y = current_top - block_height
    x_center = WIDTH // 2 - block_width // 2
    for i, ch in enumerate(word):
        y = base_top_y - i * block_height
        blocks.append(Block(x_center, y, ch))


def draw_text(surface, text, font, color, x, y):
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))
def draw_text_box(surface, text, font, text_color, box_color, x, y, padding=6):
    txt = font.render(text, True, text_color)
    rect = txt.get_rect(topleft=(x, y))

    # background box (transparent)
    box_rect = pygame.Rect(rect.x - padding, rect.y - padding,
                           rect.width + padding * 2, rect.height + padding * 2)

    pygame.draw.rect(surface, box_color, box_rect, border_radius=6)
    surface.blit(txt, rect)




def main():
    running = True
    input_text = ""

    
    chosen_category = random.choice(list(questions.keys()))
    current_question = questions[chosen_category]

    camera_y = 0
    camera_target_y = 0

    water = Water(screen_h=HEIGHT, start_level=HEIGHT - 100, anim_dur=0.9)
    WATER_RISE_PIXELS_PER_LETTER = block_height

    round_number = 1
    PERCENT_START = 0.50
    PERCENT_STEP = 0.10

    score = 0
    game_over = False

    submitted_words = set() 

    info_text = ""
    info_time = 0.0
    INFO_DURATION = 2.0

    while running:
        dt = clock.tick(60) / 1000.0

        if info_text and (pygame.time.get_ticks() / 1000.0 - info_time) > INFO_DURATION:
            info_text = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_RETURN:
                        submitted_word = input_text.strip().lower()
                        if submitted_word != "":

                            if submitted_word in submitted_words:
                                info_text = "Already used!"
                                info_time = pygame.time.get_ticks() / 1000.0

                                percent = PERCENT_START + PERCENT_STEP * (round_number - 1)
                                
                                if len(water.word_lengths) > 0:
                                    avg_len = sum(water.word_lengths) / len(water.word_lengths)
                                else:
                                    avg_len = len(submitted_word)
                                water_rise_letters = avg_len * percent
                                if water_rise_letters > 0:
                                    rise_px = water_rise_letters * WATER_RISE_PIXELS_PER_LETTER
                                    water.rise(rise_px)
                                round_number += 1

                            else:
                                
                                if submitted_word in current_question:
                                    submitted_words.add(submitted_word)
                                    add_word_blocks(submitted_word)
                                    score += len(submitted_word) * 10

                                   
                                    water.word_lengths.append(len(submitted_word))

                                    percent = PERCENT_START + PERCENT_STEP * (round_number - 1)
                                    avg_len = sum(water.word_lengths) / len(water.word_lengths)
                                    water_rise_letters = avg_len * percent
                                    if water_rise_letters > 0:
                                        rise_px = water_rise_letters * WATER_RISE_PIXELS_PER_LETTER
                                        water.rise(rise_px)

                                    round_number += 1

                                    info_text = "Correct!"
                                    info_time = pygame.time.get_ticks() / 1000.0

                                    
                                else:
                                    info_text = "Wrong!"
                                    info_time = pygame.time.get_ticks() / 1000.0

                                    if round_number == 1:
                                        game_over = True
                                    else:
                                        percent = PERCENT_START + PERCENT_STEP * (round_number - 1)
                                        if len(water.word_lengths) > 0:
                                            avg_len = sum(water.word_lengths) / len(water.word_lengths)
                                        else:
                                            avg_len = len(submitted_word)
                                        water_rise_letters = avg_len * percent
                                        if water_rise_letters > 0:
                                            rise_px = water_rise_letters * WATER_RISE_PIXELS_PER_LETTER
                                            water.rise(rise_px)
                                        round_number += 1

                        input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            input_text += event.unicode
                else:
                    if event.key == pygame.K_r:
                        blocks.clear()
                        input_text = ""
                        chosen_category = random.choice(list(questions.keys()))
                        current_question = questions[chosen_category]
                        water.reset(start_level=HEIGHT - 100)
                        round_number = 1
                        score = 0
                        camera_y = 0
                        camera_target_y = 0
                        game_over = False
                        submitted_words.clear()
                        info_text = ""
                        info_time = 0.0

    
        water.update(dt)

     # ให้กล้องมันตามบล็อกไปปปปปป
        if len(blocks) > 0:
            top_block_y = min(block.y for block in blocks)
            bottom_block_y = max(block.y for block in blocks)
            tower_top_in_view = top_block_y - camera_y
            tower_bottom_in_view = bottom_block_y - camera_y

            if tower_top_in_view < HEIGHT / 4:
                camera_target_y = top_block_y - HEIGHT / 4
            elif tower_bottom_in_view > HEIGHT * 3 / 4:
                camera_target_y = bottom_block_y - HEIGHT * 3 / 4
        else:
            camera_target_y = 0

        camera_y += (camera_target_y - camera_y) * 0.12

        if len(blocks) > 0:
            top_block_y = min(block.y for block in blocks)
            if water.level <= top_block_y:
                game_over = True


        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        for block in blocks:
            block.draw(screen, camera_y)
        water.draw(screen, camera_y)

        # แก้เติมพื้นหลังกล่องอินพุตละ 
        input_box = pygame.Rect(20, 20, 760, 50)
        input_bg = pygame.Surface((input_box.width, input_box.height), pygame.SRCALPHA)
        input_bg.fill((255, 255, 255, 100))
        screen.blit(input_bg, (input_box.x, input_box.y))
        pygame.draw.rect(screen, WHITE, input_box, 2)

        avg_display = 0.0
        if len(water.word_lengths) > 0:
            avg_display = sum(water.word_lengths) / len(water.word_lengths)

        BOX_COLOR = (255, 255, 255, 200)
        draw_text_box(screen, f"Category: {chosen_category}", FONT, BLACK, BOX_COLOR, 20, 80)
        draw_text_box(screen, f"Score: {score}", FONT, GREEN, BOX_COLOR, WIDTH - 200, 100)
        draw_text_box(screen, f"Round: {round_number}", FONT, LIGHT_BLUE, BOX_COLOR, WIDTH - 200, 150)
        draw_text(screen, input_text, FONT, BLUE, input_box.x + 10, input_box.y + 10)


        if info_text:
            color = YELLOW
            if info_text.lower().startswith("wrong") or info_text.lower().startswith("already"):
                color = RED
            draw_text(screen, info_text, FONT, color, 20, 130)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER!", BIG, RED, WIDTH // 2 - 140, HEIGHT // 3)
            draw_text(screen, f"Final Score: {score}", FONT, WHITE, WIDTH // 2 - 120, HEIGHT // 2)
            draw_text(screen, "Press R to Restart", FONT, LIGHT_BLUE, WIDTH // 2 - 150, HEIGHT // 2 + 50)

        pygame.display.flip()



    pygame.quit()


try:
    background = pygame.image.load("Bg1.png").convert()

    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except Exception as e:
    print("Warning: background 1.png not found or failed to load:", e)
    background = None

if __name__ == "__main__":
    main()
