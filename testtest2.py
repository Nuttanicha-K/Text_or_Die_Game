#%%
import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 500
FPS = 60

BLOCK_SIZE = 28  # หนึ่งบล็อกสูงกี่พิกเซล
WATER_RISE_PIXELS_PER_LETTER = BLOCK_SIZE  # น้ำขึ้นกี่พิกเซลต่อ 1 ตัวอักษรเฉลี่ย
WATER_ANIM_DURATION = 0.9
WATER_SURFACE_WAVE_AMPLITUDE = 6
WATER_SURFACE_LENGTH = 140
WATER_COLOR = (0, 100, 255)
SURFACE_HIGHLIGHT = (100, 150, 255)

BG = (30, 40, 60)
TEXT_COLOR = (255, 255, 255)

# ----- Pygame setup -----
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Text or Die - Minimal")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 36)


# ----- Classes -----


class Water:
    """
    Controls water level, animation, and cumulative average rise:
    - word_lengths: list of lengths seen so far
    - add_word(length): append and start rise by average*WATER_RISE_PIXELS_PER_LETTER
    """

    def __init__(self, screen_h):
        self.screen_h = screen_h
        self.level_y = screen_h  # start hidden (level at bottom)
        self.visible = False

        # animation state
        self.animating = False
        self.start_y = self.level_y
        self.target_y = self.level_y
        self.anim_time = 0.0
        self.anim_dur = WATER_ANIM_DURATION

        # cumulative words data
        self.word_lengths = []

    def add_word(self, word_length: int):
        """Record a new word length and start the rise based on the average."""
        self.word_lengths.append(max(1, int(word_length)))  # at least 1
        avg_len = sum(self.word_lengths) / len(self.word_lengths)
        rise_px = avg_len * WATER_RISE_PIXELS_PER_LETTER
        self.start_rise(rise_px)

    def start_rise(self, rise_pixels):
        # make visible and animate upward
        if not self.visible:
            self.visible = True
            self.level_y = float(self.level_y)
        self.start_y = float(self.level_y)
        self.target_y = max(0.0, self.start_y - rise_pixels)
        self.anim_time = 0.0
        self.animating = True

    def update(self, dt):
        if self.animating:
            self.anim_time += dt
            t = min(1.0, self.anim_time / self.anim_dur)
            # smoothstep easing
            t_ease = t * t * (3 - 2 * t)
            self.level_y = self.start_y + (self.target_y - self.start_y) * t_ease
            if t >= 1.0:
                self.level_y = self.target_y
                self.animating = False

    def draw(self, surf):
        if not self.visible:
            return
        level = int(self.level_y)
        if level < self.screen_h:
            rect = pygame.Rect(0, level, WIDTH, self.screen_h - level)
            pygame.draw.rect(surf, WATER_COLOR, rect)

            # wave highlight
            points = []
            t = pygame.time.get_ticks() / 1000.0
            amp = WATER_SURFACE_WAVE_AMPLITUDE
            length = WATER_SURFACE_LENGTH
            for x in range(0, WIDTH + 8, 8):
                y = level + math.sin((x / length) + t * 1.5) * amp
                points.append((x, y))
            if points:
                poly = [(0, level - 24)] + points + [(WIDTH, level - 24)]
                pygame.draw.polygon(surf, SURFACE_HIGHLIGHT, poly)

    def is_animating(self):
        return self.animating

    def reset(self):
        self.__init__(self.screen_h)


