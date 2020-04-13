GRID_SIZE = 5
TOKEN_NUMBER = 4

DIRECTIONS = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
SURROUNDING = [[-1, -1], [-1, 0], [-1, 1], [0, -1]]

ALIGNEMENTS = {4: [[1, 1, 1, 1, -1]],
               3: [[1, 1, 1, 0, -1], [0, 1, 1, 1, -1], [-1, 1, 1, 1, 0], [1, 0, 1, 1, -1], [1, 1, 0, 1, -1]],
               2: [[1, 1, -1, -1, -1], [-1, 1, 1, -1, -1]]}

DIFFICULTY = ['Easy', 'Normal', 'Hard']
PLAYERTYPE = ['Humain', 'AI', 'Learning']
MAX_DEPTH = [3, 4, 5]

SCREEN_SIZE = (1200, 750)
TOKEN_RADIUS = 40
TOKEN_THICKNESS = 2

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 100, 10)
YELLOW = (255, 255, 0)
MARROON = (115, 0, 0)
LIME = (180, 255, 100)
PINK = (255, 100, 180)
PURPLE = (240, 0, 255)
GRAY = (127, 127, 127)
BROWN = (100, 40, 0)
NAVY = (0, 0, 100)
LIGHTGRAY = (200, 200, 200)
BACKGROUND = (230, 230, 230)
COLORS = [RED, BLUE, GREEN, ORANGE, YELLOW, MARROON, LIME, PINK, PURPLE, GRAY, BROWN, NAVY, LIGHTGRAY, BACKGROUND]

CODE_TO_MENU = 10
CODE_TO_GAME = 11
