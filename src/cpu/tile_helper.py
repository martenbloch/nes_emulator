from ctypes import cdll

lib = cdll.LoadLibrary('./libppu.so')


class TileHelper(object):

    def __init__(self, lower, upper):
        self.obj = lib.TileHelper_new(lower, upper)

    def shift(self):
        return lib.TileHelper_shift(self.obj)

    def writeLower(self, lower):
        lib.TileHelper_writeLower(self.obj, lower)

    def writeLowerL(self, lower):
        lib.TileHelper_writeLowerL(self.obj, lower)

    def writeUpper(self, upper):
        lib.TileHelper_writeUpper(self.obj, upper)

    def writeUpperL(self, upper):
        lib.TileHelper_writeUpperL(self.obj, upper)
