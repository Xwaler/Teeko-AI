import pygame

from constants import *
from views import Button

class Rules:
    def __init__(self,surf):
        self.surf = surf
        self.font = pygame.font.Font('Amatic-Bold.ttf', 120)
        self.title = self.font.render('Teeko Rules', True, BLACK)
        self.title_rect = self.title.get_rect()
        self.title_rect.center = (SCREEN_SIZE[0] / 2, 130)

        with open('rules.txt','r') as f:
            self.rulestxt = f.readlines()


        self.font = pygame.font.Font('Amatic-Bold.ttf', 40)

        self.leavebtn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 300, 200, 50, 'Leave',
                                BACKGROUND)

    def parseEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self.leavebtn.on_button(pos):
                return CODE_TO_MENU


    def render(self):
        self.surf.fill(BACKGROUND)

        if self.leavebtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.leavebtn.hover(self.surf)
        else:
            self.leavebtn.drawRect(self.surf)

        self.surf.blit(self.title, self.title_rect)
        i=0
        for lines in self.rulestxt:
            line = self.font.render(lines, True, BLACK)
            line_rect = line.get_rect()
            line_rect.center = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2 - 100 + i*70 )
            self.surf.blit(line,line_rect)
            i+=1