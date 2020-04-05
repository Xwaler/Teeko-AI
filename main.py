import pygame

from constants import *
from env import Teeko
from menu import Menu
from tools import PageManager


def main():
    pygame.init()
    pygame.display.set_caption('Teeko-AI')
    clock = pygame.time.Clock()

    page_manager = PageManager()

    display = pygame.display.set_mode(SCREEN_SIZE)
    game = Teeko(pygame.Surface((SCREEN_SIZE[1], SCREEN_SIZE[1])))
    menu = Menu(pygame.Surface(SCREEN_SIZE))

    page_manager.setPage(menu)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                quit()

            code = page_manager.current.parse_event(event)

            if code == CODE_TO_GAME:
                page_manager.current = game
            elif code == CODE_TO_MENU:
                page_manager.current = menu

        if page_manager.current == game:
            game.update()

        display.fill(BACKGROUND)
        page_manager.current.render()
        display.blit(page_manager.current.surf, (0, 0))

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
