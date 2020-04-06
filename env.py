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
            self.players[i - 1] = Player(i, AI=i == 2)

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
                token_moves.append(shift)

            if 0 <= token.pos[0] - shift[0] < 5 and 0 <= token.pos[1] - shift[1] < 5 and \
                    self.grid[token.pos[0] - shift[0]][token.pos[1] - shift[1]] is None:
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
                if self.grid[j][i] is None:
                    positions.append((j, i))
        return positions

    def get_score(self, move):
        pass


class Teeko:
    def __init__(self, surf):
        self.surf = surf
        self.state = State().__random_start__()
        self.turn_to = randomChoice(self.state.players)

    #  move = (0, idt_player, (pos token à placer), (0, 0)) ou (1, idt_player, (pos token à deplacer), (direction))
    def minMax(self, move, current_state, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.over_if(move):
            return self.get_score(move)

        new_state = deepcopy(current_state)
        player = new_state.players[move[1]]
        if move[0] == 0:
            new_state.addToken(player, move[2])
        else:
            new_state.moveToken(new_state.grid[move[2][0]][move[2][1]], move[3])

        if maximizing_player:
            max_score = -np.inf

            for child_move in new_state.getAllMoves(player):
                pass

    def update(self):
        player = self.turn_to

        if player.AI:
            # TODO: replace random with min/max

            if np.random.random() < .5:  # place new token
                positions = self.state.getAllEmpty()
                pos = randomChoice(positions)
                self.state.addToken(player, pos)

            else:  # move token
                tokens_with_moves = self.state.getAllMoves(player)
                token = randomChoice(list(tokens_with_moves.keys()))
                direction = randomChoice(tokens_with_moves[token])
                self.state.moveToken(token, direction)

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
