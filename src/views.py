import math

import pygame

from src.constants import *


class TokenView:
    def __init__(self, surf, x, y, color):
        self.surf = surf
        self.x, self.y = x, y
        self.initial_x, self.initial_y = x, y
        self.color = color

    def render(self, highlighted=False):
        pygame.draw.circle(self.surf, self.color, (self.x, self.y), TOKEN_RADIUS)
        if highlighted:
            pygame.draw.circle(self.surf, LIME, (self.x, self.y),
                               TOKEN_RADIUS + 4 - TOKEN_THICKNESS, 4 - TOKEN_THICKNESS)

    def onToken(self, pos):
        return math.sqrt(math.pow((self.x - pos[0]), 2) + math.pow((self.y - pos[1]), 2)) <= TOKEN_RADIUS

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
        pygame.draw.circle(self.surf, BACKGROUND, (self.x, self.y), TOKEN_RADIUS + 4 - TOKEN_THICKNESS)

    def onPropzone(self, pos):
        return math.sqrt(math.pow((self.x - pos[0]), 2) + math.pow((self.y - pos[1]), 2)) <= TOKEN_RADIUS + 10

    def legitMove(self, token, length):
        return token.initial_x - SQUARE_WIDTH <= self.x <= token.initial_x + SQUARE_WIDTH \
               and token.initial_y - SQUARE_WIDTH <= self.y <= token.initial_y + SQUARE_WIDTH or length < 4

    def isAvailable(self):
        return self.available


class Plate:
    def __init__(self, surf, pos, w):
        self.surf = surf
        self.x, self.y = pos
        self.w = w
        self.playable_zones = []

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                self.playable_zones.append(
                    PlayableZone(self.surf, (i * SQUARE_WIDTH + SQUARE_WIDTH // 2) + (SCREEN_SIZE[0] - self.w) // 2,
                                 j * SQUARE_WIDTH + SQUARE_WIDTH // 2 + (SCREEN_SIZE[1] - self.w) // 2, i, j))

    def render(self):
        pygame.draw.rect(self.surf, BLACK, (self.x, self.y, self.w, self.w), 3)
        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                pygame.draw.line(self.surf, BLACK, (self.playable_zones[i + j * 5].x, self.playable_zones[i + j * 5].y),
                                 (self.playable_zones[- 1 - i * 5 - j].x,
                                  self.playable_zones[- 1 - i * 5 - j].y), 5)
                pygame.draw.line(self.surf, BLACK, (self.playable_zones[i + j * 5].x, self.playable_zones[i + j * 5].y),
                                 (self.playable_zones[i + i * 4 + j].x, self.playable_zones[i + i * 4 + j].y), 5)
            pygame.draw.line(self.surf, BLACK, (self.playable_zones[j].x, self.playable_zones[j].y), (
                self.playable_zones[- 5 + j].x,
                self.playable_zones[- 5 + j].y), 5)
            pygame.draw.line(self.surf, BLACK, (self.playable_zones[j * 5].x, self.playable_zones[j * 5].y),
                             (self.playable_zones[4 + j * 5].x, self.playable_zones[4 + j * 5].y), 5)

        for playable_zone in self.playable_zones:
            playable_zone.render()


class Button:
    def __init__(self, pos, size, text, color):
        self.x, self.y = pos
        self.w, self.h = size
        self.color = color
        self.text = text
        self.bordercolor = BLACK
        self.textcolor = BLACK
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.disableVal = False

    def drawRect(self, screen):
        pygame.draw.rect(screen, self.bordercolor, (self.x - 2, self.y - 2, self.w + 4, self.h + 4), 0)
        pygame.draw.rect(screen, self.color, self.rect, 0)
        font = pygame.font.Font('resources/Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, self.textcolor)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))

    def onButton(self, pos):
        return self.x < pos[0] < self.x + self.w and self.y < pos[1] < self.y + self.h

    def get_rect(self):
        return self.rect

    def hover(self, screen):
        pygame.draw.rect(screen, self.bordercolor, self.rect, 0)
        font = pygame.font.Font('resources/Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, WHITE)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))

    def disable(self):
        self.disableVal = True
        self.bordercolor = GRAY
        self.textcolor = GRAY

    def enable(self):
        self.bordercolor = BLACK
        self.disableVal = False
        self.textcolor = BLACK

    def isDisabled(self):
        return self.disableVal


class PageManager:
    def __init__(self):
        self.current = None
        self.animation_counter = 0

    def setPage(self, page):
        self.current = page

    def transitionTo(self, page, reverse=False):
        self.current = page
        self.animation_counter = -SCREEN_SIZE[0] if reverse else SCREEN_SIZE[0]

    def parseEvent(self, event):
        self.current.parseEvent(event)

    def ready(self):
        return self.animation_counter == 0

    def blit(self, display):
        if not self.animation_counter:
            display.blit(self.current.surf, (0, 0))
        else:
            display.blit(self.current.surf, (self.animation_counter, 0))

            if self.animation_counter > 0:
                self.animation_counter = max(self.animation_counter - ANIMATION_SPEED, 0)
            else:
                self.animation_counter = min(self.animation_counter + ANIMATION_SPEED, 0)
