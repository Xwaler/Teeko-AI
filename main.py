import pygame

from constants import *
from env import Teeko


def main():
    pygame.init()
    pygame.display.set_caption('Teeko-AI')
    clock = pygame.time.Clock()

    display = pygame.display.set_mode(SCREEN_SIZE)
    teeko_surf = pygame.Surface((SCREEN_SIZE[1], SCREEN_SIZE[1]))

    game = Teeko()
    game.print()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                quit()

        game.update()
        game.render(teeko_surf)

        display.blit(teeko_surf, (0, 0))

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
