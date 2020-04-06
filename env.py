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
        return False

    def get_score(self, player):
        max_align = np.random.randint(0, 5)
        return max_align * (-1 if player.idt == 2 else 1)


class Teeko:
    def __init__(self, surf):
        self.surf = surf
        self.state = State().__random_start__()
        self.turn_to = randomChoice(self.state.players)

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
        square_width = SCREEN_SIZE[1] // GRID_SIZE
        self.surf.fill((200, 200, 200))

        for j in range(GRID_SIZE):
            for i in range(GRID_SIZE):
                pygame.draw.circle(self.surf,
                                   RED if self.state.grid[j][i] is not None and self.state.grid[j][i].player.idt == 2
                                   else BLACK,
                                   (i * square_width + square_width // 2, j * square_width + square_width // 2),
                                   TOKEN_RADIUS, TOKEN_THICKNESS if self.state.grid[j][i] is None else 0)

    def parse_event(self, event):
        pass

    def print(self):
        print(self.grid)
