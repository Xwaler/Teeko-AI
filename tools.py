import numpy as np

from constants import DIRECTIONS


def randomChoice(a):
    return a[np.random.randint(len(a))]


def predsToMove(preds):
    if np.max(preds[:25]) > np.max(preds[25:]):
        move = [0, np.argmax(preds[:25]), 0]
    else:
        p, d = divmod(np.argmax(preds[25:]), 8)
        move = [1, p, DIRECTIONS[d]]
    return move


def moveToPreds(move):
    preds = np.zeros(25 + (25 * 8), dtype=np.float)
    if move[0] == 0:
        preds[move[1]] = 1.
    else:
        preds[25 + (move[1] * 8) + DIRECTIONS.index(move[2])] = 1.
    return preds
