import sys
import threading
import time

from tools import *


class Token:
    def __init__(self, player, pos):
        self.pos = np.array(pos)
        self.player = player

    def __str__(self):
        return self.pos

    def __repr__(self):
        return self.player.__repr__()

    def move(self, direction):
        self.pos += direction


class Player:
    def __init__(self, i, AI=True):
        self.idt = i
        self.AI = AI
        self.tokens = []
        self.has_played = False

    def __repr__(self):
        return self.idt.__repr__()


class State:
    def __init__(self):
        self.grid = None
        self.players = None

    def __random_start__(self):
        self.grid = np.empty((GRID_SIZE, GRID_SIZE), dtype=Token)

        self.players = np.empty(2, dtype=Player)
        for i in [1, 2]:
            self.players[i - 1] = Player(i, AI=True)

        # for player in self.players:
        #     j = 0
        #     while j < 4:
        #         pos = np.random.randint(0, 5, 2)
        #         if self.grid[pos[0]][pos[1]] is None:
        #             self.addToken(player, pos)
        #             j += 1
        return self

    # def getSurrounding(self, token):
    #     directions = []
    #
    #     for shift in SURROUNDING:
    #
    #         if (0 <= token.pos[0] + shift[0] < 5 and 0 <= token.pos[1] + shift[1] < 5 and
    #             self.grid[token.pos[0] + shift[0]][
    #                 token.pos[1] + shift[1]] is not None and self.grid[token.pos[0] + shift[0]][
    #                 token.pos[1] + shift[1]].player.idt == self.grid[token.pos[0]][token.pos[1]].player.idt) or (
    #                 0 <= token.pos[0] - shift[0] < 5 and 0 <= token.pos[1] - shift[1] < 5 and
    #                 self.grid[token.pos[0] - shift[0]][
    #                     token.pos[1] - shift[1]] is not None and self.grid[token.pos[0] - shift[0]][
    #                     token.pos[1] - shift[1]].player.idt == self.grid[token.pos[0]][token.pos[1]].player.idt):
    #             directions.append(shift)
    #
    #     return directions

    def getAligned(self, player):
        longestLine = 1

        for token in player.tokens:

            for direction in DIRECTIONS:

                if not (direction == [-1, -1] and (np.abs(token.pos[0] - token.pos[1]) > 1) or direction == [-1,
                                                                                                             1] and (
                                token.pos[0] + token.pos[1] > 5 or token.pos[0] + token.pos[1] < 3)):

                    currentAlignment = 1

                    newline = token.pos[0] + direction[0]
                    newcolumn = token.pos[1] + direction[1]

                    while (0 <= newline < 5 and 0 <= newcolumn < 5 and self.grid[newline][newcolumn] is not None and
                           self.grid[newline][newcolumn].player.idt == self.grid[token.pos[0]][
                               token.pos[1]].player.idt):
                        newline = newline + direction[0]
                        newcolumn = newcolumn + direction[1]

                        currentAlignment += 1

                    newline = token.pos[0] - direction[0]
                    newcolumn = token.pos[1] - direction[1]

                    while (0 <= newline < 5 and 0 <= newcolumn < 5 and self.grid[newline][newcolumn] is not None and
                           self.grid[newline][newcolumn].player.idt == self.grid[token.pos[0]][
                               token.pos[1]].player.idt):
                        newline = newline - direction[0]
                        newcolumn = newcolumn - direction[1]

                        currentAlignment += 1

                    if currentAlignment > longestLine:
                        longestLine = currentAlignment
                    # i = 1
                    #
                    # currentLine = 1
                    #
                    # while 0 <= token.pos[0] + i * direction[0] < 5 and 0 <= token.pos[1] + i * direction[1] < 5 and \
                    #         self.grid[token.pos[0] + i * direction[0]][token.pos[1] + i * direction[1]] is not None and \
                    #         self.grid[token.pos[0] + i * direction[0]][
                    #             token.pos[1] + i * direction[1]].player.idt == player.idt:
                    #     currentLine = currentLine + 1
                    #     i = i + 1
                    #
                    # i = -1
                    #
                    # while 0 <= token.pos[0] + i * direction[0] < 5 and 0 <= token.pos[1] + i * direction[1] < 5 and \
                    #         self.grid[token.pos[0] + i * direction[0]][token.pos[1] + i * direction[1]] is not None and \
                    #         self.grid[token.pos[0] + i * direction[0]][
                    #             token.pos[1] + i * direction[1]].player.idt == player.idt:
                    #     currentLine = currentLine + 1
                    #     i = i - 1

                    if longestLine < currentAlignment:

                        longestLine = currentAlignment

                        if longestLine > 2:
                            return longestLine

        return longestLine

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

    def over(self, player):
        longestAlignment = 1
        playerLongestAlignment = self.getAligned(player)

        if playerLongestAlignment > longestAlignment:
            longestAlignment = playerLongestAlignment

        return longestAlignment >= 4

    def get_score(self):
        p1 = self.getAligned(self.players[0])
        print("p1 : ", p1)
        p2 = self.getAligned(self.players[1])
        print("p2 : ", p2)
        return p1 - p2


