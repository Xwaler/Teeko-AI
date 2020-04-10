import numpy as np


def randomChoice(a):
    return a[np.random.randint(len(a))]


class PageManager:
    def __init__(self):
        self.current = None

    def setPage(self, page):
        self.current = page

    def parse_event(self, event):
        self.current.parse_event(event)
