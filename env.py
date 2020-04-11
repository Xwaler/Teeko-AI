import threading
import time

import numpy as np
import pygame

from constants import *
# from dqn import DQNAgent
from tools import randomChoice
from views import Plate, TokenView, Button


class Token:
    def __init__(self, player, pos):
        self.pos = np.array(pos)
        self.player = player

    def move(self, direction):
        self.pos += direction

    def __str__(self):
        return self.pos.__str__()

    def __repr__(self):
        return self.player.__repr__()


class Player:
    def __init__(self, i, ptype, color):
        self.idt = i
        self.ptype = ptype
        self.tokens = []
        self.has_played = False
        self.colorindex = color

    def __repr__(self):
        return self.idt.__repr__()


class Teeko:
    def __init__(self, surf=None):
        self.surf = surf
        self.render_enabled = surf is not None
        self.grid = None
        self.index_difficulty = None
        self.players = None
        self.turn_to = None
        self.players_tokens = None
        self.minmax_thread = None
        self.kill_thread = False
        self.square_width = None
        self.font = None
        self.player_one = None
        self.player_one_rect = None
        self.player_two = None
        self.player_two_rect = None
        self.back_btn = None
        self.plate = None
        self.selected_token = None
        self.selection_offset_y = None
        self.selection_offset_x = None
        self.dqnAgent = None

    def loadDQN(self):
        # self.dqnAgent = DQNAgent()
        pass

    def reset(self, players=None, index_difficulty=(1, 1)):
        self.grid = np.empty((GRID_SIZE, GRID_SIZE), dtype=Token)
        self.index_difficulty = index_difficulty
        if players is not None:
            self.players = players
            for player in self.players:
                player.tokens.clear()
                if player.ptype == 2 and self.dqnAgent is None:
                    self.loadDQN()
        else:
            self.players = [Player(i, 1, i - 1) for i in [1, 2]]
        self.turn_to = randomChoice(self.players)

        self.players_tokens = []

        self.minmax_thread = None
        self.kill_thread = False

        self.square_width = (SCREEN_SIZE[1] - 100) // GRID_SIZE

        for k in range(2):
            self.players_tokens.extend(
                (k + 1, m + 1, TokenView(
                    self.surf, (int((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4) + (
                            k * int(self.square_width * GRID_SIZE + (SCREEN_SIZE[0] -
                                                                     self.square_width * GRID_SIZE) / 2))),
                    m * (TOKEN_RADIUS * 2 + 30) + 250
                ), self.players[k].ptype != 0) for m in range(4)
            )

        if self.render_enabled:
            self.initRender()

    def initRender(self):
        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)

        self.player_one = self.font.render('Player 1', True, BLACK)
        self.player_one_rect = self.player_one.get_rect()
        self.player_one_rect.center = (int((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4), 150)

        self.player_two = self.font.render('Player 2', True, BLACK)
        self.player_two_rect = self.player_two.get_rect()
        self.player_two_rect.center = (
            int(3 * (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4) + self.square_width * GRID_SIZE, 150)

        self.back_btn = Button((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4 - 75, SCREEN_SIZE[1] - 80, 150, 50,
                               '< Back', BACKGROUND)

        self.plate = Plate(self.surf, (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 2,
                           (SCREEN_SIZE[1] - self.square_width * GRID_SIZE) / 2,
                           self.square_width * GRID_SIZE, self.square_width)
        self.selected_token = None
        self.selection_offset_y = 0
        self.selection_offset_x = 0

    def won(self):
        print(f'Game finished. Player {self.turn_to.idt} won\n', self.grid)
        raise SystemExit()

    def calculating(self):
        return self.minmax_thread is not None

    def killMinMax(self):
        if self.calculating():
            self.kill_thread = True
            while self.calculating():
                time.sleep(.5)

    def getAligned(self, player):
        longest_line = 1
        for token in player.tokens:
            for direction in DIRECTIONS:
                if not (direction == (-1, -1) and (np.abs(token.pos[0] - token.pos[1]) > 1) or
                        direction == (-1, 1) and (token.pos[0] + token.pos[1] > 5 or token.pos[0] + token.pos[1] < 3)):

                    current_alignment = 1

                    new_line = token.pos[0] + direction[0]
                    new_column = token.pos[1] + direction[1]

                    while (0 <= new_line < 5 and 0 <= new_column < 5 and self.grid[new_line][new_column] is not None and
                           self.grid[new_line][new_column].player.idt == self.grid[token.pos[0]][
                               token.pos[1]].player.idt):
                        new_line = new_line + direction[0]
                        new_column = new_column + direction[1]

                        current_alignment += 1

                    new_line = token.pos[0] - direction[0]
                    new_column = token.pos[1] - direction[1]

                    while (0 <= new_line < 5 and 0 <= new_column < 5 and self.grid[new_line][new_column] is not None and
                           self.grid[new_line][new_column].player.idt == self.grid[token.pos[0]][
                               token.pos[1]].player.idt):
                        new_line = new_line - direction[0]
                        new_column = new_column - direction[1]

                        current_alignment += 1

                    if current_alignment > longest_line:
                        longest_line = current_alignment

        return longest_line

    def addToken(self, player, pos):
        token = Token(player, pos)
        self.grid[pos[0]][pos[1]] = token
        player.tokens.append(token)

    def removeToken(self, player, pos):
        self.grid[pos[0]][pos[1]] = None

        for token in player.tokens:
            if token.pos[0] == pos[0] and token.pos[1] == pos[1]:
                player.tokens.remove(token)
                break

    def moveToken(self, token, direction):
        self.grid[token.pos[0]][token.pos[1]] = None
        self.grid[token.pos[0] + direction[0]][token.pos[1] + direction[1]] = token
        token.move(direction)

    def getPossibleMove(self, token):
        token_moves = []

        for shift in SURROUNDING:
            if 0 <= token.pos[0] + shift[0] < 5 and 0 <= token.pos[1] + shift[1] < 5 and \
                    self.grid[token.pos[0] + shift[0]][token.pos[1] + shift[1]] is None:
                token_moves.append([1, token.pos.tolist(), shift])

            if 0 <= token.pos[0] - shift[0] < 5 and 0 <= token.pos[1] - shift[1] < 5 and \
                    self.grid[token.pos[0] - shift[0]][token.pos[1] - shift[1]] is None:
                token_moves.append([1, token.pos.tolist(), [-shift[0], -shift[1]]])

        return token_moves

    def getAllMoves(self, player):
        moves = []
        if len(player.tokens) < 4:
            moves.extend([[0, pos, [0, 0]] for pos in self.getAllEmpty()])
        else:
            for token in player.tokens:
                moves.extend(self.getPossibleMove(token))
        return moves

    def getAllEmpty(self):
        positions = []
        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                if self.grid[j][i] is None:
                    positions.append([j, i])
        return positions

    def over(self):
        return max(self.getAligned(player) for player in self.players) >= 4

    def getScore(self):
        p1 = self.getAligned(self.players[0])
        # print("p1 : ", p1)
        p2 = self.getAligned(self.players[1])
        # print("p2 : ", p2)
        return (p1 ** 1.5) - (p2 ** 1.5)

    #  move = (0, (pos token à placer), (0, 0)) ou (1, (pos token à deplacer), (direction))
    def minMax(self, depth, alpha, beta, player):
        if self.kill_thread:
            raise SystemExit()

        DEPTH_IS_ZERO = depth == 0
        DEPTH_IS_MAX = depth == MAX_DEPTH[self.index_difficulty[self.turn_to.idt - 1]]

        # print("\n\ndepth : ", depth)

        # print("state : \n", self.grid)

        # print("player : ", player.idt)

        # print("move : ", move)

        if DEPTH_IS_ZERO or self.over():
            return self.getScore() * (1 + (.25 * depth))

        if player.idt == 1:
            max_score = -np.inf
            max_score_moves = []

            for move in self.getAllMoves(player):
                if move[0] == 0:
                    self.addToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0]][move[1][1]], move[2])

                score = self.minMax(depth - 1, alpha, beta, self.players[abs(player.idt - 2)])
                # print("score : ", score)

                if move[0] == 0:
                    self.removeToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                   [-move[2][0], -move[2][1]])

                if score > max_score:
                    max_score = score
                    max_score_moves = []

                if score == max_score:
                    max_score_moves.append(move)

                alpha = np.max([alpha, score])
                if beta <= alpha:
                    break

            if not DEPTH_IS_MAX:
                return max_score
            else:
                print('Max: ', max_score_moves)
                return max_score, randomChoice(max_score_moves)

        else:
            min_score = np.inf
            min_score_moves = []

            for move in self.getAllMoves(player):
                if move[0] == 0:
                    self.addToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0]][move[1][1]], move[2])

                score = self.minMax(depth - 1, alpha, beta, self.players[abs(player.idt - 2)])
                # print("score : ", score)

                if move[0] == 0:
                    self.removeToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                   [-move[2][0], -move[2][1]])
                # print("score : ", score)

                if score < min_score:
                    min_score = score
                    min_score_moves = []

                if score == min_score:
                    min_score_moves.append(move)

                beta = np.min([beta, score])
                if beta <= alpha:
                    break

            if not DEPTH_IS_MAX:
                return min_score
            else:
                print('Min: ', min_score_moves)
                return min_score, randomChoice(min_score_moves)

    def makeMove(self, move):
        AI_tokens = [token for token in self.players_tokens if token[0] == self.turn_to.idt]

        if move[0] == 0:
            self.addToken(self.turn_to, move[1])
            if self.render_enabled:
                for drop_zones in self.plate.playable_zones:
                    if drop_zones.abscisse == move[1][1] and drop_zones.ordonne == move[1][0]:
                        drop_zones.available = False
                        AI_tokens[len(self.turn_to.tokens) - 1][2].placeToken((drop_zones.x, drop_zones.y))
                        break

        else:
            self.moveToken(self.grid[move[1][0]][move[1][1]], move[2])

            if self.render_enabled:
                current_drop_zone, future_drop_zone, i = None, None, 0
                while current_drop_zone is None or future_drop_zone is None:
                    drop_zone = self.plate.playable_zones[i]
                    if current_drop_zone is None and drop_zone.abscisse == move[1][1] and \
                            drop_zone.ordonne == move[1][0]:
                        current_drop_zone = drop_zone
                    if future_drop_zone is None and drop_zone.abscisse == move[1][1] + move[2][1] and \
                            drop_zone.ordonne == move[1][0] + move[2][0]:
                        future_drop_zone = drop_zone
                    i += 1

                current_drop_zone.available = True
                for token in AI_tokens:
                    if token[2].initial_x == current_drop_zone.x and token[2].initial_y == current_drop_zone.y:
                        token[2].placeToken((future_drop_zone.x, future_drop_zone.y))
                        future_drop_zone.available = False
                        break

        self.turn_to.has_played = True
        self.minmax_thread = None

    def AI_handler(self):
        print('Grid before : \n', self.grid)
        score, move = self.minMax(MAX_DEPTH[self.index_difficulty[self.turn_to.idt - 1]], -np.inf, np.inf, self.turn_to)
        print('Score : ', score, ' | Selected move : ', move)
        self.makeMove(move)

    def update(self):
        if not self.turn_to.has_played:
            if self.turn_to.ptype == 1 and not self.calculating():
                self.minmax_thread = threading.Thread(target=self.AI_handler)
                self.minmax_thread.start()

            elif self.turn_to.ptype == 2:
                # preds = self.dqnAgent.predict(self.getState())
                # move = self.predsToMove(preds)
                # self.makeMove(move)
                pass

        else:
            if self.over():
                self.won()

            self.turn_to.has_played = False
            self.turn_to = self.players[abs(self.turn_to.idt - 2)]

    def getState(self):
        # TODO: RETURNS AN ARRAY REPRESENTATION OF THE GAME STATE
        pass

    def predsToMove(self, preds):
        # TODO: CONVERTS AN ARRAY OF PROBABILITIES TO A MOVE
        pass

    def moveToPreds(self, move):
        # TODO: CONVERTS A MOVE TO A PERFECT ARRAY WITH THE SHAPE OF THE NETWORK'S OUTPUT,
        #  MUST REPRESENT THE OBJECTIVE THAT THE NETWORK MUST ACHIEVE
        pass

    def render(self):
        self.surf.fill(BACKGROUND)

        self.surf.blit(self.player_one, self.player_one_rect)
        self.surf.blit(self.player_two, self.player_two_rect)

        if self.back_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.back_btn.hover(self.surf)
        else:
            self.back_btn.drawRect(self.surf)

        self.plate.render()
        for token_view in self.players_tokens:
            if token_view[0] == 1:
                token_view[2].render(COLORS[self.players[0].colorindex])
            elif token_view[0] == 2:
                token_view[2].render(COLORS[self.players[1].colorindex])

    def parseEvent(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_btn.on_button(pos):
                return CODE_TO_MENU

            for token_view in self.players_tokens:
                if token_view[2].on_token(pos) and not token_view[3] and self.turn_to.idt == token_view[0]:
                    self.selected_token = token_view[2]
                    self.selection_offset_x = token_view[2].x - pos[0]
                    self.selection_offset_y = token_view[2].y - pos[1]

        if event.type == pygame.MOUSEBUTTONUP:
            if self.selected_token is not None:
                for drop_zone in self.plate.playable_zones:
                    if drop_zone.isAvailable() and drop_zone.onPropzone(pos):
                        current_drop_zone, i = None, 0
                        while i < len(self.plate.playable_zones) and current_drop_zone is None:
                            iter_drop_zone = self.plate.playable_zones[i]
                            if self.selected_token.initial_x == iter_drop_zone.x and \
                                    self.selected_token.initial_y == iter_drop_zone.y:
                                current_drop_zone = iter_drop_zone
                            i += 1
                        if current_drop_zone is not None:
                            self.removeToken(self.turn_to, (current_drop_zone.ordonne, current_drop_zone.abscisse))
                            current_drop_zone.available = True

                        self.addToken(self.turn_to, (drop_zone.ordonne, drop_zone.abscisse))
                        self.selected_token.placeToken((drop_zone.x, drop_zone.y))
                        drop_zone.available = False

                        self.selected_token = None
                        self.turn_to.has_played = True
                        break

                if self.selected_token is not None:
                    self.selected_token.placeToken((self.selected_token.initial_x, self.selected_token.initial_y))
                    self.selected_token = None

        if event.type == pygame.MOUSEMOTION:
            if self.selected_token is not None:
                self.selected_token.drag((self.selection_offset_x + pos[0], self.selection_offset_y + pos[1]))

    def print(self):
        print(self.grid)
