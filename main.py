import os

import pygame

from src.constants import *
from src.env import Teeko
from src.menu import Menu
from src.rules import Rules
from src.views import PageManager


def main():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (200, 40)
    pygame.init()
    pygame.display.set_caption('Teeko-AI')
    icon = pygame.image.load('resources/Teeko_logo.png')
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()

    page_manager = PageManager()

    display = pygame.display.set_mode(SCREEN_SIZE)
    game = Teeko(pygame.Surface(SCREEN_SIZE))
    menu = Menu(pygame.Surface(SCREEN_SIZE))
    rules = Rules(pygame.Surface(SCREEN_SIZE))
    page_manager.setPage(menu)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                game.killMinMax()
                quit()

            code = page_manager.current.parseEvent(event)

            if code == CODE_TO_GAME:
                game.reset(players=(menu.playerone, menu.playertwo),
                           index_difficulty=(menu.index_difficulty_one, menu.index_difficulty_two))
                page_manager.transitionTo(game)

            elif code == CODE_TO_MENU:
                game.killMinMax()
                page_manager.transitionTo(menu, reverse=True)

            elif code == CODE_TO_RULES:
                page_manager.transitionTo(rules)

        if page_manager.current == game and page_manager.ready():
            game.update()

        page_manager.current.render()

        page_manager.blit(display)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
