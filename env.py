import math
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


class TokenView:
    def __init__(self, surf, x, y):
        self.surf = surf
        self.x, self.y = x, y
        self.initialx, self.initialy = x, y
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
        self.initialx, self.initialy = pos

    def drag(self, pos):
        self.x, self.y = pos


class Player:
    def __init__(self, i, AI=True):
        self.idt = i
        self.AI = AI
        self.tokens = []
        self.has_played = False

    def __repr__(self):
        return self.idt.__repr__()


class PlayableZone:
    def __init__(self, surf, x, y,i,j):
        self.surf = surf
        self.x = x
        self.y = y
        self.abscisse = i
        self.ordonne = j
        self.available = True

    def draw(self):
        pygame.draw.circle(self.surf, BLACK, (self.x, self.y), TOKEN_RADIUS+5, TOKEN_THICKNESS)

    def on_dropzone(self, pos):
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
        self.playableZones = []
        self.square_width = square_width

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                self.playableZones.append(
                    PlayableZone(self.surf, (i * self.square_width + self.square_width // 2) + int(
                        (SCREEN_SIZE[0] - self.w) / 2),
                                 j * self.square_width + self.square_width // 2 + int(
                                     (SCREEN_SIZE[1] - self.w) / 2),i,j))

    def drawPlate(self):
        pygame.draw.rect(self.surf, BLACK, (self.x, self.y, self.w, self.w), 3)

        for playableZone in self.playableZones:
            playableZone.draw()