class typingText:

    def __init__(self, screen, font, question, valid_answers):
        self.screen = screen
        self.font = font
        self.question = question
        self.valid_answers = set(ans.lower() for ans in valid_answers)
        self.user_input = ""
        self.answer_valid = False
        self.submitted = False  # True when Enter pressed (not yet consumed)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # mark submitted; compute validity but don't clear input yet
                self.answer_valid = self.check_answer()
                self.submitted = True
            else:
                char = event.unicode
                if char and char.isprintable():
                    self.user_input += char

    def check_answer(self):
        return self.user_input.lower().strip() in self.valid_answers

    def get_answer_length(self):
        return len(self.user_input.strip())

    def consume_submission(self):
        """
        Called by main loop to check whether a submission occurred.
        Returns (submitted: bool, valid: bool, word: str) and clears internal submitted flag.
        If submitted==False, returns (False, False, "").
        """
        if not self.submitted:
            return False, False, ""
        # consume
        valid = self.answer_valid
        word = self.user_input.strip()
        # reset input after consuming submission (game design choice)
        self.user_input = ""
        self.answer_valid = False
        self.submitted = False
        return True, valid, word

    def draw(self):
        # Draw question and current typed text (this method draws onto self.screen)
        question_surf = self.font.render(f"Question: {self.question}", True, (255, 255, 255))
        input_surf = self.font.render(f"Your answer: {self.user_input}", True, (255, 255, 0))
        self.screen.blit(question_surf, (20, 20))
        self.screen.blit(input_surf, (20, 60))

        # Feedback (shows since last Enter until consume_submission clears it)
        if self.submitted:
            if self.answer_valid:
                result_text = f"Correct! Length: {self.get_answer_length()}"
                result_color = (0, 255, 0)
            else:
                result_text = "Wrong spelling"
                result_color = (255, 100, 100)
            result_surf = self.font.render(result_text, True, result_color)
            self.screen.blit(result_surf, (20, 100))


# ----- Main -----
def main():
    # Setup UI objects
    #ค่อยมาแก้ให้ใส่ไฟล์คำถามแล้วกันอิอิ
    question = "Name a car brand"
    valid_answers = ["ford", "toyota", "bmw", "honda", "audi", "nissan", "tesla", "chevrolet"]
    typer = typingText(screen, font, question, valid_answers)
    water = Water(HEIGHT)

    running = True
    game_over = False
    info_message = ""

    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                typer.handle_event(event)

        # --- Process submission if any ---
        submitted, valid, word = typer.consume_submission()
        if submitted:
            if valid:
                # add word to water (water will compute avg and rise)
                water.add_word(len(word))
                info_message = f"Submitted '{word}' — water will rise (avg of {len(water.word_lengths)} entries)"
            else:
                info_message = f"'{word}' is not a valid answer"

        water.update(dt)
        screen.fill(BG)
        water.draw(screen)
        pygame.draw.rect(screen, (20, 20, 30), (0, 0, WIDTH, 140))
        typer.draw()
        if water.visible:
            lvl = int(water.level_y)
            hud = font.render(f"Water Y: {lvl} px  (words: {len(water.word_lengths)})", True, (220, 220, 220))
        else:
            hud = font.render("Water hidden (no submissions yet)", True, (220, 220, 220))
        screen.blit(hud, (20, 140))
        info_surf = font.render(info_message, True, (240, 240, 160))
        screen.blit(info_surf, (20, 170))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
#%%
import pygame
import math
import sys

pygame.init()

# ----- Config / Constants -----
WIDTH, HEIGHT = 900, 520
FPS = 60

BLOCK_SIZE = 28
WATER_RISE_PIXELS_PER_LETTER = BLOCK_SIZE
WATER_ANIM_DURATION = 0.9
WATER_SURFACE_WAVE_AMPLITUDE = 6
WATER_SURFACE_LENGTH = 140
WATER_COLOR = (0, 100, 255)
SURFACE_HIGHLIGHT = (100, 150, 255)

BG = (30, 40, 60)
UI_BG = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)

# ----- Pygame setup -----
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Text or Die - Single Player")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)


# ----- Classes -----
class Water:
    def __init__(self, screen_h):
        self.screen_h = screen_h
        self.level_y = screen_h
        self.visible = False
        self.animating = False
        self.start_y = self.level_y
        self.target_y = self.level_y
        self.anim_time = 0.0
        self.anim_dur = WATER_ANIM_DURATION
        self.word_lengths = []

    def add_word(self, word_length: int):
        self.word_lengths.append(max(1, int(word_length)))
        avg_len = sum(self.word_lengths) / len(self.word_lengths)
        rise_px = avg_len * WATER_RISE_PIXELS_PER_LETTER
        self.start_rise(rise_px)

    def start_rise(self, rise_pixels):
        if not self.visible:
            self.visible = True
        self.start_y = float(self.level_y)
        self.target_y = max(0.0, self.start_y - rise_pixels)
        self.anim_time = 0.0
        self.animating = True

    def update(self, dt):
        if self.animating:
            self.anim_time += dt
            t = min(1.0, self.anim_time / self.anim_dur)
            # smoothstep easing
            t_ease = t * t * (3 - 2 * t)
            self.level_y = self.start_y + (self.target_y - self.start_y) * t_ease
            if t >= 1.0:
                self.level_y = self.target_y
                self.animating = False

    def draw(self, surf):
        if not self.visible:
            return
        level = int(self.level_y)
        if level < self.screen_h:
            rect = pygame.Rect(0, level, WIDTH, self.screen_h - level)
            pygame.draw.rect(surf, WATER_COLOR, rect)

            # wave highlight
            points = []
            t = pygame.time.get_ticks() / 1000.0
            amp = WATER_SURFACE_WAVE_AMPLITUDE
            length = WATER_SURFACE_LENGTH
            for x in range(0, WIDTH + 8, 8):
                y = level + math.sin((x / length) + t * 1.5) * amp
                points.append((x, y))
            if points:
                poly = [(0, level - 24)] + points + [(WIDTH, level - 24)]
                pygame.draw.polygon(surf, SURFACE_HIGHLIGHT, poly)


