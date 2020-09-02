from src.cpu import frame
import random


class Ppu:
    def __init__(self, screen):
        self.cycle = 0
        self.scanline = 0
        self.screen = screen
        self.frame = frame.Frame(262, 341)

        self.palette = [(0, 0, 0)] * 64
        self.palette[0x00] = (84, 84, 84)
        self.palette[0x01] = (0, 30, 116)
        self.palette[0x02] = (8, 16, 144)
        self.palette[0x03] = (48, 0, 136)
        self.palette[0x04] = (68, 0, 100)
        self.palette[0x05] = (92, 0, 48)
        self.palette[0x06] = (84, 4, 0)
        self.palette[0x07] = (60, 24, 0)
        self.palette[0x08] = (32, 42, 0)
        self.palette[0x09] = (8, 58, 0)
        self.palette[0x0A] = (0, 64, 0)
        self.palette[0x0B] = (0, 60, 0)
        self.palette[0x0C] = (0, 50, 60)
        self.palette[0x0D] = (0, 0, 0)
        self.palette[0x0E] = (0, 0, 0)
        self.palette[0x0F] = (0, 0, 0)

        self.palette[0x10] = (152, 150, 152)
        self.palette[0x11] = (8, 76, 196)
        self.palette[0x12] = (48, 50, 236)
        self.palette[0x13] = (92, 30, 228)
        self.palette[0x14] = (136, 20, 176)
        self.palette[0x15] = (160, 20, 100)
        self.palette[0x16] = (152, 34, 32)
        self.palette[0x17] = (120, 60, 0)
        self.palette[0x18] = (84, 90, 0)
        self.palette[0x19] = (40, 114, 0)
        self.palette[0x1A] = (8, 124, 0)
        self.palette[0x1B] = (0, 118, 40)
        self.palette[0x1C] = (0, 102, 120)
        self.palette[0x1D] = (0, 0, 0)
        self.palette[0x1E] = (0, 0, 0)
        self.palette[0x1F] = (0, 0, 0)

        self.palette[0x20] = (236, 238, 236)
        self.palette[0x21] = (76, 154, 236)
        self.palette[0x22] = (120, 124, 236)
        self.palette[0x23] = (176, 98, 236)
        self.palette[0x24] = (228, 84, 236)
        self.palette[0x25] = (236, 88, 180)
        self.palette[0x26] = (236, 106, 100)
        self.palette[0x27] = (212, 136, 32)
        self.palette[0x28] = (160, 170, 0)
        self.palette[0x29] = (116, 196, 0)
        self.palette[0x2A] = (76, 208, 32)
        self.palette[0x2B] = (56, 204, 108)
        self.palette[0x2C] = (56, 180, 204)
        self.palette[0x2D] = (60, 60, 60)
        self.palette[0x2E] = (0, 0, 0)
        self.palette[0x2F] = (0, 0, 0)

        self.palette[0x30] = (236, 238, 236)
        self.palette[0x31] = (168, 204, 236)
        self.palette[0x32] = (188, 188, 236)
        self.palette[0x33] = (212, 178, 236)
        self.palette[0x34] = (236, 174, 236)
        self.palette[0x35] = (236, 174, 212)
        self.palette[0x36] = (236, 180, 176)
        self.palette[0x37] = (228, 196, 144)
        self.palette[0x38] = (204, 210, 120)
        self.palette[0x39] = (180, 222, 120)
        self.palette[0x3A] = (168, 226, 144)
        self.palette[0x3B] = (152, 226, 180)
        self.palette[0x3C] = (160, 214, 228)
        self.palette[0x3D] = (160, 162, 160)
        self.palette[0x3E] = (0, 0, 0)
        self.palette[0x3F] = (0, 0, 0)

    def clock(self):

        self.frame.set_pixel(self.cycle, self.scanline, self.palette[0x3f if random.random() > 0.5 else 0x30])

        self.cycle += 1
        if self.cycle == 340:
            self.cycle = 0
            self.scanline += 1
            if self.scanline == 261:
                self.scanline = 0
                self.screen.update(self.frame)