class Teeko:
    def __init__(self, surf):
        self.surf = surf
        self.state = State().__random_start__()
        self.turn_to = randomChoice(self.state.players)

        self.end_last_turn = 0
        self.playeronecolor = None
        self.playertwocolor = None

        self.minmax_thread = None
        self.kill_thread = False

        self.square_width = (SCREEN_SIZE[1] - 100) // GRID_SIZE

        self.font = pygame.font.Font('Amatic-Bold.ttf', 50)
        self.playerone = self.font.render('Player 1', True, BLACK)
        self.playeronerect = self.playerone.get_rect()
        self.playeronerect.center = (int((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4), 150)

        self.playertwo = self.font.render('Player 2', True, BLACK)
        self.playertworect = self.playertwo.get_rect()
        self.playertworect.center = (
            int(3 * (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4) + self.square_width * GRID_SIZE, 150)

        self.backbtn = Button((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4 - 75, SCREEN_SIZE[1] - 80, 150, 50,
                              '< Back', BACKGROUND)

    #  move = (0, (pos token à placer), (0, 0)) ou (1, (pos token à deplacer), (direction))
    def minMax(self, move, depth, alpha, beta, maximizing_player, player_id):
        if self.kill_thread:
            raise SystemExit()

        print("\n\ndepth : ", depth)

        print("state : \n", self.state.grid)

        player = self.state.players[player_id - 1]

        print("player : ", player.idt)

        print("move : ", move)

        if move is not None:
            if move[0] == 0:
                self.state.addToken(player, move[1])
            else:
                self.state.moveToken(self.state.grid[move[1][0]][move[1][1]], move[2])

            print("state after move : \n", self.state.grid)

            if depth == 0 or self.state.over(player):
                if move[0] == 0:
                    self.state.removeToken(player, move[1])
                else:
                    self.state.moveToken(self.state.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                         [-move[2][0], -move[2][1]])

                return self.state.get_score()

        if maximizing_player:
            max_score = -np.inf
            max_score_moves = []

            for child_move in self.state.getAllMoves(player):
                score = self.minMax(child_move, depth - 1, alpha, beta, False, abs(player_id - 1))

                print("score : ", score)

                if score >= max_score:
                    max_score = score
                    max_score_moves = []
                if score == max_score:
                    max_score_moves.append(child_move)

                alpha = np.max([alpha, score])
                if beta <= alpha:
                    break

            if move is not None:
                if move[0] == 0:
                    self.state.removeToken(player, move[1])
                else:
                    self.state.moveToken(self.state.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                         [-move[2][0], -move[2][1]])

            if depth != MAX_DEPTH:
                return max_score
            else:
                return randomChoice(max_score_moves)

        else:
            min_score = np.inf
            min_score_moves = []

            for child_move in self.state.getAllMoves(player):
                score = self.minMax(child_move, depth - 1, alpha, beta, True, abs(player_id - 1))

                print("score : ", score)

                if score < min_score:
                    min_score = score
                    min_score_moves = []
                if score == min_score:
                    min_score_moves.append(child_move)

                beta = np.min([beta, score])
                if beta <= alpha:
                    break

            if move is not None:
                if move[0] == 0:
                    self.state.removeToken(player, move[1])
                else:
                    self.state.moveToken(self.state.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                         [-move[2][0], -move[2][1]])

            if depth != MAX_DEPTH:
                return min_score
            else:
                return randomChoice(min_score_moves)

    def AI_handler(self, player):
        move = self.minMax(None, MAX_DEPTH, -np.inf, np.inf, player.idt == 1, player.idt)
        print('Selected move : ', move)

        if move[0] == 0:
            self.state.addToken(player, move[1])
        else:
            self.state.moveToken(self.state.grid[move[1][0]][move[1][1]], move[2])

        player.has_played = True
        self.minmax_thread = None
        self.end_last_turn = time.time()

    def update(self):
        if time.time() > self.end_last_turn + 1:  # TEMPORAIRE : waits about a sec between turns
            player = self.turn_to

            if not player.has_played:
                if player.AI and self.minmax_thread is None:
                    self.minmax_thread = threading.Thread(target=self.AI_handler, args=(player,))
                    self.minmax_thread.start()

                else:
                    # TODO
                    player.has_played = True

            else:
                self.turn_to = self.state.players[abs(np.where(self.state.players == player)[0][0] - 1)]
                player.has_played = False

    def render(self):
        self.surf.fill(BACKGROUND)

        self.surf.blit(self.playerone, self.playeronerect)
        self.surf.blit(self.playertwo, self.playertworect)

        if self.backbtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.backbtn.hover(self.surf)
        else:
            self.backbtn.drawRect(self.surf)

        pygame.draw.rect(self.surf, BLACK, (
            (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 2, (SCREEN_SIZE[1] - self.square_width * GRID_SIZE) / 2,
            self.square_width * GRID_SIZE, self.square_width * GRID_SIZE), 3)

        #Player One Token

        for k in range(TOKEN_NUMBER):
            pygame.draw.circle(self.surf,self.playeronecolor,(int((SCREEN_SIZE[0]-self.square_width*GRID_SIZE)/4), k*(TOKEN_RADIUS*2 + 30) + 250), TOKEN_RADIUS)
            pygame.draw.circle(self.surf, self.playertwocolor, (int((SCREEN_SIZE[0] - self.square_width * GRID_SIZE)*3 / 4) + self.square_width*GRID_SIZE, k * (TOKEN_RADIUS * 2 + 30) + 250), TOKEN_RADIUS)

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                pygame.draw.circle(self.surf,
                                   self.playertwocolor if self.state.grid[j][i] is not None and self.state.grid[j][
                                       i].player.idt == 2 else self.playeronecolor if self.state.grid[j][i] is not None and self.state.grid[j][
                                       i].player.idt == 1 else BLACK, (
                                       (i * self.square_width + self.square_width // 2) + int(
                                           (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 2),
                                       j * self.square_width + self.square_width // 2 + int(
                                           (SCREEN_SIZE[1] - self.square_width * GRID_SIZE) / 2)), TOKEN_RADIUS, TOKEN_THICKNESS if self.state.grid[j][i] is None else 0)

    def parse_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.backbtn.on_button(pos):
                return CODE_TO_MENU


    def print(self):
        print(self.grid)
        sys.stdout.flush()
