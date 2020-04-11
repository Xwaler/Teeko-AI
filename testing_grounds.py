from env import Teeko

env = Teeko()
env.reset()

for _ in range(4):
    env.update()
    while env.calculating():
        continue
    env.update()
env.print()