class Teeko:
    def __init__(self, surf):
        self.surf = surf
        self.grid = np.empty((GRID_SIZE, GRID_SIZE), dtype=Token)
        self.players = np.empty(2, dtype=Player)
        for i in [1, 2]:
            self.players[i - 1] = Player(i, AI=i == 1)
        self.turn_to = randomChoice(self.players)
        self.indexdifficulty = 0

        self.playerstokens = []
        self.end_last_turn = 0
        self.playerscolors = []

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

        for k in range(0, 2):
            for m in range(0, 4):
                self.playerstokens.append(
                    (k+1, m+1, TokenView(
                        self.surf, (int((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4) + (
                                k * int(self.square_width * GRID_SIZE + (SCREEN_SIZE[0] -
                                                                         self.square_width * GRID_SIZE) / 2))),
                        m * (TOKEN_RADIUS * 2 + 30) + 250
                    ), False if self.players[k].AI is True else True)
                )

        self.backbtn = Button((SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 4 - 75, SCREEN_SIZE[1] - 80, 150, 50,
                              '< Back', BACKGROUND)

        self.plate = Plate(surf, (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 2,
                           (SCREEN_SIZE[1] - self.square_width * GRID_SIZE) / 2,
                           self.square_width * GRID_SIZE, self.square_width)
        self.token_dragging = False
        self.initialToken = TokenView(self.surf, 0, 0)
        self.selectedtoken = self.initialToken
        self.offset_Y = 0
        self.offset_X = 0

    def getAligned(self, player):
        longestLine = 1

        for token in player.tokens:
            for direction in DIRECTIONS:
                if not (direction == (-1, -1) and (np.abs(token.pos[0] - token.pos[1]) > 1) or
                        direction == (-1, 1) and (token.pos[0] + token.pos[1] > 5 or token.pos[0] + token.pos[1] < 3)):

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
        return self.getAligned(player) >= 4

    def get_score(self):
        p1 = self.getAligned(self.players[0])
        # print("p1 : ", p1)
        p2 = self.getAligned(self.players[1])
        # print("p2 : ", p2)
        return p1 - p2

    #  move = (0, (pos token à placer), (0, 0)) ou (1, (pos token à deplacer), (direction))
    def minMax(self, move, depth, alpha, beta, maximizing_player, player_id):
        if self.kill_thread:
            raise SystemExit()

        DEPTH_IS_ZERO = depth == 0
        DEPTH_IS_MAX = depth == MAX_DEPTH[self.indexdifficulty]
        PLACEMENT = move is not None and move[0] == 0

        # print("\n\ndepth : ", depth)

        # print("state : \n", self.grid)

        player = self.players[player_id - 1]

        # print("player : ", player.idt)

        # print("move : ", move)

        if move is not None:
            if PLACEMENT:
                self.addToken(player, move[1])
            else:
                self.moveToken(self.grid[move[1][0]][move[1][1]], move[2])

            # print("state after move : \n", self.grid)

            if DEPTH_IS_ZERO or self.over(player):
                if PLACEMENT:
                    self.removeToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                   [-move[2][0], -move[2][1]])

                return self.get_score()

        if maximizing_player:
            max_score = -np.inf
            max_score_moves = []

            for child_move in self.getAllMoves(player):
                score = self.minMax(child_move, depth - 1, alpha, beta, False, abs(player_id - 1))

                # print("score : ", score)

                if score >= max_score:
                    max_score = score
                    max_score_moves = []

                if DEPTH_IS_MAX and score == max_score:
                    max_score_moves.append(child_move)

                alpha = np.max([alpha, score])
                if beta <= alpha:
                    break

            if move is not None:
                if PLACEMENT:
                    self.removeToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                   [-move[2][0], -move[2][1]])

            if not DEPTH_IS_MAX:
                return max_score
            else:
                return randomChoice(max_score_moves)

        else:
            min_score = np.inf
            min_score_moves = []

            for child_move in self.getAllMoves(player):
                score = self.minMax(child_move, depth - 1, alpha, beta, True, abs(player_id - 1))

                # print("score : ", score)

                if score < min_score:
                    min_score = score
                    min_score_moves = []

                if DEPTH_IS_MAX and score == min_score:
                    min_score_moves.append(child_move)

                beta = np.min([beta, score])
                if beta <= alpha:
                    break

            if move is not None:
                if PLACEMENT:
                    self.removeToken(player, move[1])
                else:
                    self.moveToken(self.grid[move[1][0] + move[2][0]][move[1][1] + move[2][1]],
                                   [-move[2][0], -move[2][1]])

            if not DEPTH_IS_MAX:
                return min_score
            else:
                return randomChoice(min_score_moves)

    def AI_handler(self, player):
        move = self.minMax(None, MAX_DEPTH[self.indexdifficulty], -np.inf, np.inf, player.idt == 1, player.idt)
        # print('Selected move : ', move)

        # TODO: update TokenView ???
        if move[0] == 0:
            self.addToken(player, move[1])
        else:
            self.moveToken(self.grid[move[1][0]][move[1][1]], move[2])

        self.end_last_turn = time.time()
        self.minmax_thread = None
        player.has_played = True

    def update(self):
        if time.time() > self.end_last_turn + 1:  # TEMPORAIRE : waits about a sec between turns
            if self.over(self.players[1]):
                print("P2 win")
                print("state : \n", self.grid)
                i = 1/0
            elif self.over(self.players[0]):
                print("P1 Win")
                print("state : \n", self.grid)
                i = 1/0
            else:
                player = self.turn_to
                if not player.has_played:
                    if player.AI and self.minmax_thread is None:
                        self.minmax_thread = threading.Thread(target=self.AI_handler, args=(player,))
                        self.minmax_thread.start()

                    # else:
                    #     # TODO: allow human player to move his tokens
                    #     player.has_played = True  # TODO: move that to parse_event, somewhere

                else:
                    self.turn_to = self.players[abs(np.where(self.players == player)[0][0] - 1)]
                    player.has_played = False

    def render(self):
        self.surf.fill(BACKGROUND)

        self.surf.blit(self.playerone, self.playeronerect)
        self.surf.blit(self.playertwo, self.playertworect)

        if self.backbtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.backbtn.hover(self.surf)
        else:
            self.backbtn.drawRect(self.surf)

        self.plate.drawPlate()

        for Tokens in self.playerstokens:
            if Tokens[0] == 0:
                Tokens[2].render(self.playerscolors[0])
            elif Tokens[0] == 1:
                Tokens[2].render(self.playerscolors[1])

    # for j in range(GRID_SIZE):
    #     for i in range(GRID_SIZE):
    #         pygame.draw.circle(self.surf,
    #                            self.playerscolors[1] if self.grid[j][i] is not None and (
    #                                    self.grid[j][i].player.idt == 2) else self.playerscolors[0] if (
    #                                    self.grid[j][i] is not None and self.grid[j][i].player.idt == 1) else BLACK,
    #                            (
    #                                (i * self.square_width + self.square_width // 2) + int(
    #                                    (SCREEN_SIZE[0] - self.square_width * GRID_SIZE) / 2),
    #                                j * self.square_width + self.square_width // 2 + int(
    #                                    (SCREEN_SIZE[1] - self.square_width * GRID_SIZE) / 2)), TOKEN_RADIUS,
    #                            TOKEN_THICKNESS if self.grid[j][i] is None else 0)

    def parse_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.backbtn.on_button(pos):
                return CODE_TO_MENU

            for TokenView in self.playerstokens:
                if TokenView[2].on_token(pos) and not TokenView[3] and self.turn_to.idt == TokenView[1]:
                    self.selectedtoken = TokenView[2]
                    self.offset_X = TokenView[2].x - pos[0]
                    self.offset_Y = TokenView[2].y - pos[1]
                    self.token_dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            if self.token_dragging:
                for dropZone in self.plate.playableZones:
                    if dropZone.on_dropzone(pos) and dropZone.isAvailable():
                        dropZone.available = False
                        self.selectedtoken.placeToken((dropZone.x, dropZone.y))
                        self.addToken(self.turn_to,(dropZone.abscisse,dropZone.ordonne))
                        # TODO: update grid and token objects ???
                        self.token_dragging = False
                        self.turn_to.has_played = True
                        break

                if self.token_dragging:
                    self.selectedtoken.placeToken((self.selectedtoken.initialx, self.selectedtoken.initialy))
                    self.token_dragging = False
            self.selectedtoken = self.initialToken

        if event.type == pygame.MOUSEMOTION:
            if self.token_dragging:
                newX = self.offset_X + pos[0]
                newY = self.offset_Y + pos[1]
                self.selectedtoken.drag((newX, newY))

    def print(self):
        print(self.grid)
