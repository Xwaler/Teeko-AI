import sys

import math

import numpy as np
import pygame

from constants import *
from tools import *

class ColorChanger:
    def __init__(self, x, y, r , color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color

    def drawCircle(self,screen,color):
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.r)
        pygame.draw.circle(screen, color, (self.x,self.y),self.r-2)

    def changeColor(self, pos):
        if math.sqrt(math.pow((self.x - pos[0]),2)+math.pow((self.y-pos[1]),2)) <= self.r:
            return True
        return False


class Button:
    def __init__(self, x, y, w, h, text, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.rect = pygame.Rect(x,y,w,h)

    def drawRect(self, screen):
        pygame.draw.rect(screen,BLACK,(self.x-2,self.y-2,self.w+4,self.h+4),0)
        pygame.draw.rect(screen, self.color, self.rect, 0)
        font = pygame.font.Font('Amatic-Bold.ttf',35)
        text = font.render(self.text, 1, BLACK)
        screen.blit(text, (self.x + (self.w/2 - text.get_width()/2), self.y + (self.h/2 - text.get_height()/2)))

    def on_button(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.w:
            if pos[1] > self.y and pos[1] < self.y + self.h:
                return True
        return False

    def get_rect(self):
        return self.rect

    def hover(self,screen):
        pygame.draw.rect(screen, BLACK, self.rect, 0)
        font = pygame.font.Font('Amatic-Bold.ttf', 35)
        text = font.render(self.text, 1, WHITE)
        screen.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (self.h / 2 - text.get_height() / 2)))


class Token:
    def __init__(self, player, pos):
        self.pos = np.array(pos)
        self.player = player

    def move(self, direction):
        self.pos += direction


class Player:
    def __init__(self, i, AI=True):
        self.idt = i
        self.AI = AI
        self.tokens = []
        self.has_played = False

    def addToken(self, pos):
        self.tokens.append(Token(self, pos))


class Teeko:
    def __init__(self):
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int)

        self.players = np.empty(2, dtype=Player)
        for i in [1, 2]:
            self.players[i - 1] = Player(i, AI=i == 1)
            # self.players[i - 1] = Player(i, AI=True)

        for player in self.players:
            j = 0
            while j < 4:
                pos = np.random.randint(0, 5, 2)
                if self.grid[pos[0]][pos[1]] == 0:
                    self.addToken(player, pos)
                    j += 1

        self.turn_to = randomChoice(self.players)

    def addToken(self, player, pos):
        self.grid[pos[0]][pos[1]] = player.idt
        player.addToken(pos)

    def moveToken(self, token, direction):
        self.grid[token.pos[0]][token.pos[1]] = 0
        self.grid[token.pos[0] + direction[0]][token.pos[1] + direction[1]] = token.player.idt
        token.move(direction)

    def getPossibleMove(self, token):
        token_moves = []

        for shift in SURROUNDING:
            if 0 <= token.pos[0] + shift[0] < 5 and 0 <= token.pos[1] + shift[1] < 5 and \
                    self.grid[token.pos[0] + shift[0]][token.pos[1] + shift[1]] == 0:
                token_moves.append(shift)

            if 0 <= token.pos[0] - shift[0] < 5 and 0 <= token.pos[1] - shift[1] < 5 and \
                    self.grid[token.pos[0] - shift[0]][token.pos[1] - shift[1]] == 0:
                token_moves.append([-shift[0], -shift[1]])

        return token_moves

    def getAllMoves(self, player):
        moves = {}

        for token in player.tokens:
            currentTokenMoves = self.getPossibleMove(token)

            if currentTokenMoves:
                moves[token] = currentTokenMoves

        return moves

    def getAllEmpty(self):
        positions = []
        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                if self.grid[j][i] == 0:
                    positions.append((j, i))
        return positions

    def update(self):
        player = self.turn_to

        if player.AI:
            # TODO: replace random with min/max

            if np.random.random() < .5:  # place new token
                positions = self.getAllEmpty()
                pos = randomChoice(positions)
                self.addToken(player, pos)

            else:  # move token
                tokens_with_moves = self.getAllMoves(player)
                token = randomChoice(list(tokens_with_moves.keys()))
                direction = randomChoice(tokens_with_moves[token])
                self.moveToken(token, direction)

            player.has_played = True

        else:
            # waits about a sec
            if np.random.random() < 1 / 60:
                player.has_played = True

        if player.has_played:
            self.turn_to = self.players[abs(np.where(self.players == player)[0][0] - 1)]
            player.has_played = False

    def render(self, surf):
        square_width = SCREEN_SIZE[1] // GRID_SIZE
        surf.fill((200, 200, 200))

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                pygame.draw.circle(surf, RED if self.grid[j][i] == 2 else BLACK,
                                   (i * square_width + square_width // 2, j * square_width + square_width // 2),
                                   TOKEN_RADIUS, TOKEN_THICKNESS if self.grid[j][i] == 0 else 0)

        return surf

    def print(self):
        print(self.grid)
        sys.stdout.flush()