class Player:
    def __init__(self, name, x):
        self.name = name
        self.x = x
        self.color = (80, 200, 140)
        self.tower_blocks = 0
        self.last_word = ""
        self.last_len_display_time = 0.0
        self.last_len_duration = 2.0

    @property
    def height_px(self):
        return self.tower_blocks * BLOCK_SIZE

    def add_word(self, word):
        n = max(1, len(word.strip()))
        self.tower_blocks += n
        self.last_word = word.strip()
        self.last_len_display_time = pygame.time.get_ticks() / 1000.0

    def draw(self, surf, base_y):
        # Draw tower
        for i in range(self.tower_blocks):
            block_y = base_y - (i + 1) * BLOCK_SIZE
            rect = pygame.Rect(self.x - BLOCK_SIZE, block_y, BLOCK_SIZE * 2, BLOCK_SIZE)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, (40, 40, 40), rect, 1)

        # Platform and player circle
        platform_y = base_y - self.height_px - BLOCK_SIZE
        platform = pygame.Rect(self.x - BLOCK_SIZE - 10, platform_y, BLOCK_SIZE * 2 + 20, 8)
        pygame.draw.rect(surf, (80, 80, 80), platform)

        cx, cy = self.x, platform_y - 20
        pygame.draw.circle(surf, (250, 220, 120), (cx, cy), 14)
        name_s = font.render(self.name, True, TEXT_COLOR)
        name_rect = name_s.get_rect(center=(cx, cy - 28))
        surf.blit(name_s, name_rect)

        # Display box below player showing last word
        now = pygame.time.get_ticks() / 1000.0
        if self.last_word and (now - self.last_len_display_time) <= self.last_len_duration:
            box_w, box_h = 160, 38
            box_rect = pygame.Rect(cx - box_w // 2, base_y + 10, box_w, box_h)
            pygame.draw.rect(surf, (18, 18, 18), box_rect)
            pygame.draw.rect(surf, (120, 120, 120), box_rect, 2)
            txt1 = font.render(f"Word: {self.last_word}", True, (240, 240, 240))
            txt2 = font.render(f"Len: {len(self.last_word)}", True, (230, 210, 120))
            surf.blit(txt1, (box_rect.x + 8, box_rect.y + 4))
            surf.blit(txt2, (box_rect.x + 8, box_rect.y + 20))


class TypingBox:
    def __init__(self, screen, font, question, valid_answers):
        self.screen = screen
        self.font = font
        self.question = question
        self.valid_answers = set(ans.lower() for ans in valid_answers)
        self.user_input = ""
        self.answer_valid = False
        self.submitted = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.answer_valid = self.check_answer()
                self.submitted = True
            else:
                char = event.unicode
                if char.isprintable():
                    self.user_input += char

    def check_answer(self):
        return self.user_input.lower().strip() in self.valid_answers

    def consume_submission(self):
        if not self.submitted:
            return False, False, ""
        valid = self.answer_valid
        word = self.user_input.strip()
        self.user_input = ""
        self.answer_valid = False
        self.submitted = False
        return True, valid, word

    def draw(self):
        q_s = self.font.render(f"Question: {self.question}", True, (255, 255, 255))
        i_s = self.font.render(f"Your answer: {self.user_input}", True, (255, 255, 0))
        self.screen.blit(q_s, (20, 20))
        self.screen.blit(i_s, (20, 60))


# ----- Main -----
def main():
    base_y = HEIGHT - 110
    player_x = WIDTH // 2
    human = Player("You", player_x)

    question = "Name a car brand"
    valid_answers = ["ford", "toyota", "bmw", "honda", "audi", "nissan", "tesla", "chevrolet"]
    typer = TypingBox(screen, font, question, valid_answers)
    water = Water(HEIGHT)

    running = True
    info_message = ""

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                typer.handle_event(event)

        # Handle player submission
        submitted, valid, word = typer.consume_submission()
        if submitted:
            if valid:
                human.add_word(word)
                water.add_word(len(word))
                info_message = f"You submitted '{word}'"
            else:
                info_message = f"'{word}' is not valid"

        water.update(dt)

        # --- Drawing ---
        screen.fill(BG)
        pygame.draw.rect(screen, UI_BG, (0, 0, WIDTH, 140))
        water.draw(screen)
        human.draw(screen, base_y)
        typer.draw()

        hud = font.render(
            f"Water Y: {int(water.level_y) if water.visible else 'hidden'}  (words: {len(water.word_lengths)})",
            True,
            (220, 220, 220),
        )
        screen.blit(hud, (20, 140))
        info = font.render(info_message, True, (240, 240, 160))
        screen.blit(info, (20, 170))

        pygame.draw.rect(screen, (60, 60, 60), (0, HEIGHT - 80, WIDTH, 80))
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
#%%
import pygame
import math
import sys

pygame.init()

# ----- Config / Constants -----
WIDTH, HEIGHT = 900, 520
FPS = 60

BLOCK_SIZE = 28
WATER_RISE_PIXELS_PER_LETTER = BLOCK_SIZE
WATER_ANIM_DURATION = 0.9
WATER_SURFACE_WAVE_AMPLITUDE = 6
WATER_SURFACE_LENGTH = 140
WATER_COLOR = (0, 100, 255)
SURFACE_HIGHLIGHT = (100, 150, 255)

BG = (30, 40, 60)
UI_BG = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)

