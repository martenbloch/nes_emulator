from ctypes import cdll, c_int
import ctypes
import numpy as np

lib = cdll.LoadLibrary('./libppu.so')


def test(cartridge_data):
    a = [5, 6]
    c_a = (c_int * len(a))(*a)
    lib.testa(c_a)


class PpuCpp(object):

    def __init__(self, cartridge_data, mirroring):
        c_cartridge_data = (ctypes.c_byte * len(cartridge_data))(*cartridge_data)
        self.obj = lib.ppu_new(c_cartridge_data, len(c_cartridge_data), mirroring)

    def reset(self):
        lib.ppu_reset(self.obj)

    def clock(self):
        lib.ppu_clock(self.obj)

    @property
    def raise_nmi(self):
        return lib.ppu_is_nmi_raised(self.obj)

    @raise_nmi.setter
    def raise_nmi(self, value):
        lib.ppu_clear_nmi(self.obj)

    def is_address_valid(self, address):
        return lib.ppu_is_address_valid(self.obj, c_int(address))

    def write(self, address, data):
        lib.ppu_write(self.obj, c_int(address), c_int(data))

    def read(self, address):
        return lib.ppu_read(self.obj, address)

    def get_frame_data(self):
        return lib.ppu_get_frame_data(self.obj)

    @property
    def render_background(self):
        return lib.ppu_bg_enabled(self.obj)

    @property
    def screen_data(self):
        ptr = lib.ppu_get_frame_data(self.obj)
        ArrayType = ctypes.c_uint * (256*240)
        array_pointer = ctypes.cast(ptr, ctypes.POINTER(ArrayType))
        v = np.frombuffer(array_pointer.contents, dtype=np.int32)
        return v

    def write_oam_data(self, dma_offset, dma_data):
        lib.ppu_write_oam_data(self.obj, dma_offset, dma_data)


    '''
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
    '''
