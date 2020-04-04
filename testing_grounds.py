import numpy as np

gameGridO = np.zeros((5, 5))
playerPos = np.full((2, 4, 2), 6)
SURROUNDING = [[-1, -1], [-1, 0], [-1, 1], [0, -1]]


def placeToken(line, column, player):
    if gameGridO[line][column] == 0:

        gameGridO[line][column] = player

        i = 0

        while playerPos[player - 1][i][0] != 6 and i < 3:
            i = i + 1

        playerPos[player - 1][i][0] = line
        playerPos[player - 1][i][1] = column

        return 0
    return 1


def randomStart():
    # placeToken(0, 0, 2)
    # placeToken(0, 2, 2)
    # placeToken(1, 1, 2)
    # placeToken(2, 0, 2)

    for j in [1, 2]:

        i = 0

        while i != 4:
            if placeToken(np.random.randint(5), np.random.randint(5), j) == 0:
                i = i + 1


def getSurrounding(token, gameGrid):
    directions = []

    for shift in SURROUNDING:

        if (0 <= token[0] + shift[0] < 5 and 0 <= token[1] + shift[1] < 5 and gameGrid[token[0] + shift[0]][
            token[1] + shift[1]] == gameGrid[token[0]][token[1]]) or (
                0 <= token[0] - shift[0] < 5 and 0 <= token[1] - shift[1] < 5 and gameGrid[token[0] - shift[0]][
            token[1] - shift[1]] == gameGrid[token[0]][token[1]]):
            directions.append(shift)

    return directions


def getAligned(player, gameGrid):
    longestLine = 1

    for token in playerPos[player - 1]:

        for direction in getSurrounding(token, gameGrid):

            if not (direction == [-1, -1] and (np.abs(token[0] - token[1]) > 1) or direction == [-1, 1] and (
                    token[0] + token[1] > 5 or token[0] + token[1] < 3)):

                i = 1

                currentLine = 1

                while 0 <= token[0] + i * direction[0] < 5 and 0 <= token[1] + i * direction[1] < 5 and \
                        gameGrid[token[0] + i * direction[0]][token[1] + i * direction[1]] == player:
                    currentLine = currentLine + 1
                    i = i + 1

                i = -1

                while 0 <= token[0] + i * direction[0] < 5 and 0 <= token[1] + i * direction[1] < 5 and \
                        gameGrid[token[0] + i * direction[0]][token[1] + i * direction[1]] == player:
                    currentLine = currentLine + 1
                    i = i - 1

                if longestLine < currentLine:

                    longestLine = currentLine

                    if longestLine > 2:
                        return longestLine

    return longestLine


def getAllMoves(player, gameGrid):
    moves = []

    for token in playerPos[player - 1]:

        currentTokenMoves = []

        for shift in SURROUNDING:

            if 0 <= token[0] + shift[0] < 5 and 0 <= token[1] + shift[1] < 5 and gameGrid[token[0] + shift[0]][
                token[1] + shift[1]] == 0:
                currentTokenMoves.append([token, shift])

            if 0 <= token[0] - shift[0] < 5 and 0 <= token[1] - shift[1] < 5 and gameGrid[token[0] - shift[0]][
                token[1] - shift[1]] == 0:
                currentTokenMoves.append([token, [-shift[0], -shift[1]]])

        moves.append(currentTokenMoves)
    return moves


def evaluateMove(move, gameGrid):
    i = 1


def moveToken(move, gameGrid):
    gameGrid[move[0][0] + move[1][0]][move[0][1] + move[1][1]] = gameGrid[move[0][0]][move[0][1]]
    gameGrid[move[0][0]][move[0][1]] = 0


randomStart()

print(gameGridO)
print("Position jetons joueurs :")
print(playerPos)

print("Nombre jetons alignés joueur 1 :")
print(getAligned(1, gameGridO))
print("Nombre jetons alignés joueur 2:")
print(getAligned(2, gameGridO))

print(getAllMoves(1, gameGridO))

print(getAllMoves(2, gameGridO))
