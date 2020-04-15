from env import Teeko
import numpy as np

env = Teeko()
env.reset()

env.addToken(env.players[0], 20)
env.addToken(env.players[0], 15)
env.addToken(env.players[0], 10)
env.addToken(env.players[1], 5)


env.print()
print(env.getAligned(env.players[0]))
