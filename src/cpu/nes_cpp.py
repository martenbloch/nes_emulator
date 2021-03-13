from ctypes import cdll, c_int
import ctypes

lib = cdll.LoadLibrary('./libNesApi.so')


class NesCpp:

    def __init__(self, nes_file, btn_state_getter, on_frame_update):
        s = ctypes.c_char_p(bytes(nes_file, encoding='utf-8'))
        self.obj = lib.nes_new(s, btn_state_getter, on_frame_update)

    def start(self):
        lib.nes_start(self.obj)

    def reset(self):
        lib.nes_reset(self.obj)
