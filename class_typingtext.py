# -*- coding: utf-8 -*-
import pygame

class typingText:
    def __init__(self, screen, font, question, valid_answers):
        self.screen = screen
        self.font = font
        self.question = question
        self.valid_answers = set(ans.lower() for ans in valid_answers)
        self.user_input = ""
        self.answer_valid = False

    def handle_event(self, event): # Typing function
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.answer_valid = self.check_answer() # Choice API or txt file
            else:
                char = event.unicode
                if char.isprintable():
                    self.user_input += char

    def check_answer(self): #Vocal checker
        return self.user_input.lower() in self.valid_answers

    def get_answer_length(self): #Count letter
        return len(self.user_input)

    def draw(self): #Limited lette draw
        self.screen.fill((0, 0, 0))

        question_surf = self.font.render(f"Question: {self.question}", True, (255, 255, 255))
        input_surf = self.font.render(f"Your answer: {self.user_input}", True, (255, 255, 0))
        self.screen.blit(question_surf, (20, 20))
        self.screen.blit(input_surf, (20, 60))

        if self.answer_valid:
            result_text = f"Correct! Length: {self.get_answer_length()}"
            result_color = (0, 255, 0)
        else:
            result_text = "Wrong spelling"
            result_color = (255, 255, 255)

        result_surf = self.font.render(result_text, True, result_color)
        self.screen.blit(result_surf, (20, 100))
