#%%

# เดี๋ยวมาแก้พวกชื่อตัวแปรหลังจากไฟนอลฟีเจอร์ทุกคนมารวมกัน 
import pygame
import math


WATER_RISE_PIXELS_PER_LETTER = BLOCK_SIZE  # น้ำจะขึ้นตามจำนวนตัวอักษรที่พิมพ์ได้
WATER_ANIM_DURATION = 0.9  # ระยะเวลาเคลื่อนขึ้นของน้ำ
WATER_SURFACE_WAVE_AMPLITUDE = 6
WATER_SURFACE_LENGTH = 140 # ความยาวคลื่นผิวน้ำ

class Water:
    def __init__(self, screen_h):
        self.screen_h = screen_h
        self.level_y = screen_h  # ให้น้ำเริ่มจากล่างสุดจอ
        self.visible = False  # น้ำไม่แสดงตอนเริ่มเกม
 
        self.animating = False # ไม่ได้เคลื่อนที่ตอนเริ่มเกม
        self.start_y = self.level_y 
        self.target_y = self.level_y
        self.anim_time = 0.0  # เวลาเริ่มนับตอนที่น้ำแบบเริ่่มขึ้น
        self.anim_dur = WATER_ANIM_DURATION

    def start_rise(self, rise_pixels):

        if not self.visible:
            self.visible = True
            self.level_y = float(self.level_y)
        self.start_y = float(self.level_y)  # เป็นfloatแล้วขอบพิกเซลมันหาย
        self.target_y = max(0.0, self.start_y - rise_pixels)
        self.anim_time = 0.0
        self.animating = True

    def update(self, dt):
        if self.animating:
            self.anim_time += dt
            t = min(1.0, self.anim_time / self.anim_dur)
   
            t_ease = t * t * (3 - 2 * t) # smoothing easing indian guy said ทำให้objectมันเคลื่อนแบบนุ่ม ๆ
            self.level_y = self.start_y + (self.target_y - self.start_y) * t_ease
            if t >= 1.0:
                self.level_y = self.target_y
                self.animating = False

    def draw(self, surf):
        if not self.visible:
            return
        level = int(self.level_y)
        if level < self.screen_h:

            # วาดน้ำำำำำำำำำำำำ
            rect = pygame.Rect(0, level, WIDTH, self.screen_h - level)
            pygame.draw.rect(surf, WATER_COLOR, rect)
  
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


#การขึ้นของน้ำ ต้องอยู่ในmain แต่ขอแปะไว้ตรงนี้ก่อน
                lens = [max(1, len(w)) for w in submitted_words ] 
                avg_len = sum(lens) / len(lens)
                rise_px = avg_len * WATER_RISE_PIXELS_PER_LETTER
                # start water rising animation
                water.start_rise(rise_px)