# ----- Pygame setup -----
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Text or Die - Single Player")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)


# ----- Classes -----
class Water:
    def __init__(self, screen_h):
        self.screen_h = screen_h
        self.level_y = screen_h
        self.visible = False
        self.animating = False
        self.start_y = self.level_y
        self.target_y = self.level_y
        self.anim_time = 0.0
        self.anim_dur = WATER_ANIM_DURATION
        self.word_lengths = []

    def add_word(self, word_length: int):
        self.word_lengths.append(max(1, int(word_length)))
        avg_len = sum(self.word_lengths) / len(self.word_lengths)
        rise_px = avg_len * WATER_RISE_PIXELS_PER_LETTER
        self.start_rise(rise_px)

    def start_rise(self, rise_pixels):
        if not self.visible:
            self.visible = True
        self.start_y = float(self.level_y)
        self.target_y = max(0.0, self.start_y - rise_pixels)
        self.anim_time = 0.0
        self.animating = True

    def update(self, dt):
        if self.animating:
            self.anim_time += dt
            t = min(1.0, self.anim_time / self.anim_dur)
            # smoothstep easing
            t_ease = t * t * (3 - 2 * t)
            self.level_y = self.start_y + (self.target_y - self.start_y) * t_ease
            if t >= 1.0:
                self.level_y = self.target_y
                self.animating = False

    def draw(self, surf):
        if not self.visible:
            return
        level = int(self.level_y)
        if level < self.screen_h:
            rect = pygame.Rect(0, level, WIDTH, self.screen_h - level)
            pygame.draw.rect(surf, WATER_COLOR, rect)

            # wave highlight
            points = []
            t = pygame.time.get_ticks() / 1000.0
            amp = WATER_SURFACE_WAVE_AMPLITUDE
            length = WATER_SURFACE_LENGTH
            for x in range(0, WIDTH + 8, 8):
                y = level + math.sin((x / length) + t * 1.5) * amp
                points.append((x, y))
            if points:
                poly = [(0, level - 24)] + points + [(WIDTH, level - 24)]
                pygame.draw.polygon(surf, SURFACE_HIGHLIGHT, poly)


