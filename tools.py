import numpy as np

from constants import DIRECTIONS


def randomChoice(a):
    return a[np.random.randint(len(a))]


def predsToMove(preds):
    move = [np.argmax(preds[:2]),
            np.argmax(preds[2:27]),
            DIRECTIONS[np.argmax(preds[27:35])]]
    return move


def moveToPreds(move):
    preds = np.zeros(2 + 25 + 8, dtype=np.float)
    preds[move[0]] = 1.
    preds[2 + move[1]] = 1.
    if move[0] == 1:
        preds[2 + 25 + DIRECTIONS.index(move[2])] = 1.
    return preds
