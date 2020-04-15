import math

import pygame

from constants import *
from env import Player
from views import Button


class ColorChanger:
    def __init__(self, screen, x, y, r, color):
        self.surf = screen
        self.x = x
        self.y = y
        self.r = r
        self.color = color

    def drawCircle(self, color):
        pygame.draw.circle(self.surf, BLACK, (self.x, self.y), self.r)
        pygame.draw.circle(self.surf, color, (self.x, self.y), self.r - 2)

    def is_inside(self, pos):
        if math.sqrt(math.pow((self.x - pos[0]), 2) + math.pow((self.y - pos[1]), 2)) <= self.r:
            return True
        return False

    def hover(self, color):
        pygame.draw.circle(self.surf, BLACK, (self.x, self.y), self.r)
        pygame.draw.circle(self.surf, color, (self.x, self.y), self.r - 4)


class Menu:
    def __init__(self, surf):
        self.surf = surf

        self.font = pygame.font.Font('Amatic-Bold.ttf', 180)
        self.title = self.font.render('Teeko AI', True, BLACK)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (SCREEN_SIZE[0] / 2, 180)

        self.index_difficulty_one = 1
        self.index_difficulty_two = 1

        self.playerone = Player(1, 0, 0)
        self.playertwo = Player(2, 1, 1)

        self.color_btn_one = ColorChanger(self.surf, int((SCREEN_SIZE[0] - 700) / 2),
                                          int((SCREEN_SIZE[1] - 30) / 2 + 30), 30,
                                          COLORS[self.playerone.color_index])
        self.color_btn_two = ColorChanger(self.surf, int((SCREEN_SIZE[0] - 700) / 2 + 550),
                                          int((SCREEN_SIZE[1] - 30) / 2 + 30),
                                          30,
                                          COLORS[self.playertwo.color_index])

        self.tick_zone_one = Button((SCREEN_SIZE[0] - 700) / 2, (SCREEN_SIZE[1] - 30) / 2 + 100, 150, 50,
                                    PLAYERTYPE[self.playerone.ptype],
                                    BACKGROUND)

        self.tick_zone_two = Button((SCREEN_SIZE[0] - 700) / 2 + 550, (SCREEN_SIZE[1] - 30) / 2 + 100, 150, 50,
                                    PLAYERTYPE[self.playertwo.ptype],
                                    BACKGROUND)

        self.rulesbtn = Button(SCREEN_SIZE[0]-170,SCREEN_SIZE[1]-70,150,50,"Rules",BACKGROUND)
        self.displayrules = False

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

        self.leave_btn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 300, 200, 50, 'Leave',
                                BACKGROUND)

    def displayrules(self):
        background_rules = pygame.Surface(SCREEN_SIZE)
        background_rules.fill(GRAY)
        background_rules.set_alpha(150)
        self.surf.blit(background_rules, (0, 0))

        bandeau = pygame.Surface((SCREEN_SIZE[0]-200, SCREEN_SIZE[1]-200))
        bandeau.fill(BACKGROUND)
        self.surf.blit(bandeau, (100, 100))


    def parseEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.start_btn.on_button(pos):
                return CODE_TO_GAME

            if self.rulesbtn.on_button(pos):
                return CODE_TO_RULES

            if self.AI_diff_one.on_button(pos) and not self.AI_diff_one.isDisabled():
                if self.index_difficulty_one < 2:
                    self.index_difficulty_one += 1
                else:
                    self.index_difficulty_one = 0

                self.AI_diff_one.text = 'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty_one]

            if self.AI_diff_two.on_button(pos) and not self.AI_diff_two.isDisabled():
                if self.index_difficulty_two < 2:
                    self.index_difficulty_two += 1
                else:
                    self.index_difficulty_two = 0

                self.AI_diff_two.text = 'AI  Difficulty : ' + DIFFICULTY[self.index_difficulty_two]

            if self.tick_zone_one.on_button(pos):
                if self.playerone.ptype < 2:
                    self.playerone.ptype += 1
                    self.AI_diff_one.enable()
                else:
                    self.playerone.ptype = 0
                    self.AI_diff_one.disable()

                self.tick_zone_one.text = PLAYERTYPE[self.playerone.ptype]

            if self.tick_zone_two.on_button(pos):
                if self.playertwo.ptype < 2:
                    self.playertwo.ptype += 1
                    self.AI_diff_two.enable()
                else:
                    self.playertwo.ptype = 0
                    self.AI_diff_two.disable()

                self.tick_zone_two.text = PLAYERTYPE[self.playertwo.ptype]

            if self.leave_btn.on_button(pos):
                pygame.quit()
                quit()

            if self.color_btn_one.is_inside(pos):
                if self.playerone.color_index + 1 < len(COLORS):
                    if self.playerone.color_index + 1 != self.playertwo.color_index:
                        self.playerone.color_index += 1
                    else:
                        self.playerone.color_index += 2
                else:
                    if self.playertwo.color_index == 0:
                        self.playerone.color_index = 1
                    else:
                        self.playerone.color_index = 0

            if self.color_btn_two.is_inside(pos):
                if self.playertwo.color_index + 1 < len(COLORS):
                    if self.playertwo.color_index + 1 != self.playerone.color_index:
                        self.playertwo.color_index += 1
                    else:
                        self.playertwo.color_index += 2
                else:
                    if self.playerone.color_index == 0:
                        self.playertwo.color_index = 1
                    else:
                        self.playertwo.color_index = 0

    def render(self):
        self.surf.fill(BACKGROUND)
        if self.start_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.start_btn.hover(self.surf)
        else:
            self.start_btn.drawRect(self.surf)

        if self.tick_zone_one.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.tick_zone_one.hover(self.surf)
        else:
            self.tick_zone_one.drawRect(self.surf)

        if self.tick_zone_two.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.tick_zone_two.hover(self.surf)
        else:
            self.tick_zone_two.drawRect(self.surf)

        if self.AI_diff_one.get_rect().collidepoint(pygame.mouse.get_pos()) and not self.AI_diff_one.isDisabled():
            self.AI_diff_one.hover(self.surf)
        else:
            self.AI_diff_one.drawRect(self.surf)

        if self.AI_diff_two.get_rect().collidepoint(pygame.mouse.get_pos()) and not self.AI_diff_two.isDisabled():
            self.AI_diff_two.hover(self.surf)
        else:
            self.AI_diff_two.drawRect(self.surf)

        if self.leave_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.leave_btn.hover(self.surf)
        else:
            self.leave_btn.drawRect(self.surf)

        if self.rulesbtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.rulesbtn.hover(self.surf)
        else:
            self.rulesbtn.drawRect(self.surf)

        if self.color_btn_one.is_inside(pygame.mouse.get_pos()):
            self.color_btn_one.hover(COLORS[self.playerone.color_index])
        else:
            self.color_btn_one.drawCircle(COLORS[self.playerone.color_index])

        if self.color_btn_two.is_inside(pygame.mouse.get_pos()):
            self.color_btn_two.hover(COLORS[self.playertwo.color_index])
        else:
            self.color_btn_two.drawCircle(COLORS[self.playertwo.color_index])

        self.surf.blit(self.title, self.title_rect)
        self.surf.blit(self.player_one, self.player_one_rect)
        self.surf.blit(self.player_two, self.player_two_rect)
