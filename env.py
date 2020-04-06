import sys
from copy import deepcopy

from tools import *


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


class State:
    def __init__(self):
        self.grid = None
        self.players = None

    def __random_start__(self):
        self.grid = np.empty((GRID_SIZE, GRID_SIZE), dtype=Token)

        self.players = np.empty(2, dtype=Player)
        for i in [1, 2]:
            self.players[i - 1] = Player(i, AI=True)

        for player in self.players:
            j = 0
            while j < 4:
                pos = np.random.randint(0, 5, 2)
                if self.grid[pos[0]][pos[1]] is None:
                    self.addToken(player, pos)
                    j += 1
        return self

    def getSurrounding(self, token):
        directions = []

        for shift in SURROUNDING:

            if (0 <= token.pos[0] + shift[0] < 5 and 0 <= token.pos[1] + shift[1] < 5 and self.grid[token.pos[0] + shift[0]][
                token.pos[1] + shift[1]] == self.grid[token.pos[0]][token.pos[1]]) or (
                    0 <= token.pos[0] - shift[0] < 5 and 0 <= token.pos[1] - shift[1] < 5 and self.grid[token.pos[0] - shift[0]][
                token.pos[1] - shift[1]] == self.grid[token.pos[0]][token.pos[1]]):
                directions.append(shift)

        return directions

    def getAligned(self, player):
        longestLine = 1

        for token in player.tokens:

            for direction in self.getSurrounding(token):

                if not (direction == [-1, -1] and (np.abs(token.pos[0] - token.pos[1]) > 1) or direction == [-1, 1] and (
                        token.pos[0] + token.pos[1] > 5 or token.pos[0] + token.pos[1] < 3)):

                    i = 1

                    currentLine = 1

                    while 0 <= token.pos[0] + i * direction[0] < 5 and 0 <= token.pos[1] + i * direction[1] < 5 and \
                            self.grid[token.pos[0] + i * direction[0]][token.pos[1] + i * direction[1]] == player.idt:
                        currentLine = currentLine + 1
                        i = i + 1

                    i = -1

                    while 0 <= token.pos[0] + i * direction[0] < 5 and 0 <= token.pos[1] + i * direction[1] < 5 and \
                            self.grid[token.pos[0] + i * direction[0]][token.pos[1] + i * direction[1]] == player.idt:
                        currentLine = currentLine + 1
                        i = i - 1

                    if longestLine < currentLine:

                        longestLine = currentLine

                        if longestLine > 2:
                            return longestLine

        return longestLine

    def addToken(self, player, pos):
        token = Token(player, pos)
        self.grid[pos[0]][pos[1]] = token
        player.tokens.append(token)

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

        for token in player.tokens:
            moves.extend(self.getPossibleMove(token))

        if len(player.tokens) < 4:
            placement_move = [[0, pos.tolist(), [0, 0]] for pos in self.getAllEmpty()]
            moves.extend(placement_move)

        return moves

    def getAllEmpty(self):
        positions = []
        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                if self.grid[j][i] is None:
                    positions.append((j, i))
        return positions

    def over(self):
        # TODO: ALED GUILLAUME
        # return max(self.getAligned(1), self.getAligned(2)) >= 4

        longestAlignment = 1

        for player in self.players:

            playerLongestAlignment = self.getAligned(player)

            if playerLongestAlignment > longestAlignment:
                longestAlignment = playerLongestAlignment

        return bool(longestAlignment >= 4)

    def get_score(self, player):
        max_align = self.getAligned(player)
        return max_align * (-1 if player.idt == 2 else 1)


class Teeko:
    def __init__(self, surf):
        self.surf = surf
        self.state = State().__random_start__()
        self.turn_to = randomChoice(self.state.players)

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
    def minMax(self, move, current_state, depth, alpha, beta, maximizing_player, primary_player_idt):
        new_state = deepcopy(current_state)

        player = new_state.players[primary_player_idt - 1]
        other_player = new_state.players[abs(primary_player_idt - 2)]

        if move[0] == 0:
            new_state.addToken(player, move[1])
        else:
            new_state.moveToken(new_state.grid[move[1][0]][move[1][1]], move[2])

        if depth == 0 or new_state.over():
            return new_state.get_score(player)

        if maximizing_player:
            max_score = -np.inf

            for child_move in new_state.getAllMoves(player):
                score = self.minMax(child_move, new_state, depth - 1, alpha, beta, False, primary_player_idt)
                max_score = np.max([max_score, score])

                alpha = np.max([alpha, score])
                if beta <= alpha:
                    break
            return max_score

        else:
            min_score = np.inf

            for child_move in new_state.getAllMoves(other_player):
                score = self.minMax(child_move, new_state, depth - 1, alpha, beta, True, primary_player_idt)
                min_score = np.min([min_score, score])

                beta = np.min([beta, score])
                if beta <= alpha:
                    break
            return min_score

    def update(self):
        player = self.turn_to

        if player.AI:
            possible_moves = self.state.getAllMoves(player)
            scores = np.empty(len(possible_moves))
            for i, move in enumerate(possible_moves):
                scores[i] = self.minMax(move, self.state, 2,
                                        np.max(scores) if player.idt == 1 else -np.inf,
                                        np.min(scores) if player.idt == 2 else np.inf,
                                        player.idt != 1, player.idt)
            print(player.idt, list(zip(possible_moves, scores)))

            if player.idt == 1:
                move = possible_moves[np.argmax(scores)]
            else:
                move = possible_moves[np.argmin(scores)]

            if move[0] == 0:
                self.state.addToken(player, move[1])
            else:
                self.state.moveToken(self.state.grid[move[1][0]][move[1][1]], move[2])
            player.has_played = True

        else:
            # waits about a sec
            if np.random.random() < 1 / 60:
                player.has_played = True

        if player.has_played:
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

        pygame.draw.rect(self.surf,BLACK,( (SCREEN_SIZE[0]-self.square_width*GRID_SIZE)/2,(SCREEN_SIZE[1]-self.square_width*GRID_SIZE)/2,self.square_width*GRID_SIZE , self.square_width*GRID_SIZE),3)

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                pygame.draw.circle(self.surf, RED if self.state.grid[j][i] == 2 else BLACK,((i * self.square_width + self.square_width // 2)+int((SCREEN_SIZE[0]-self.square_width*GRID_SIZE)/2), j * self.square_width + self.square_width // 2+int((SCREEN_SIZE[1]-self.square_width*GRID_SIZE)/2)),TOKEN_RADIUS, TOKEN_THICKNESS if self.state.grid[j][i] == 0 else 0)

    def parse_event(self, event):
        pass

    def print(self):
        print(self.grid)
        sys.stdout.flush()
