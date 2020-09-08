import pygame


class Screen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((341*2, 262*2))
        pygame.display.update()

    def update(self, frame):
        d = frame.get_data()
        for x in range(341*2):
            for y in range(262*2):
                self.screen.fill(d[x][y], ((x, y), (2, 2)))

        pygame.display.update()
