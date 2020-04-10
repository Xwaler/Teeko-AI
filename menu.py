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
        self.title_rect.center = (SCREEN_SIZE[0] / 2, 180)

        self.index_difficulty_one = 0
        self.index_difficulty_two = 0

        self.color_btn_one = ColorChanger(int((SCREEN_SIZE[0] - 700) / 2), int((SCREEN_SIZE[1] - 30) / 2 + 30), 30,
                                          COLORS[self.INDEX_COLOR_ONE])
        self.color_btn_two = ColorChanger(int((SCREEN_SIZE[0] - 700) / 2 + 550), int((SCREEN_SIZE[1] - 30) / 2 + 30),
                                          30,
                                          COLORS[self.INDEX_COLOR_TWO])

        self.tick_zone_one = Button((SCREEN_SIZE[0] - 700) / 2 , (SCREEN_SIZE[1] - 30) / 2 + 100, 150, 50,
                                   PLAYERTYPE[self.player_one_type],
                                   BACKGROUND)

        self.tick_zone_two = Button((SCREEN_SIZE[0] - 700) / 2 + 550, (SCREEN_SIZE[1] - 30) / 2 + 100, 150, 50,
                                  PLAYERTYPE[self.player_two_type],
                                  BACKGROUND)

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)
        self.player_one = self.font.render('Player 1', True, BLACK)
        self.player_one_rect = self.player_one.get_rect()
        self.player_one_rect.center = (int((SCREEN_SIZE[0] - 500) / 2), (SCREEN_SIZE[1] - 30) / 2 + 30)

        self.player_two = self.font.render('Player 2', True, BLACK)
        self.player_two_rect = self.player_two.get_rect()
        self.player_two_rect.center = (int((SCREEN_SIZE[0] - 300) / 2 + 450), (SCREEN_SIZE[1] - 30) / 2 + 30)

        self.start_btn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 230, 200, 50, 'Start',
                                BACKGROUND)
        self.AI_diff_one = Button((SCREEN_SIZE[0] - 700) / 2 - 50, (SCREEN_SIZE[1] - 30) / 2 + 170, 250, 50,
                                   'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty_one],
                                   BACKGROUND)
        self.AI_diff_one.disable()

        self.AI_diff_two = Button((SCREEN_SIZE[0] - 700) / 2 + 500, (SCREEN_SIZE[1] - 30) / 2 + 170, 250, 50,
                                  'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty_two],
                                  BACKGROUND)
        self.AI_diff_two.disable()

        self.leave_btn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 300, 200, 50, 'Leave',
                                BACKGROUND)

        self.playerone = Player(1,0, 0)
        self.playertwo = Player(2,0, 1)

    def parse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.start_btn.on_button(pos):
                return CODE_TO_GAME

            if self.AI_diff_one.on_button(pos) and not self.AI_diff_one.isDisable():
                if self.index_difficulty_one < 2:
                    self.index_difficulty_one += 1
                else:
                    self.index_difficulty_one = 0

                self.AI_diff_one.text = 'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty_one]

            if self.AI_diff_two.on_button(pos) and not self.AI_diff_two.isDisable():
                if self.index_difficulty_two < 2:
                    self.index_difficulty_two += 1
                else:
                    self.index_difficulty_two = 0

                self.AI_diff_two.text = 'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty_two]

            if self.tick_zone_one.on_button(pos):
                if self.player_one.type < 2:
                    self.player_one.type += 1
                    self.AI_diff_one.able()
                else:
                    self.player_one.type = 0
                    self.AI_diff_one.disable()

                self.tick_zone_one.text = PLAYERTYPE[self.player_one.type]

            if self.tick_zone_two.on_button(pos):
                if self.player_two.type<2:
                    self.player_two.type +=1
                    self.AI_diff_two.able()
                else:
                    self.player_two.type = 0
                    self.AI_diff_two.disable()

                self.tick_zone_two.text = PLAYERTYPE[self.player_two.type]

            if self.leave_btn.on_button(pos):
                pygame.quit()
                quit()

            if self.color_btn_one.changeColor(pos):
                if self.player_one.colorindex + 1 < len(COLORS):
                    if self.player_one.colorindex + 1 != self.player_two.colorindex:
                        self.player_one.colorindex += 1
                    else:
                        self.player_one.colorindex += 2
                else:
                    if self.player_two.colorindex == 0:
                        self.player_one.colorindex = 1
                    else:
                        self.player_one.colorindex = 0

            if self.color_btn_two.changeColor(pos):
                if self.player_two.colorindex + 1 < len(COLORS):
                    if self.player_two.colorindex + 1 != self.player_one.colorindex:
                        self.player_two.colorindex += 1
                    else:
                        self.player_two.colorindex += 2
                else:
                    if self.player_one.colorindex == 0:
                        self.player_two.colorindex = 1
                    else:
                        self.player_two.colorindex = 0

    def render(self):
        self.surf.fill(BACKGROUND)
        if self.start_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.start_btn.hover(self.surf)
        else:
            self.start_btn.drawRect(self.surf)

        if self.AI_diff_one.get_rect().collidepoint(pygame.mouse.get_pos()) and not self.AI_diff_one.isDisable():
            self.AI_diff_one.hover(self.surf)
        else:
            self.AI_diff_one.drawRect(self.surf)

        if self.AI_diff_two.get_rect().collidepoint(pygame.mouse.get_pos()) and not self.AI_diff_two.isDisable():
            self.AI_diff_two.hover(self.surf)
        else:
            self.AI_diff_two.drawRect(self.surf)

        if self.leave_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.leave_btn.hover(self.surf)
        else:
            self.leave_btn.drawRect(self.surf)

        self.tick_zone_one.drawRect(self.surf)
        self.tick_zone_two.drawRect(self.surf)
        self.color_btn_one.drawCircle(self.surf, COLORS[self.INDEX_COLOR_ONE])
        self.color_btn_two.drawCircle(self.surf, COLORS[self.INDEX_COLOR_TWO])

        self.surf.blit(self.title, self.title_rect)
        self.surf.blit(self.player_one, self.player_one_rect)
        self.surf.blit(self.player_two, self.player_two_rect)
