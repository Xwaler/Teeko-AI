from env import Teeko
import numpy as np
from constants import *

env = Teeko()
env.reset()

env.addToken(env.players[0], 0)
env.addToken(env.players[0], 6)
env.addToken(env.players[0], 10)
env.addToken(env.players[1], 12)


env.print()
print(env.getAligned(env.players[0]))