class Player:
    def __init__(self, name, x):
        self.name = name
        self.x = x
        self.color = (80, 200, 140)
        self.tower_blocks = 0
        self.last_word = ""
        self.last_len_display_time = 0.0
        self.last_len_duration = 2.0

    @property
    def height_px(self):
        return self.tower_blocks * BLOCK_SIZE

    def add_word(self, word):
        n = max(1, len(word.strip()))
        self.tower_blocks += n
        self.last_word = word.strip()
        self.last_len_display_time = pygame.time.get_ticks() / 1000.0

    def draw(self, surf, base_y):
        # Draw tower
        for i in range(self.tower_blocks):
            block_y = base_y - (i + 1) * BLOCK_SIZE
            rect = pygame.Rect(self.x - BLOCK_SIZE, block_y, BLOCK_SIZE * 2, BLOCK_SIZE)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, (40, 40, 40), rect, 1)

        # Platform and player circle
        platform_y = base_y - self.height_px - BLOCK_SIZE
        platform = pygame.Rect(self.x - BLOCK_SIZE - 10, platform_y, BLOCK_SIZE * 2 + 20, 8)
        pygame.draw.rect(surf, (80, 80, 80), platform)

        cx, cy = self.x, platform_y - 20
        pygame.draw.circle(surf, (250, 220, 120), (cx, cy), 14)
        name_s = font.render(self.name, True, TEXT_COLOR)
        name_rect = name_s.get_rect(center=(cx, cy - 28))
        surf.blit(name_s, name_rect)

        # Display box below player showing last word
        now = pygame.time.get_ticks() / 1000.0
        if self.last_word and (now - self.last_len_display_time) <= self.last_len_duration:
            box_w, box_h = 160, 38
            box_rect = pygame.Rect(cx - box_w // 2, base_y + 10, box_w, box_h)
            pygame.draw.rect(surf, (18, 18, 18), box_rect)
            pygame.draw.rect(surf, (120, 120, 120), box_rect, 2)
            txt1 = font.render(f"Word: {self.last_word}", True, (240, 240, 240))
            txt2 = font.render(f"Len: {len(self.last_word)}", True, (230, 210, 120))
            surf.blit(txt1, (box_rect.x + 8, box_rect.y + 4))
            surf.blit(txt2, (box_rect.x + 8, box_rect.y + 20))


class TypingBox:
    def __init__(self, screen, font, question, valid_answers):
        self.screen = screen
        self.font = font
        self.question = question
        self.valid_answers = set(ans.lower() for ans in valid_answers)
        self.user_input = ""
        self.answer_valid = False
        self.submitted = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.answer_valid = self.check_answer()
                self.submitted = True
            else:
                char = event.unicode
                if char.isprintable():
                    self.user_input += char

    def check_answer(self):
        return self.user_input.lower().strip() in self.valid_answers

    def consume_submission(self):
        if not self.submitted:
            return False, False, ""
        valid = self.answer_valid
        word = self.user_input.strip()
        self.user_input = ""
        self.answer_valid = False
        self.submitted = False
        return True, valid, word

    def draw(self):
        q_s = self.font.render(f"Question: {self.question}", True, (255, 255, 255))
        i_s = self.font.render(f"Your answer: {self.user_input}", True, (255, 255, 0))
        self.screen.blit(q_s, (20, 20))
        self.screen.blit(i_s, (20, 60))


# ----- Main -----
def main():
    base_y = HEIGHT - 110
    player_x = WIDTH // 2
    human = Player("You", player_x)

    question = "Name a car brand"
    valid_answers = ["ford", "toyota", "bmw", "honda", "audi", "nissan", "tesla", "chevrolet"]
    typer = TypingBox(screen, font, question, valid_answers)
    water = Water(HEIGHT)

    running = True
    info_message = ""

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                typer.handle_event(event)

        # Handle player submission
        submitted, valid, word = typer.consume_submission()
        if submitted:
            if valid:
                human.add_word(word)
                water.add_word(len(word))
                info_message = f"You submitted '{word}'"
            else:
                info_message = f"'{word}' is not valid"

        water.update(dt)

        # --- Drawing ---
        screen.fill(BG)
        pygame.draw.rect(screen, UI_BG, (0, 0, WIDTH, 140))
        water.draw(screen)
        human.draw(screen, base_y)
        typer.draw()

        hud = font.render(
            f"Water Y: {int(water.level_y) if water.visible else 'hidden'}  (words: {len(water.word_lengths)})",
            True,
            (220, 220, 220),
        )
        screen.blit(hud, (20, 140))
        info = font.render(info_message, True, (240, 240, 160))
        screen.blit(info, (20, 170))

        pygame.draw.rect(screen, (60, 60, 60), (0, HEIGHT - 80, WIDTH, 80))
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
#%%