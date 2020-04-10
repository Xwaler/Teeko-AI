import math

import pygame

from constants import *
from views import Button


class ColorChanger:
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color

    def drawCircle(self, screen, color):
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.r)
        pygame.draw.circle(screen, color, (self.x, self.y), self.r - 2)

    def changeColor(self, pos):
        if math.sqrt(math.pow((self.x - pos[0]), 2) + math.pow((self.y - pos[1]), 2)) <= self.r:
            return True
        return False


class Menu:
    def __init__(self, surf):
        self.surf = surf

        self.font = pygame.font.Font('Amatic-Bold.ttf', 180)
        self.title = self.font.render('Teeko AI', True, BLACK)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (SCREEN_SIZE[0] / 2, 200)

        self.INDEX_COLOR_ONE = 0
        self.INDEX_COLOR_TWO = 1
        self.index_difficulty = 0

        self.color_btn_one = ColorChanger(int((SCREEN_SIZE[0] - 400) / 2), int((SCREEN_SIZE[1] - 30) / 2 + 30), 30,
                                          COLORS[self.INDEX_COLOR_ONE])
        self.color_btn_two = ColorChanger(int((SCREEN_SIZE[0] - 400) / 2 + 300), int((SCREEN_SIZE[1] - 30) / 2 + 30),
                                          30,
                                          COLORS[self.INDEX_COLOR_TWO])

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)
        self.player_one = self.font.render('Player 1', True, BLACK)
        self.player_one_rect = self.player_one.get_rect()
        self.player_one_rect.center = (int((SCREEN_SIZE[0] - 300) / 2 + 50), (SCREEN_SIZE[1] - 30) / 2 + 30)

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)
        self.player_two = self.font.render('Player 2', True, BLACK)
        self.player_two_rect = self.player_two.get_rect()
        self.player_two_rect.center = (int((SCREEN_SIZE[0] - 300) / 2 + 350), (SCREEN_SIZE[1] - 30) / 2 + 30)

        self.start_btn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 220, 200, 50, 'Start',
                                BACKGROUND)
        self.settings_btn = Button((SCREEN_SIZE[0] - 250) / 2, (SCREEN_SIZE[1] - 50) / 2 + 150, 250, 50,
                                   'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty],
                                   BACKGROUND)
        self.leave_btn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 290, 200, 50, 'Leave',
                                BACKGROUND)

    def parse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.start_btn.on_button(pos):
                return CODE_TO_GAME

            if self.settings_btn.on_button(pos):
                if self.index_difficulty < 2:
                    self.index_difficulty += 1
                else:
                    self.index_difficulty = 0

                self.settings_btn.text = 'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty]

            if self.leave_btn.on_button(pos):
                pygame.quit()
                quit()

            if self.color_btn_one.changeColor(pos):
                if self.INDEX_COLOR_ONE + 1 < len(COLORS):
                    if self.INDEX_COLOR_ONE + 1 != self.INDEX_COLOR_TWO:
                        self.INDEX_COLOR_ONE += 1
                    else:
                        self.INDEX_COLOR_ONE += 2
                else:
                    if self.INDEX_COLOR_TWO == 0:
                        self.INDEX_COLOR_ONE = 1
                    else:
                        self.INDEX_COLOR_ONE = 0
            if self.color_btn_two.changeColor(pos):
                if self.INDEX_COLOR_TWO + 1 < len(COLORS):
                    if self.INDEX_COLOR_TWO + 1 != self.INDEX_COLOR_ONE:
                        self.INDEX_COLOR_TWO += 1
                    else:
                        self.INDEX_COLOR_TWO += 2
                else:
                    if self.INDEX_COLOR_ONE == 0:
                        self.INDEX_COLOR_TWO = 1
                    else:
                        self.INDEX_COLOR_TWO = 0

    def render(self):
        self.surf.fill(BACKGROUND)
        if self.start_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.start_btn.hover(self.surf)
        else:
            self.start_btn.drawRect(self.surf)

        if self.settings_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.settings_btn.hover(self.surf)
        else:
            self.settings_btn.drawRect(self.surf)

        if self.leave_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.leave_btn.hover(self.surf)
        else:
            self.leave_btn.drawRect(self.surf)

        self.color_btn_one.drawCircle(self.surf, COLORS[self.INDEX_COLOR_ONE])
        self.color_btn_two.drawCircle(self.surf, COLORS[self.INDEX_COLOR_TWO])

        self.surf.blit(self.title, self.title_rect)
        self.surf.blit(self.player_one, self.player_one_rect)
        self.surf.blit(self.player_two, self.player_two_rect)
