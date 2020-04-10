import math

import pygame

from constants import *


class TokenView:
    def __init__(self, surf, x, y):
        self.surf = surf
        self.x, self.y = x, y
        self.initial_x, self.initial_y = x, y
        self.color = None

    def render(self, color):
        self.color = color
        pygame.draw.circle(self.surf, color, (self.x, self.y), TOKEN_RADIUS)

    def on_token(self, pos):
        if math.sqrt(math.pow((self.x - pos[0]), 2) + math.pow((self.y - pos[1]), 2)) <= TOKEN_RADIUS:
            return True
        return False

    def placeToken(self, pos):
        self.x, self.y = pos
        self.initial_x, self.initial_y = pos

    def drag(self, pos):
        self.x, self.y = pos


class PlayableZone:
    def __init__(self, surf, x, y, i, j):
        self.surf = surf
        self.x = x
        self.y = y
        self.abscisse = i
        self.ordonne = j
        self.available = True

    def render(self):
        pygame.draw.circle(self.surf, BLACK, (self.x, self.y), TOKEN_RADIUS + 5, TOKEN_THICKNESS)

    def onPropzone(self, pos):
        if math.sqrt(math.pow((self.x - pos[0]), 2) + math.pow((self.y - pos[1]), 2)) <= TOKEN_RADIUS:
            return True
        return False

    def isAvailable(self):
        return self.available


class Plate:
    def __init__(self, surf, x, y, w, square_width):
        self.surf = surf
        self.x = x
        self.y = y
        self.w = w
        self.playable_zones = []
        self.square_width = square_width

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                self.playable_zones.append(
                    PlayableZone(self.surf, (i * self.square_width + self.square_width // 2) + int(
                        (SCREEN_SIZE[0] - self.w) / 2),
                                 j * self.square_width + self.square_width // 2 + int(
                                     (SCREEN_SIZE[1] - self.w) / 2), i, j))

    def render(self):
        pygame.draw.rect(self.surf, BLACK, (self.x, self.y, self.w, self.w), 3)

        for playable_zone in self.playable_zones:
            playable_zone.render()


class Button:
    def __init__(self, x, y, w, h, text, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.bordercolor = BLACK
        self.textcolor = BLACK
        self.rect = pygame.Rect(x, y, w, h)
        self.disableVal = False

    def drawRect(self, screen):
        pygame.draw.rect(screen, self.bordercolor, (self.x - 2, self.y - 2, self.w + 4, self.h + 4), 0)
        pygame.draw.rect(screen, self.color, self.rect, 0)
        font = pygame.font.Font('Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, self.textcolor)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))

    def on_button(self, pos):
        if self.x < pos[0] < self.x + self.w:
            if self.y < pos[1] < self.y + self.h:
                return True
        return False

    def get_rect(self):
        return self.rect

    def hover(self, screen):
        pygame.draw.rect(screen, self.bordercolor, self.rect, 0)
        font = pygame.font.Font('Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, WHITE)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))

    def disable(self):
        self.disableVal = True
        self.bordercolor = GRAY
        self.textcolor = GRAY

    def able(self):
        self.bordercolor = BLACK
        self.disableVal = False
        self.textcolor = BLACK

    def isDisable(self):
        return self.disableVal
