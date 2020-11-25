import pygame


class Frame:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.surface = pygame.Surface((256, 240))
        self.pa = pygame.PixelArray(self.surface)

    def set_pixel(self, x, y, color):
        self.pa[x, y] = color

    def get_surface(self):
        return self.surface
