
class Frame:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        white = (255, 255, 255)
        self.data = [[white for i in range(self.w)] for j in range(self.h)]

    def set_pixel(self, x, y, color):
        self.data[x][y] = color

    def get_data(self):
        return self.data
