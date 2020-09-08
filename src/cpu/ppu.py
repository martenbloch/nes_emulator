from src.cpu import frame
import random


class Ppu:
    def __init__(self, screen, cardridge):
        self.cycle = 0
        self.scanline = -1
        self.screen = screen
        self.frame = frame.Frame(262, 341)
        self.status = 0x00
        self.vblank = 0
        self.cardridge = cardridge

        self.ppu_addr_flag = 0
        self.ppu_addr = 0x0000

        self.start_addr = 0x2000
        self.end_addr = 0x2008

        self.name_table_0 = [0 for i in range(1024)]
        self.name_table_1 = [0 for i in range(1024)]
        self.vram_addr = 0x0000

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

        self.shiftRegister1 = ShiftRegister(16)
        self.shiftRegister2 = ShiftRegister(16)
        self.next_tile_idx = 2
        self.row = 0
        self.tail_number = 0
        self.tail_base_number = 0
        self.cnt = 0

        self.idx = 0
        self.base_idx = 0

        self.enable_nmi = False
        self.raise_nmi = False

        self.nametable_inc = 0 # 0 - add 1, 1 - add 32

        self.background_half = 0 # 0 - left, 1 - right

        self.render_background = False

        self.read_buffer = 0x00

        self.palette_ram = [0 for i in range(32)]

        self.is_odd = True

    def clock(self):

        if self.scanline == -1 and self.cycle == 0:
            print("Start new frame")

        if self.scanline == -1:
            if self.render_background:
                self.row = 0
                self.tail_number = 0
                self.idx = 0
                l1, u1 = self.cardridge.get_tile_data(self.name_table_0[self.idx], self.row, self.background_half) # self.name_table_0[self.idx]
                self.tail_number += 1
                self.idx += 1
                l2, u2 = self.cardridge.get_tile_data(self.name_table_0[self.idx], self.row, self.background_half) # self.name_table_0[self.idx]

                l = (l1 << 8) | l2
                u = (u1 << 8) | u2

                self.shiftRegister1.write(l)
                self.shiftRegister1.write(u)

        if self.cycle == 0:
            self.tail_number = self.tail_base_number
            self.cnt += 1
            if self.cnt == 7:
                self.tail_base_number += 30

        if self.cycle >=1 and self.cycle <= 256 and self.scanline >=0 and self.scanline <= 240:

            p = self.palette[0x00]
            if self.render_background:
                b1 = self.shiftRegister1.shift()
                b2 = self.shiftRegister2.shift()
                color = b1 | (b2 << 1)
                p = self.palette[0x00]
                if color == 1:
                    p = self.palette[0x16]
                elif color == 2:
                    p = self.palette[0x26]
                elif color == 3:
                    p = self.palette[0x31]

            self.frame.set_pixel(self.cycle-1, self.scanline, p)

        if (self.cycle - 1) % 8 == 0 and self.scanline >=0 and self.scanline <= 239 and self.cycle <=256:

            if self.render_background:

                l1, u1 = self.cardridge.get_tile_data(self.name_table_0[self.idx], self.row,
                                                      self.background_half)  # self.name_table_0[self.idx]
                self.tail_number += 1
                self.idx += 1

                # print("scanline:{}   cycle:{}  row:{}    idx: {}    val:{}".format(self.scanline, self.cycle, self.row, self.idx, self.name_table_0[self.idx]))

                # TODO: to remove
                if self.next_tile_idx == len(self.name_table_0):
                    self.next_tile_idx = 0

                v = (self.shiftRegister1.read() & 0xFF00) | l1
                self.shiftRegister1.write(v)
                v = (self.shiftRegister2.read() & 0xFF00) | u1
                self.shiftRegister2.write(v)

        if self.scanline == 241 and self.cycle == 1:
            print("PPU: ----------------------> SET v blank")
            self.vblank = 1
            self.status = self.status | (1 << 7)
            if self.enable_nmi:
                self.raise_nmi = True

        if self.scanline == 260 and self.cycle == 304:
            self.vblank = 0
            self.status = self.status & (0 << 7)
            print("PPU: ----------------------> Clear v blank")

        self.cycle += 1

        if self.scanline == 261 and self.cycle == 340 and self.is_odd:
            self.cycle += 1

        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1

            if self.scanline > 0:
                self.row += 1

            if self.scanline % 8 == 0 and self.scanline != 0:
                self.base_idx += 32

            self.idx = self.base_idx

            if self.row == 8:
                self.row = 0
            if self.scanline >= 262:
                self.scanline = -1
                self.base_idx = 0
                self.screen.update(self.frame)

                if self.is_odd:
                    self.is_odd = False
                else:
                    self.is_odd = True

    def read(self, address):

        if address == 0x2002:
            #val = self.read_buffer & 0x1f | self.status & 0xe0
            val = self.status
            print("PPU read 0x2002 val:{}".format(hex(val)))
            self.status = self.status & (0 << 7)    # read clears vertical blank
            self.ppu_addr_flag = 0
            return val
        elif address == 0x2007:
            if self.vram_addr >= 0x2000 and self.vram_addr <= 0x3eff:
                index = self.vram_addr & 0x3ff
                if self.cardridge.mirroring == 0:   # horizontal
                    if self.vram_addr >= 0x2000 and self.vram_addr <= 0x23ff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_0[index]
                        return val
                    elif self.vram_addr >= 0x2400 and self.vram_addr <= 0x27ff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_0[index]
                        return val
                    elif 0x2800 <= self.vram_addr <= 0x2bff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_1[index]
                        return val
                    elif self.vram_addr >= 0x2c00 and self.vram_addr <= 0x2fff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_1[index]
                        return val
                else:
                    if self.vram_addr >= 0x2000 and self.vram_addr <= 0x23ff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_0[index]
                        return val
                    elif self.vram_addr >= 0x2400 and self.vram_addr <= 0x27ff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_1[index]
                        return val
                    elif self.vram_addr >= 0x2800 and self.vram_addr <= 0x2bff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_0[index]
                        return val
                    elif self.vram_addr >= 0x2c00 and self.vram_addr <= 0x2fff:
                        val = self.read_buffer
                        self.read_buffer = self.name_table_1[index]
                        return val
            elif self.vram_addr >= 0x3f00 and self.vram_addr <= 0x3fff:
                index = self.vram_addr & 0x3ff
                self.read_buffer = self.name_table_1[index]

                return self.palette_ram[self.vram_addr & 0xff]
            elif self.vram_addr >= 0 and self.vram_addr <= 0x1fff:
                val = self.read_buffer
                self.read_buffer = self.cardridge.chr[self.vram_addr]
                return val
            else:
                raise NotImplementedError("PPUREAD for addr:{}".format(hex(self.vram_addr)))

            if self.nametable_inc:
                self.vram_addr += 32
            else:
                self.vram_addr += 1
            return
        else:
            raise NotImplementedError("PPU read not implemented, address:{}".format(hex(address)))

    def write(self, address, data):
        if address == 0x2000:
            print("PPUCTRL write:{}".format(hex(data)))

            if data & 0x80:
                print("PPU: NMI enabled")
                self.enable_nmi = True
            else:
                self.enable_nmi = False

            if data & 0x04:
                self.nametable_inc = 1
            else:
                self.nametable_inc = 0

            if data & 0x10:
                print(" Background pattern table 0x1000")
                self.background_half = 1
            else:
                self.background_half = 0
                print(" Background pattern table 0x0000")

            return
        elif address == 0x2001:
            print("PPUMASK write:{}".format(hex(data)))

            if data & 0x8:
                self.render_background = True
            else:
                self.render_background = False

            return
        elif address == 0x2003:
            print("PPU OAM ADDR write:{}".format(hex(data)))
            return
        elif address == 0x2004:
            print("PPU OAM DATA write:{}".format(hex(data)))
            return
        elif address == 0x2005:
            print("PPUSCROLL write:{}".format(hex(data)))
            return
        elif address == 0x2006:
            if self.ppu_addr_flag == 0:
                self.ppu_addr_flag = 1
                self.ppu_addr = 0x000 | (data << 8)
            else:
                self.ppu_addr_flag = 0
                self.ppu_addr = self.ppu_addr | data
                self.vram_addr = self.ppu_addr
            x = 3
            print("PPUADDR write:{}".format(hex(data)))
            return
        elif address == 0x2007:
            if self.vram_addr >= 0x2000 and self.vram_addr <= 0x3eff:
                index = self.vram_addr & 0x3ff
                if self.cardridge.mirroring == 0:   # horizontal
                    if self.vram_addr >= 0x2000 and self.vram_addr <= 0x23ff:
                        self.name_table_0[index] = data
                    elif self.vram_addr >= 0x2400 and self.vram_addr <= 0x27ff:
                        self.name_table_0[index] = data
                    elif 0x2800 <= self.vram_addr <= 0x2bff:
                        self.name_table_1[index] = data
                    elif self.vram_addr >= 0x2c00 and self.vram_addr <= 0x2fff:
                        self.name_table_1[index] = data
                else:
                    if self.vram_addr >= 0x2000 and self.vram_addr <= 0x23ff:
                        self.name_table_0[index] = data
                    elif self.vram_addr >= 0x2400 and self.vram_addr <= 0x27ff:
                        self.name_table_1[index] = data
                    elif self.vram_addr >= 0x2800 and self.vram_addr <= 0x2bff:
                        self.name_table_0[index] = data
                    elif self.vram_addr >= 0x2c00 and self.vram_addr <= 0x2fff:
                        self.name_table_1[index] = data

            elif self.vram_addr >= 0x3f00 and self.vram_addr <= 0x3fff:
                self.palette_ram[self.vram_addr & 0x1f] = data
            elif self.vram_addr >= 0 and self.vram_addr <= 0x1fff:
                self.cardridge.chr[self.vram_addr] = data
                pass
            else:
                raise NotImplementedError("PPUWRITE for addr:{}   data:{}".format(hex(self.vram_addr), hex(data)))

            if data != 0:
                print("PPUWRITE write addr:{}  data:{}".format(hex(self.vram_addr), hex(data)))

            if self.nametable_inc:
                self.vram_addr += 32
            else:
                self.vram_addr += 1
            return
        else:
            raise NotImplementedError("PPU write not implemented. addr:{}  data:{}".format(hex(address), hex(data)))

    def is_address_valid(self, address):
        if self.start_addr <= address < self.end_addr:
            return True
        return False


class ShiftRegister:

    def __init__(self, len):
        self.len = len
        self.mask = 1 << (len - 1)
        self.value = 0

    def shift(self):
        b = (self.value & self.mask) >> (self.len - 1)
        self.value = self.value << 1
        return b

    def write(self, value):
        self.value = value

    def read(self):
        return self.value


if __name__ == "__main__":
    print("test")
    s = ShiftRegister(8)
    s.write(170)
    b1 = s.shift()
    b2 = s.shift()
    b3 = s.shift()
    b4 = s.shift()
    x=3

