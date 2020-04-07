import math

import pygame

from constants import *
from tools import Button


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
        self.titleRect = self.title.get_rect()
        self.titleRect.center = (SCREEN_SIZE[0] / 2, 200)

        self.INDEXCOLORONE = 0
        self.INDEXCOLORTWO = 1
        self.indexdifficulty = 0

        self.colorbtnone = ColorChanger(int((SCREEN_SIZE[0] - 400) / 2), int((SCREEN_SIZE[1] - 30) / 2 + 30), 30,
                                        COLORS[self.INDEXCOLORONE])
        self.colorbtntwo = ColorChanger(int((SCREEN_SIZE[0] - 400) / 2 + 300), int((SCREEN_SIZE[1] - 30) / 2 + 30), 30,
                                        COLORS[self.INDEXCOLORTWO])

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)
        self.playerone = self.font.render('Player 1', True, BLACK)
        self.playeronerect = self.playerone.get_rect()
        self.playeronerect.center = (int((SCREEN_SIZE[0] - 300) / 2 + 50), (SCREEN_SIZE[1] - 30) / 2 + 30)

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)
        self.playertwo = self.font.render('Player 2', True, BLACK)
        self.playertworect = self.playertwo.get_rect()
        self.playertworect.center = (int((SCREEN_SIZE[0] - 300) / 2 + 350), (SCREEN_SIZE[1] - 30) / 2 + 30)

        self.startbtn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 220, 200, 50, 'Start',
                               BACKGROUND)
        self.settingsbtn = Button((SCREEN_SIZE[0] - 250) / 2, (SCREEN_SIZE[1] - 50) / 2 + 150, 250, 50, 'AI  Difficulty : ' + DIFFICULTY[self.indexdifficulty],
                               BACKGROUND)
        self.leavebtn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 290, 200, 50, 'Leave',
                               BACKGROUND)

    def parse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.startbtn.on_button(pos):
                return CODE_TO_GAME

            if self.settingsbtn.on_button(pos):
                if self.indexdifficulty < 2:
                    self.indexdifficulty +=1
                else:
                    self.indexdifficulty = 0

                self.settingsbtn.text = 'AI  Difficulty : ' + DIFFICULTY[self.indexdifficulty]

            if self.leavebtn.on_button(pos):
                pygame.quit()
                quit()

            if self.colorbtnone.changeColor(pos):
                if self.INDEXCOLORONE + 1 < len(COLORS):
                    if self.INDEXCOLORONE + 1 != self.INDEXCOLORTWO:
                        self.INDEXCOLORONE += 1
                    else:
                        self.INDEXCOLORONE += 2
                else:
                    if self.INDEXCOLORTWO == 0:
                        self.INDEXCOLORONE = 1
                    else:
                        self.INDEXCOLORONE = 0
            if self.colorbtntwo.changeColor(pos):
                if self.INDEXCOLORTWO + 1 < len(COLORS):
                    if self.INDEXCOLORTWO + 1 != self.INDEXCOLORONE:
                        self.INDEXCOLORTWO += 1
                    else:
                        self.INDEXCOLORTWO += 2
                else:
                    if self.INDEXCOLORONE == 0:
                        self.INDEXCOLORTWO = 1
                    else:
                        self.INDEXCOLORTWO = 0

    def render(self):
        self.surf.fill(BACKGROUND)
        if self.startbtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.startbtn.hover(self.surf)
        else:
            self.startbtn.drawRect(self.surf)

        if self.settingsbtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.settingsbtn.hover(self.surf)
        else:
            self.settingsbtn.drawRect(self.surf)

        if self.leavebtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.leavebtn.hover(self.surf)
        else:
            self.leavebtn.drawRect(self.surf)

        self.colorbtnone.drawCircle(self.surf, COLORS[self.INDEXCOLORONE])
        self.colorbtntwo.drawCircle(self.surf, COLORS[self.INDEXCOLORTWO])

        self.surf.blit(self.title, self.titleRect)
        self.surf.blit(self.playerone, self.playeronerect)
        self.surf.blit(self.playertwo, self.playertworect)
