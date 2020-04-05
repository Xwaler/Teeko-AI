import pygame

from constants import *
from env import Teeko, Button, ColorChanger


def main():
    pygame.init()
    pygame.display.set_caption('Teeko-AI')
    clock = pygame.time.Clock()

    display = pygame.display.set_mode(SCREEN_SIZE)
    teeko_surf = pygame.Surface((SCREEN_SIZE[1], SCREEN_SIZE[1]))
    font = pygame.font.Font('Amatic-Bold.ttf',180)
    title = font.render('Teeko AI',True,BLACK)
    titleRect = title.get_rect()
    titleRect.center = (SCREEN_SIZE[0]/2,200)

    INDEXCOLORONE = 0
    INDEXCOLORTWO = 1

    colorbtnone = ColorChanger(int((SCREEN_SIZE[0]-400)/2), int((SCREEN_SIZE[1] - 30) / 2 + 30), 30, COLORS[INDEXCOLORONE])
    colorbtntwo = ColorChanger(int((SCREEN_SIZE[0]-400)/2+300), int((SCREEN_SIZE[1] - 30) / 2 + 30), 30, COLORS[INDEXCOLORTWO])

    font = pygame.font.Font('Amatic-Bold.ttf', 50)
    playerone = font.render('Player 1', True, BLACK)
    playeronerect = playerone.get_rect()
    playeronerect.center = (int((SCREEN_SIZE[0]-300)/2+50),(SCREEN_SIZE[1] - 30) / 2 + 30)

    font = pygame.font.Font('Amatic-Bold.ttf', 50)
    playertwo = font.render('Player 2', True, BLACK)
    playertworect = playertwo.get_rect()
    playertworect.center = (int((SCREEN_SIZE[0]-300)/2+350), (SCREEN_SIZE[1] - 30) / 2 + 30)

    startbtn = Button((SCREEN_SIZE[0] - 200) / 2, (SCREEN_SIZE[1] - 50) / 2 + 150, 200, 50, 'Start', BACKGROUND)
    leavebtn = Button((SCREEN_SIZE[0]-200)/2,(SCREEN_SIZE[1]-50)/2 + 220, 200, 50, 'Leave', BACKGROUND)

    game = Teeko()
    game.print()

    while True:
        game.update()

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if startbtn.on_button(pos):
                    game.render(teeko_surf)
                    display.blit(teeko_surf, (0, 0))
                if leavebtn.on_button(pos):
                    pygame.quit()
                    quit()
                if colorbtnone.changeColor(pos):
                    if INDEXCOLORONE +1 < len(COLORS):
                        if INDEXCOLORONE + 1 != INDEXCOLORTWO:
                            INDEXCOLORONE += 1
                        else:
                            INDEXCOLORONE += 2
                    else:
                        if INDEXCOLORTWO == 0:
                            INDEXCOLORONE = 1
                        else:
                            INDEXCOLORONE = 0
                if colorbtntwo.changeColor(pos):
                    if INDEXCOLORTWO + 1 < len(COLORS):
                        if INDEXCOLORTWO + 1 != INDEXCOLORONE:
                            INDEXCOLORTWO += 1
                        else:
                            INDEXCOLORTWO += 2
                    else:
                        if INDEXCOLORONE == 0:
                            INDEXCOLORTWO = 1
                        else:
                            INDEXCOLORTWO = 0

        display.fill(BACKGROUND)
        if startbtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            startbtn.hover(display)
        else:
            startbtn.drawRect(display)

        if leavebtn.get_rect().collidepoint(pygame.mouse.get_pos()):
            leavebtn.hover(display)
        else:
            leavebtn.drawRect(display)

        colorbtnone.drawCircle(display, COLORS[INDEXCOLORONE])
        colorbtntwo.drawCircle(display, COLORS[INDEXCOLORTWO])
        display.blit(title, titleRect)
        display.blit(playerone, playeronerect)
        display.blit(playertwo, playertworect)

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
