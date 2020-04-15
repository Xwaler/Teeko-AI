from env import Teeko
import numpy as np
from constants import *

env = Teeko()
env.reset()

env.addToken(env.players[0], 20)
env.addToken(env.players[0], 15)
env.addToken(env.players[0], 10)
env.addToken(env.players[1], 5)


print(env.getAligned(env.players[0]))


def getAligned(self, player):
    idt = player.idt
    longest_alignment = 1

    for token in player.tokens:
        l_shape_first_direction = 0

        for direction in SURROUNDING:
            current_alignment = 1

            alignment_contain_zero = False
            zero_is_last = False

            current_cell = token
            module_current_cell = current_cell % 5

            next_cell = token + direction

            IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                               (current_cell + next_cell) % 5 != 4)

            while IN_GRID:
                next_cell_value = env.grid[next_cell]

                if next_cell_value == 0:

                    if alignment_contain_zero:
                        break

                    else:
                        alignment_contain_zero = True
                        zero_is_last = True

                elif next_cell_value == idt:
                    zero_is_last = False

                    current_alignment += 1

                else:
                    break

                current_cell = next_cell
                module_current_cell = current_cell % 5

                next_cell = current_cell + direction

                IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                                   (current_cell + next_cell) % 5 != 4)

            if current_alignment == 4:
                if alignment_contain_zero and not zero_is_last:
                    current_alignment = 3
                else:
                    current_alignment = 4
            elif current_alignment == 3:
                if not alignment_contain_zero:
                    current_cell = token
                    module_current_cell = current_cell % 5

                    next_cell = current_cell - direction

                    IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                                       (current_cell + next_cell) % 5 != 4)
                    if IN_GRID and env.grid[next_cell] == 0:
                        current_alignment = 3
                    else:
                        current_alignment = 1

                        square_alignment, l_shape_first_direction = Square_test(l_shape_first_direction, direction,
                                                                                token, idt)

                        current_alignment = max(current_alignment, square_alignment)

                else:
                    current_alignment = 3

            elif current_alignment == 2:
                if not alignment_contain_zero or zero_is_last:
                    square_alignment, l_shape_first_direction = Square_test(l_shape_first_direction, direction, token, idt)

                    current_alignment = max(current_alignment, square_alignment)
                    if current_alignment == 2:
                        current_cell = token
                        module_current_cell = current_cell % 5

                        next_cell = current_cell - direction

                        IN_GRID = 0 <= next_cell < 25 and ((module_current_cell != 0 and module_current_cell != 4) or
                                                           (current_cell + next_cell) % 5 != 4)
                        if IN_GRID and env.grid[next_cell] == 0:
                            current_cell = next_cell
                            module_current_cell = current_cell % 5

                            next_cell = current_cell - direction

                            IN_GRID = 0 <= next_cell < 25 and (
                                        (module_current_cell != 0 and module_current_cell != 4) or
                                        (current_cell + next_cell) % 5 != 4)
                            if IN_GRID and env.grid[next_cell] != 0:
                                current_alignment = 1
                        else:
                            current_alignment = 1

            if current_alignment > 2:
                return current_alignment

            if current_alignment > longest_alignment:
                longest_alignment = current_alignment

    return longest_alignment


def Square_test(self, l_shape_first_direction, direction, token, idt):
    current_alignment = 3
    if l_shape_first_direction == 0:
        current_alignment = 1
        if direction != 6:
            l_shape_first_direction = direction
    elif LSTTT[l_shape_first_direction] != direction:
        current_alignment = 1
        if direction == 5 and l_shape_first_direction == 1:
            fourth_cell_value = env.grid[token + 6]
            if fourth_cell_value == idt:
                current_alignment = 4
            elif fourth_cell_value == 0:
                current_alignment = 3
    else:
        fourth_cell_value = env.grid[token + LSFTT[l_shape_first_direction]]
        if fourth_cell_value != 0:
            current_alignment = 1
    return current_alignment, l_shape_first_direction
