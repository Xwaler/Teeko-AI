import bisect
import threading

import numpy as np
import pygame

from constants import *
from tools import randomChoice, predsToMove, moveToPreds
from views import Plate, TokenView, Button


class Player:
    def __init__(self, i, ptype, color):
        self.idt = i
        self.ptype = ptype
        self.tokens = []
        self.has_played = False
        self.color_index = color

    def __repr__(self):
        return self.idt.__repr__()


class Teeko:
    def __init__(self, surf=None):
        self.grid = None
        self.index_difficulty = None
        self.players = None
        self.dqn_agent = None
        self.turn_to = None
        self.minmax_thread = None
        self.kill_thread = False
        self.turn = None

        self.render_enabled = surf is not None
        self.surf = surf
        self.players_tokens = None
        self.font = None
        self.player_one = None
        self.player_one_rect = None
        self.player_two = None
        self.player_two_rect = None
        self.back_btn = None
        self.plate = None
        self.error_txt_1 = None
        self.error_txt_1_rect = None
        self.error_txt_2 = None
        self.error_txt_2_rect = None
        self.currentlyplaying = None
        self.currentlyplaying_rect = None
        self.angle = None
        self.winner_annouced = None
        self.winner_annouced_rect = None
        self.retry_btn = None
        self.goto_menu = None
        self.leave_game = None
        self.selected_token = None
        self.selection_offset_y = None
        self.selection_offset_x = None
        self.game_ended = False
        self.error_trigger_code = False

    def loadDQN(self):
        from dqn import DQNAgent
        self.dqn_agent = DQNAgent()

    def reset(self, players=None, index_difficulty=(1, 1)):
        self.grid = np.zeros(GRID_SIZE * GRID_SIZE, dtype=np.int)
        self.index_difficulty = index_difficulty
        if players is not None:
            self.players = players
            for player in self.players:
                player.tokens.clear()
                if player.ptype == 2 and self.dqn_agent is None:
                    self.loadDQN()
        else:
            self.players = [Player(i, 1, i - 1) for i in [1, 2]]
        self.turn_to = randomChoice(self.players)

        self.minmax_thread = None
        self.kill_thread = False
        self.turn = 0

        if self.render_enabled:
            self.initRender()

    def initRender(self):
        self.players_tokens = []
        for k in range(2):
            x = (SCREEN_SIZE[0] - SQUARE_WIDTH * GRID_SIZE) // 4 + (k * int(
                SQUARE_WIDTH * GRID_SIZE + (SCREEN_SIZE[0] - SQUARE_WIDTH * GRID_SIZE) / 2
            ))
            self.players_tokens.extend(
                (k + 1, m + 1, TokenView(self.surf, x, m * (TOKEN_RADIUS * 2 + 30) + 250,
                                         COLORS[self.players[k].color_index]),
                 self.players[k].ptype != 0) for m in range(4)
            )

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)

        self.player_one = self.font.render('Player 1', True, BLACK)
        self.player_one_rect = self.player_one.get_rect()
        self.player_one_rect.center = GAME_PLAYER_ONE_CENTER

        self.player_two = self.font.render('Player 2', True, BLACK)
        self.player_two_rect = self.player_two.get_rect()
        self.player_two_rect.center = GAME_PLAYER_TWO_CENTER

        self.currentlyplaying = pygame.image.load("hourglass.png")
        self.angle = 0

        self.back_btn = Button(BACK_BTN_POS, BACK_BTN_SIZE, '< Back', BACKGROUND)

        self.plate = Plate(self.surf, PLATE_POS, PLATE_W)

        self.error_txt_1 = self.font.render('You can\'t place your token here :/', True, BLACK)
        self.error_txt_1_rect = self.error_txt_1.get_rect()
        self.error_txt_1_rect.center = ERROR_TXT_CENTER
        self.error_txt_2 = self.font.render('You can\'t move your tokens yet :/', True, BLACK)
        self.error_txt_2_rect = self.error_txt_2.get_rect()
        self.error_txt_2_rect.center = ERROR_TXT_CENTER

        self.font = pygame.font.Font('Amatic-Bold.ttf', 80)
        self.winner_annouced = self.font.render(f'Player {self.turn_to.idt} won !', True, BLACK)
        self.winner_annouced_rect = self.winner_annouced.get_rect()
        self.winner_annouced_rect.center = WINNER_CENTER

        self.retry_btn = Button(RETRY_BTN_POS, RETRY_BTN_SIZE, 'Retry', BACKGROUND)
        self.goto_menu = Button(MENU_BTN_POS, MENU_BTN_SIZE, 'Go to Menu', BACKGROUND)
        self.leave_game = Button(QUIT_BTN_POS, QUIT_BTN_SIZE, 'Quit', BACKGROUND)

        self.selected_token = None
        self.selection_offset_y = 0
        self.selection_offset_x = 0

    def won(self):
        self.game_ended = True
        self.winner_annouced = self.font.render(f'Player {self.turn_to.idt} won !', True, BLACK)
        print(f'Game finished. Player {self.turn_to.idt} won\n', self.rectGrid())

    def calculating(self):
        return self.minmax_thread is not None

    def killMinMax(self):
        if self.calculating():
            self.kill_thread = True
            while self.calculating():
                continue

    def getAligned(self, player):
        longest_alignment = 1

        for token in player.tokens:
            l_shape_first_direction = 0

            for direction in SURROUNDING:
                current_alignment = 1

                alignment_contain_zero = False
                zero_is_last = False
                followed_by_two_0 = False

                current_cell = token
                module_current_cell = current_cell % 5

                next_cell = token + direction

                IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                                   (current_cell + next_cell) % 5 != 4)

                while IN_GRID:
                    next_cell_value = self.grid[next_cell]

                    if next_cell_value == 0:
                        if alignment_contain_zero:
                            followed_by_two_0 = True
                            break

                        else:
                            alignment_contain_zero = True
                            zero_is_last = True

                    elif next_cell_value == player.idt:
                        zero_is_last = False
                        current_alignment += 1

                    else:
                        break

                    current_cell = next_cell
                    module_current_cell = current_cell % 5

                    next_cell = current_cell + direction

                    IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                                       (current_cell + next_cell) % 5 != 4)

                if current_alignment == 4:
                    if alignment_contain_zero and not zero_is_last:
                        current_alignment = 3

                    else:
                        current_alignment = 4

                elif current_alignment == 3:
                    if not alignment_contain_zero:
                        current_cell = token
                        module_current_cell = current_cell % 5

                        next_cell = current_cell - direction

                        IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                                           (current_cell + next_cell) % 5 != 4)

                        if IN_GRID and self.grid[next_cell] == 0:
                            current_alignment = 3

                        else:
                            current_alignment = 1
                            square_alignment, l_shape_first_direction = self.squareTest(l_shape_first_direction,
                                                                                        direction, token, player.idt)
                            current_alignment = max(current_alignment, square_alignment)

                    else:
                        current_alignment = 3

                elif current_alignment == 2:
                    if not alignment_contain_zero or zero_is_last:
                        square_alignment, l_shape_first_direction = self.squareTest(l_shape_first_direction, direction,
                                                                                    token, player.idt)

                        current_alignment = max(current_alignment, square_alignment)
                        if current_alignment == 2:
                            if not followed_by_two_0:
                                current_cell = token
                                module_current_cell = current_cell % 5

                                next_cell = current_cell - direction

                                IN_GRID = 0 <= next_cell < 25 and (
                                        (module_current_cell != 0 and module_current_cell != 4) or
                                        (current_cell + next_cell) % 5 != 4)

                                if IN_GRID and self.grid[next_cell] == 0:
                                    if not zero_is_last:
                                        current_cell = next_cell
                                        module_current_cell = current_cell % 5

                                        next_cell = current_cell - direction

                                        IN_GRID = 0 <= next_cell < 25 and (
                                                (module_current_cell != 0 and module_current_cell != 4) or
                                                (current_cell + next_cell) % 5 != 4)

                                        if not IN_GRID or self.grid[next_cell] != 0:
                                            current_alignment = 1

                                else:
                                    current_alignment = 1

                    elif alignment_contain_zero:
                        current_alignment = 1

                if current_alignment > 2:
                    return current_alignment

                if current_alignment > longest_alignment:
                    longest_alignment = current_alignment

        return longest_alignment

    def squareTest(self, l_shape_first_direction, direction, token, idt):
        current_alignment = 3

        if l_shape_first_direction == 0:
            current_alignment = 1
            if direction != 6:
                l_shape_first_direction = direction

        elif LSTTT[l_shape_first_direction] != direction:
            current_alignment = 1
            if direction == 5 and l_shape_first_direction == 1:
                fourth_cell_value = self.grid[token + 6]
                if fourth_cell_value == idt:
                    current_alignment = 4
                elif fourth_cell_value == 0:
                    current_alignment = 3

        else:
            fourth_cell_value = self.grid[token + LSFTT[l_shape_first_direction]]
            if fourth_cell_value != 0:
                current_alignment = 1

        return current_alignment, l_shape_first_direction

    def addToken(self, player, pos):
        self.grid[pos] = player.idt
        bisect.insort(player.tokens, pos)

    def removeToken(self, player, pos):
        self.grid[pos] = 0

        for token in player.tokens:
            if token == pos:
                player.tokens.remove(token)
                break

    def moveToken(self, player, pos, direction):
        self.grid[pos] = 0
        self.grid[pos + direction] = player.idt

        for i, token in enumerate(player.tokens):
            if token == pos:
                player.tokens[i] += direction
                player.tokens.sort()
                break

    def getPossibleMove(self, token):
        token_moves = []
        module_pos = token % 5
        SAFE_ZONE = (module_pos != 0 and module_pos != 4)

        for shift in DIRECTIONS:
            token_plus = token + shift

            if 0 <= token_plus < 25 and self.grid[token_plus] == 0 and (SAFE_ZONE or (token_plus + token) % 5 != 4):
                token_moves.append([1, token, shift])

        return token_moves

    def getAllMoves(self, player):
        if len(player.tokens) < 4:
            moves = [[0, pos, 0] for pos in self.getAllEmpty()]
        else:
            moves = []
            for token in player.tokens:
                moves.extend(self.getPossibleMove(token))
        return moves

    def getAllEmpty(self):
        return np.where(self.grid == 0)[0]

    def over(self, align_score=None):
        if align_score is None:
            align_score = [self.getAligned(player) for player in self.players]
        return max(align_score) >= 4

    def getScore(self, align_score=None, depth=0):
        if align_score is None:
            align_score = [self.getAligned(player) for player in self.players]
        p1, p2 = align_score

        if p1 >= 4:
            return 20 * (depth + 1)
        elif p2 >= 4:
            return -20 * (depth + 1)
        else:
            w1, w2 = (1.50, 1.75) if self.turn_to.idt == 1 else (1.75, 1.50)
            return round((p1 ** w1) - (p2 ** w2), 4)

    #  move = (0, pos token à placer, 0) ou (1, pos token à deplacer, direction)
    def minMax(self, depth, alpha, beta, player):
        if self.kill_thread:
            self.minmax_thread = None
            raise SystemExit()

        DEPTH_IS_ZERO = depth == 0
        DEPTH_IS_MAX = depth == MAX_DEPTH[self.index_difficulty[self.turn_to.idt - 1]]

        align_score = [self.getAligned(p) for p in self.players]
        if DEPTH_IS_ZERO or self.over(align_score):
            return self.getScore(align_score, depth)

        if player.idt == 1:
            max_score = -np.inf
            max_score_move = None

            for move in self.getAllMoves(player):
                move_index, pos, direction = move

                if move_index == 0:
                    self.addToken(player, pos)
                else:
                    self.moveToken(player, pos, direction)

                score = self.minMax(depth - 1, alpha, beta, self.players[abs(player.idt - 2)])

                if move_index == 0:
                    self.removeToken(player, pos)
                else:
                    self.moveToken(player, pos + direction, -direction)

                if score > max_score:
                    max_score = score
                    max_score_move = move

                alpha = max(alpha, score)
                if beta <= alpha:
                    break

            if not DEPTH_IS_MAX:
                return max_score
            else:
                return max_score, max_score_move

        else:
            min_score = np.inf
            min_score_move = None

            for move in self.getAllMoves(player):
                move_index, pos, direction = move

                if move_index == 0:
                    self.addToken(player, pos)
                else:
                    self.moveToken(player, pos, direction)

                score = self.minMax(depth - 1, alpha, beta, self.players[abs(player.idt - 2)])

                if move_index == 0:
                    self.removeToken(player, pos)
                else:
                    self.moveToken(player, pos + direction, -direction)

                if score < min_score:
                    min_score = score
                    min_score_move = move

                beta = min(beta, score)
                if beta <= alpha:
                    break

            if not DEPTH_IS_MAX:
                return min_score
            else:
                return min_score, min_score_move

    def makeMove(self, move):
        if move[0] == 0:
            _, position, _ = move
            self.addToken(self.turn_to, position)
            if self.render_enabled:
                AI_tokens = [token for token in self.players_tokens if token[0] == self.turn_to.idt]

                for drop_zones in self.plate.playable_zones:
                    div, mod = divmod(position, 5)
                    if drop_zones.abscisse == mod and drop_zones.ordonne == div:
                        drop_zones.available = False
                        AI_tokens[len(self.turn_to.tokens) - 1][2].placeToken((drop_zones.x, drop_zones.y))
                        break

        else:
            _, token, direction = move
            self.moveToken(self.turn_to, token, direction)

            if self.render_enabled:
                AI_tokens = [token for token in self.players_tokens if token[0] == self.turn_to.idt]

                current_drop_zone, future_drop_zone, i = None, None, 0
                while current_drop_zone is None or future_drop_zone is None:
                    drop_zone = self.plate.playable_zones[i]
                    div, mod = divmod(token, 5)
                    if current_drop_zone is None and drop_zone.abscisse == mod and drop_zone.ordonne == div:
                        current_drop_zone = drop_zone
                    div, mod = divmod(token + direction, 5)
                    if future_drop_zone is None and drop_zone.abscisse == mod and drop_zone.ordonne == div:
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
        print('\nGrid before : \n', self.rectGrid())
        score, move = self.minMax(MAX_DEPTH[self.index_difficulty[self.turn_to.idt - 1]], -np.inf, np.inf, self.turn_to)
        print('Score : ', score, ' | Selected move : ', move)
        self.makeMove(move)

    def update(self):
        if not self.game_ended:
            if not self.turn_to.has_played:
                if self.turn_to.ptype == 1 and not self.calculating():
                    if self.turn != 0:
                        self.minmax_thread = threading.Thread(target=self.AI_handler)
                        self.minmax_thread.start()

                    else:
                        self.makeMove(self.getRandomMove(self.turn_to.idt))

                elif self.turn_to.ptype == 2:
                    print(self.getState(reverse=self.turn_to.idt == 2))
                    preds = self.dqn_agent.predict(self.getState(reverse=self.turn_to.idt == 2))
                    preds, move = self.correctMove(preds, self.turn_to.idt)
                    print('Predicted move: ', move)
                    self.makeMove(move)

            else:
                self.turn += 1
                print(f'P{self.turn_to.idt} align : {self.getAligned(self.turn_to)}, tokens : {self.turn_to.tokens}')

                if self.over():
                    self.won()

                self.turn_to.has_played = False
                self.turn_to = self.players[abs(self.turn_to.idt - 2)]

    def step(self, move, player_idt):
        self.turn_to = self.players[player_idt - 1]
        self.makeMove(move)
        return self.over()

    def getState(self, reverse=False):
        state = np.zeros((3, 5, 5), dtype=np.float)
        rect = self.rectGrid()
        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                state[rect[j][i]][j][i] = 1.
        if reverse:
            state[[1, 2]] = state[[2, 1]]
        return state

    def getRandomMove(self, player_idt):
        return randomChoice(self.getAllMoves(self.players[player_idt - 1]))

    def correctMove(self, preds, player_idt):
        correct_moves = self.getAllMoves(self.players[player_idt - 1])
        correct_preds_filter = np.sum([moveToPreds(move) for move in correct_moves], axis=0)
        lower_bound = np.min(preds)
        preds = ((preds - lower_bound) * correct_preds_filter) + lower_bound
        return preds, predsToMove(preds)

    def render(self):
        mouse_pos = pygame.mouse.get_pos()

        self.surf.fill(BACKGROUND)
        self.surf.blit(self.player_one, self.player_one_rect)
        self.surf.blit(self.player_two, self.player_two_rect)

        if self.error_trigger_code == 1:
            self.surf.blit(self.error_txt_1, self.error_txt_1_rect)
        elif self.error_trigger_code == 2:
            self.surf.blit(self.error_txt_2, self.error_txt_2_rect)

        if self.turn_to.idt == 1:
            self.angle = (self.angle + 2) % 360
            rotated_surf = pygame.transform.rotate(self.currentlyplaying, self.angle)
            self.currentlyplaying_rect = rotated_surf.get_rect(center=HOURGLASS_CENTER_ONE)
        else:
            self.angle = (self.angle + 2) % 360
            rotated_surf = pygame.transform.rotate(self.currentlyplaying, self.angle)
            self.currentlyplaying_rect = rotated_surf.get_rect(center=HOURGLASS_CENTER_TWO)

        self.surf.blit(rotated_surf, self.currentlyplaying_rect)

        if self.back_btn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.back_btn.hover(self.surf)
        else:
            self.back_btn.drawRect(self.surf)

        self.plate.render()
        for token_view in self.players_tokens:
            if token_view[0] == 1:
                token_view[2].render()
            elif token_view[0] == 2:
                token_view[2].render()

        if self.game_ended:
            background_end = pygame.Surface(SCREEN_SIZE)
            background_end.fill(GRAY)
            background_end.set_alpha(150)
            self.surf.blit(background_end, (0, 0))

            bandeau = pygame.Surface((SCREEN_SIZE[0], 400))
            bandeau.fill(BACKGROUND)
            bandeau.set_alpha(210)
            self.surf.blit(bandeau, BANDEAU_POSITION)

            if self.retry_btn.get_rect().collidepoint(mouse_pos):
                self.retry_btn.hover(self.surf)
            else:
                self.retry_btn.drawRect(self.surf)

            if self.goto_menu.get_rect().collidepoint(mouse_pos):
                self.goto_menu.hover(self.surf)
            else:
                self.goto_menu.drawRect(self.surf)

            if self.leave_game.get_rect().collidepoint(mouse_pos):
                self.leave_game.hover(self.surf)
            else:
                self.leave_game.drawRect(self.surf)

            self.surf.blit(self.winner_annouced, self.winner_annouced_rect)

    def parseEvent(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_btn.on_button(mouse_pos):
                return CODE_TO_MENU

            if self.game_ended:
                if self.goto_menu.on_button(mouse_pos):
                    self.game_ended = False
                    return CODE_TO_MENU

                if self.leave_game.on_button(mouse_pos):
                    pygame.quit()
                    self.killMinMax()
                    quit()

                if self.retry_btn.on_button(mouse_pos):
                    self.game_ended = False
                    return CODE_TO_GAME

            for token_view in self.players_tokens:
                if token_view[2].on_token(mouse_pos) and not token_view[3] and self.turn_to.idt == token_view[0]:
                    self.selected_token = token_view[2]
                    self.selection_offset_x = token_view[2].x - mouse_pos[0]
                    self.selection_offset_y = token_view[2].y - mouse_pos[1]

        if event.type == pygame.MOUSEBUTTONUP:
            if self.selected_token is not None:
                for drop_zone in self.plate.playable_zones:
                    if drop_zone.isAvailable() and drop_zone.onPropzone(mouse_pos) and \
                            drop_zone.legitMove(self.selected_token, len(self.turn_to.tokens)):
                        current_drop_zone, i = None, 0
                        while i < len(self.plate.playable_zones) and current_drop_zone is None:
                            iter_drop_zone = self.plate.playable_zones[i]
                            if self.selected_token.initial_x == iter_drop_zone.x and \
                                    self.selected_token.initial_y == iter_drop_zone.y:
                                current_drop_zone = iter_drop_zone
                            i += 1
                        if current_drop_zone is not None:
                            if len(self.turn_to.tokens) < 4:
                                self.error_trigger_code = 2
                                break

                            self.removeToken(self.turn_to, 5 * current_drop_zone.ordonne + current_drop_zone.abscisse)
                            current_drop_zone.available = True

                        self.addToken(self.turn_to, 5 * drop_zone.ordonne + drop_zone.abscisse)
                        self.selected_token.placeToken((drop_zone.x, drop_zone.y))
                        drop_zone.available = False

                        self.selected_token = None
                        self.turn_to.has_played = True
                        self.error_trigger_code = 0
                        break

                if self.selected_token is not None:
                    self.selected_token.placeToken((self.selected_token.initial_x, self.selected_token.initial_y))
                    self.selected_token = None
                    self.error_trigger_code = max(self.error_trigger_code, 1)

        if event.type == pygame.MOUSEMOTION:
            if self.selected_token is not None:
                self.selected_token.drag((self.selection_offset_x + mouse_pos[0],
                                          self.selection_offset_y + mouse_pos[1]))

    def rectGrid(self):
        return self.grid.reshape((GRID_SIZE, GRID_SIZE))

    def print(self):
        print(self.rectGrid())
