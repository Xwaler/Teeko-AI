import sys

import numpy as np
import pygame

from constants import *


class Token:
    def __init__(self, player, pos):
        self.pos = pos
        self.player = player

    def move(self, move):
        self.pos += move


class Player:
    def __init__(self, i, AI=True):
        self.idt = i
        self.AI = AI
        self.tokens = []

    def addToken(self, pos):
        self.tokens.append(Token(self, pos))


class Teeko:
    def __init__(self):
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int)

        self.players = np.empty(2, dtype=Player)
        for i in [1, 2]:
            # FUTURE: une IA, un joueur
            # self.players[i] = Player(i, AI=i == 0)
            self.players[i - 1] = Player(i, AI=True)

        for player in self.players:
            j = 0
            while j < 4:
                pos = np.random.randint(0, 5, 2)
                if self.grid[pos[0]][pos[1]] == 0:
                    self.addToken(player, pos)
                    j += 1

    def addToken(self, player, pos):
        self.grid[pos[0]][pos[1]] = player.idt
        player.addToken(pos)

    def moveToken(self, token, direction):
        self.grid[token.pos[0]][token.pos[1]] = 0
        self.grid[token.pos[0] + direction[0]][token.pos[1] + direction[1]] = token.player.idt
        token.move(direction)

    def update(self):
        for player in self.players:
            if not player.AI:
                # TODO
                pass

            else:
                pass

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
