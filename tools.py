import numpy as np
import pygame

from constants import *


def randomChoice(a):
    return a[np.random.randint(len(a))]


class Button:
    def __init__(self, x, y, w, h, text, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def drawRect(self, screen):
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, self.w + 4, self.h + 4), 0)
        pygame.draw.rect(screen, self.color, self.rect, 0)
        font = pygame.font.Font('Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, BLACK)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))

    def on_button(self, pos):
        if self.x < pos[0] < self.x + self.w:
            if self.y < pos[1] < self.y + self.h:
                return True
        return False

    def get_rect(self):
        return self.rect

    def hover(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect, 0)
        font = pygame.font.Font('Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, WHITE)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))


class PageManager:
    def __init__(self):
        self.current = None

    def setPage(self, page):
        self.current = page

    def parse_event(self, event):
        self.current.parse_event(event)
