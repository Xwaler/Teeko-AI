import numpy as np


def randomChoice(a):
    return a[np.random.randint(len(a))]


def orderTokens(tokens):
    return sorted(tokens, key=lambda x: (x[0], x[1]), reverse=True)
