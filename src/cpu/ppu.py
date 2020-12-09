from src.cpu import frame
import random
import numpy as np
import pygame

class OamData:
    def __init__(self):
        self.y = 0xFF
        self.tile_num = 0xFF
        self.attr = 0xFF
        self.x = 0xFF

    def get_prio(self):
        return (self.attr & 0x20) >> 5

    def flip_horizontally(self):
        return self.attr & 0x40 == 0x40

    def palette(self):
        return self.attr & 0x3

    def __repr__(self):
        return "({},{}) tile:{}  prio:{}  ".format(self.x, self.y, self.tile_num, self.get_prio())


class PpuCtrl:

    def __init__(self):
        self.base_nametable = 0x2000
        self.vram_inc = 1
        self.sprite_address = 0x0000
        self.bg_address = 0x0000
        self.sprite_size = 0  # 0 - 8x8, 1 - 8x16
        self.generate_nmi = False

    def from_byte(self, data):

        val = data & 0x3
        if val == 0:
            self.base_nametable = 0x2000
        elif val == 1:
            self.base_nametable = 0x2400
        elif val == 2:
            self.base_nametable = 0x2800
        else:
            self.base_nametable = 0x2C00

        if data & 0x4 == 0:
            self.vram_inc = 1
        else:
            self.vram_inc = 32

        if data & 0x8 == 0:
            self.sprite_address = 0x0000
        else:
            self.sprite_address = 0x1000

        if data & 0x10 == 0:
            self.bg_address = 0x0000
        else:
            self.bg_address = 0x1000

        if data & 0x20 == 0:
            self.sprite_size = 0
        else:
            self.sprite_size = 1
            print("Sprite size 8x16")

        if data & 0x80 == 0:
            self.generate_nmi = False
        else:
            self.generate_nmi = True


class Ppu:
    def __init__(self, screen, cardridge):

        self.ppu_ctrl = PpuCtrl()

        self.oam = [OamData() for i in range(64)]
        self.secondary_oam = [OamData() for i in range(8)]
        self.secondary_oam_x_counter = [0 for i in range(8)]
        self.secondary_oam_num_pixel_to_draw = [8 for i in range(8)]
        self.secondary_oam_attr_bytes = [8 for i in range(8)]
        self.secondary_oam_l = [ShiftRegister(8) for i in range(8)]
        self.secondary_oam_h = [ShiftRegister(8) for i in range(8)]

        self.oam_addr = 0x00
        self.show_sprite = False
        self.sprite_pattern_table = 0x0000

        self.cycle = 0
        self.scanline = 0
        self.screen = screen
        self.frame = frame.Frame(262, 341)
        self.status = 0x00
        self.cardridge = cardridge

        self.ppu_addr_flag = 0
        self.ppu_addr = 0x0000

        self.start_addr = 0x2000
        self.end_addr = 0x2008

        self.name_table_0 = [0 for i in range(1024)]
        self.name_table_1 = [0 for i in range(1024)]
        self.vram_addr = 0x0000

        self.palette = [(0, 0, 0)] * 64
        '''
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
        '''

        self.palette[0x00] = 0x545454
        self.palette[0x01] = 0x001E74
        self.palette[0x02] = 0x081090
        self.palette[0x03] = 0x300088
        self.palette[0x04] = 0x440064
        self.palette[0x05] = 0x5C0030
        self.palette[0x06] = 0x540400
        self.palette[0x07] = 0x3C1800
        self.palette[0x08] = 0x202A00
        self.palette[0x09] = 0x083A00
        self.palette[0x0A] = 0x004000
        self.palette[0x0B] = 0x003C00
        self.palette[0x0C] = 0x00323C
        self.palette[0x0D] = 0x000000
        self.palette[0x0E] = 0x000000
        self.palette[0x0F] = 0x000000
        self.palette[0x10] = 0x989698
        self.palette[0x11] = 0x084CC4
        self.palette[0x12] = 0x3032EC
        self.palette[0x13] = 0x5C1EE4
        self.palette[0x14] = 0x8814B0
        self.palette[0x15] = 0xA01464
        self.palette[0x16] = 0x982220
        self.palette[0x17] = 0x783C00
        self.palette[0x18] = 0x545A00
        self.palette[0x19] = 0x287200
        self.palette[0x1A] = 0x087C00
        self.palette[0x1B] = 0x007628
        self.palette[0x1C] = 0x006678
        self.palette[0x1D] = 0x000000
        self.palette[0x1E] = 0x000000
        self.palette[0x1F] = 0x000000
        self.palette[0x20] = 0xECEEEC
        self.palette[0x21] = 0x4C9AEC
        self.palette[0x22] = 0x787CEC
        self.palette[0x23] = 0xB062EC
        self.palette[0x24] = 0xE454EC
        self.palette[0x25] = 0xEC58B4
        self.palette[0x26] = 0xEC6A64
        self.palette[0x27] = 0xD48820
        self.palette[0x28] = 0xA0AA00
        self.palette[0x29] = 0x74C400
        self.palette[0x2A] = 0x4CD020
        self.palette[0x2B] = 0x38CC6C
        self.palette[0x2C] = 0x38B4CC
        self.palette[0x2D] = 0x3C3C3C
        self.palette[0x2E] = 0x000000
        self.palette[0x2F] = 0x000000
        self.palette[0x30] = 0xECEEEC
        self.palette[0x31] = 0xA8CCEC
        self.palette[0x32] = 0xBCBCEC
        self.palette[0x33] = 0xD4B2EC
        self.palette[0x34] = 0xECAEEC
        self.palette[0x35] = 0xECAED4
        self.palette[0x36] = 0xECB4B0
        self.palette[0x37] = 0xE4C490
        self.palette[0x38] = 0xCCD278
        self.palette[0x39] = 0xB4DE78
        self.palette[0x3A] = 0xA8E290
        self.palette[0x3B] = 0x98E2B4
        self.palette[0x3C] = 0xA0D6E4
        self.palette[0x3D] = 0xA0A2A0
        self.palette[0x3E] = 0x000000
        self.palette[0x3F] = 0x000000

        #for i in range(len(self.palette)):
        #    c = self.palette[i]
        #    print("self.palette[0x{:02X}] = 0x{:06X}".format(i, c[0] << 16 | c[1] << 8 | c[2]))

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

        self.nametable_inc = 0  # 0 - add 1, 1 - add 32

        self.background_half = 0  # 0 - left, 1 - right

        self.render_background = False

        self.read_buffer = 0x00

        self.palette_ram = [0 for i in range(32)]

        self.is_odd = True

        self.cur_addr = VramRegister()
        self.tmp_addr = VramRegister()
        self.address_latch = 0
        self.next_tile_id = 0
        self.next_tile_low = 0x00
        self.next_tile_high = 0x00

        self.debug_tile = ""

        self.enable_bg_render = False

        self.last_written_data = 0x00

        self.frame_cnt = 1

        self.pallete_idx = 0x0

        self.sprite_zero_hit = False

        self.bg_pixel = 0

        self.num_secondary_sprites = 0

        self.pallete_base_address = 0x3F00

        #self.th = tile_helper.TileHelper(0x0000, 0x0000)
        self.screen_data = [0 for i in range(256*240)]

        self.bg_next_tile_attrib = 0x00

        self.attr_low = ShiftRegister(16)
        self.attr_high = ShiftRegister(16)

    def clear_secondary_oam(self):
        self.secondary_oam = [OamData() for i in range(8)]

    def fill_secondary_oam(self, y):
        self.num_secondary_sprites = 0
        self.secondary_oam_num_pixel_to_draw = [0, 0, 0, 0, 0, 0, 0, 0]
        # msg = "scanline:{}  sprites: ".format(y)
        for i in range(64):
            if self.oam[i].y <= y < self.oam[i].y + 8:
                self.secondary_oam[self.num_secondary_sprites] = self.oam[i]
                self.secondary_oam_x_counter[self.num_secondary_sprites] = self.oam[i].x
                self.secondary_oam_attr_bytes[self.num_secondary_sprites] = self.oam[i].attr
                self.secondary_oam_num_pixel_to_draw[self.num_secondary_sprites] = 8
                self.num_secondary_sprites += 1
                # msg += ascii(self.oam[i])
                if self.num_secondary_sprites == 8:
                    break
        # if cnt != 0:
        #    print(msg)

    def decrement_sprite_x_counters(self):
        for i in range(self.num_secondary_sprites):
            if self.secondary_oam_x_counter[i] > 0:
                self.secondary_oam_x_counter[i] -= 1
            if self.secondary_oam_x_counter[i] == 0 and self.secondary_oam_num_pixel_to_draw[i] > 0:
                b1 = self.secondary_oam_l[i].shift()
                b2 = self.secondary_oam_h[i].shift()
                color = b1 | (b2 << 1)

                pallete_idx = self.secondary_oam[i].palette()
                idx = (self.read_video_mem(0x3F10 + (pallete_idx << 2) + color)) & 0x3f

                priority = (self.secondary_oam_attr_bytes[i] & 0x20) >> 5

                if self.bg_pixel == 0 and color == 0:
                    idx = (self.read_video_mem(0x3F00) & 0x3f)
                    self.screen_data[(self.cycle - 1) + (256 * self.scanline)] = self.palette[idx]
                elif self.bg_pixel == 0 and color != 0:
                    self.screen_data[(self.cycle - 1) + (256 * self.scanline)] = self.palette[idx]
                elif color == 0:
                    pass
                elif self.bg_pixel != 0 and color != 0 and priority == 0:
                    self.screen_data[(self.cycle - 1) + (256 * self.scanline)] = self.palette[idx]

                self.secondary_oam_num_pixel_to_draw[i] -= 1

                if not self.sprite_zero_hit and i == 0 and color != 0 and self.bg_pixel != 0:
                    self.sprite_zero_hit = True

    def fill_sprites_shift_registers(self, y):
        row = y % 8
        for i in range(8):
            sprite = self.secondary_oam[i]
            half = 0
            if self.ppu_ctrl.sprite_address == 0x1000:
                half = 1

            low, upper = self.cardridge.get_tile_data(sprite.tile_num, row, half)

            #if sprite.tile_num != 255:
                #print("half:{} tile_num:{} row:{} l:{} u:{}".format(half, sprite.tile_num, row, low, upper))

            if sprite.flip_horizontally():
                low = int('{:08b}'.format(low)[::-1], 2)
                upper = int('{:08b}'.format(upper)[::-1], 2)

            self.secondary_oam_l[i] = ShiftRegister(8, low)
            self.secondary_oam_h[i] = ShiftRegister(8, upper)

    def read_palette_ram(self, address):
        address &= 0x001F
        if address == 0x0010:
            address = 0x0000
        elif address == 0x0014:
            address = 0x0004
        elif address == 0x0018:
            address = 0x0008
        elif address == 0x001C:
            address = 0x000C

        return self.palette_ram[address & 0xff]

    def read_video_mem(self, address):
        if 0x2000 <= address <= 0x3eff:
            index = address & 0x3ff
            if self.cardridge.mirroring == 0:  # horizontal
                if 0x2000 <= address <= 0x23ff or 0x2400 <= address <= 0x27ff:
                    return self.name_table_0[index]
                elif 0x2800 <= address <= 0x2bff or 0x2c00 <= address <= 0x2fff:
                    return self.name_table_1[index]
            else:
                if 0x2000 <= address <= 0x23ff or 0x2800 <= address <= 0x2bff:
                    return self.name_table_0[index]
                elif 0x2400 <= address <= 0x27ff or 0x2c00 <= address <= 0x2fff:
                    return self.name_table_1[index]
        elif 0x3f00 <= address <= 0x3fff:
            if address == 0x3f04 or address == 0x3F08 or address == 0x3F0C:
                address = 0x3f00

            address &= 0x001F

            return self.palette_ram[address & 0xff]

        elif 0 <= address <= 0x1fff:
            return self.cardridge.chr[address]
            #return self.cardridge.chr[self.vram_addr]
        else:
            raise NotImplementedError("video ram read for address:{:X}".format(address))
        return

    def write_video_mem(self, address, data):
        pass

    def get_palette_idx(self):
        attr_data = self.read_video_mem(
            self.cur_addr.base_name_table | 0x3c0 | (self.cur_addr.tile_x >> 2) | (
                    (self.cur_addr.tile_y >> 2) << 3))

        if self.cur_addr.tile_y & 0x02:
            attr_data = attr_data >> 4
        elif self.cur_addr.tile_x & 0x02:
            attr_data = attr_data >> 2
        attr_data = attr_data & 0x03
        self.pallete_idx = attr_data

    def tile_row_to_pixels(self, lower, upper, palette_idx):
        palette_address = 0x3F00 + (palette_idx << 2)

        lower = np.unpackbits(np.array(lower, dtype=np.uint8))
        upper = np.unpackbits(np.array(upper, dtype=np.uint8))

        s = np.add(lower, upper) #+ palette_address
        pixels = [self.palette[el] for el in s]
        return pixels

    def clock(self):

        if self.scanline == -1:
            if self.cycle == 1:
                self.status &= 0x7F
                self.sprite_zero_hit = False

            elif 280 <= self.cycle <= 304:
                self.cur_addr.base_name_table = self.tmp_addr.base_name_table
                self.cur_addr.tile_y = self.tmp_addr.tile_y
                self.cur_addr.fine_y = self.tmp_addr.fine_y

            elif self.cycle == 322 and self.render_background:
                # load id's of 2 first tiles
                first_tile_id = self.read_video_mem(self.cur_addr.get_vram_address())
                self.get_palette_idx()
                self.cur_addr.increment_tile_x()
                second_tile_id = self.read_video_mem(self.cur_addr.get_vram_address())
                self.cur_addr.increment_tile_x()

                # fill shift register
                l1, u1 = self.cardridge.get_tile_data(first_tile_id, self.cur_addr.fine_y,
                                                      self.background_half)  # self.name_table_0[self.idx]
                self.tail_number += 1
                self.idx += 1
                l2, u2 = self.cardridge.get_tile_data(second_tile_id, self.cur_addr.fine_y,
                                                      self.background_half)  # self.name_table_0[self.idx]

                l = (l1 << 8) | l2
                u = (u1 << 8) | u2

                #self.th.writeLower((l1 << 8) | l2)
                #self.th.writeUpper((u1 << 8) | u2)
                self.shiftRegister1.write(l)
                self.shiftRegister1.write(u)

        # visible scanline section
        elif 0 <= self.scanline <= 239:

            if self.render_background:
                if self.scanline == 0 and self.cycle == 0 and self.is_odd:
                    self.cycle = 1

                elif 1 <= self.cycle <= 256 or (321 <= self.cycle <= 340):  # screen width - 256px

                    r = self.cycle % 8
                    if r == 2:
                        self.next_tile_id = self.read_video_mem(self.cur_addr.get_vram_address())
                    elif r == 4:

                        addr = self.cur_addr.base_name_table | 0x3c0 | (self.cur_addr.tile_x >> 2) | (
                                (self.cur_addr.tile_y >> 2) << 3)

                        attr_data = self.read_video_mem(addr)

                        if self.cur_addr.tile_y & 0x02:
                            attr_data >>= 4
                        elif self.cur_addr.tile_x & 0x02:
                            attr_data >>= 2
                        attr_data &= 0x03
                        self.pallete_idx = attr_data
                        self.pallete_base_address = 0x3F00 + (self.pallete_idx << 2)

                        self.bg_next_tile_attrib = attr_data

                    # performcne improvement, read tile data at once
                    #elif self.cycle % 8 == 6:
                    #    self.next_tile_low, u1 = self.cardridge.get_tile_data(self.next_tile_id, self.cur_addr.fine_y,
                    #                                                          self.background_half)

                    elif r == 0:
                        self.next_tile_low, self.next_tile_high = self.cardridge.get_tile_data(self.next_tile_id, self.cur_addr.fine_y,
                                                                               self.background_half)

                        self.cur_addr.increment_tile_x()

                    elif r == 1 and self.cycle > 1:
                        v = (self.shiftRegister1.read() & 0xFF00) | self.next_tile_low
                        self.shiftRegister1.write(v)
                        v = (self.shiftRegister2.read() & 0xFF00) | self.next_tile_high
                        self.shiftRegister2.write(v)

                        low = 0x00
                        if self.bg_next_tile_attrib & 0x01:
                            low = 0xff
                        upper = 0x00
                        if self.bg_next_tile_attrib & 0x02:
                            upper = 0xff

                        v = (self.attr_low.read() & 0xFF00) | low
                        self.attr_low.write(v)
                        v = (self.attr_high.read() & 0xFF00) | upper
                        self.attr_high.write(v)

                if 1 <= self.cycle <= 336:
                    self.bg_pixel = self.shiftRegister1.shift() | (self.shiftRegister2.shift() << 1)
                    self.pallete_idx = self.attr_low.shift() | (self.attr_high.shift() << 1)
                    idx = (self.read_video_mem(0x3F00 + (self.pallete_idx << 2) + self.bg_pixel)) & 0x3f

                    if 1 <= self.cycle <= 256:
                        self.screen_data[(self.cycle - 1) + (256 * self.scanline)] = self.palette[idx]

                if self.cycle == 256:
                    self.cur_addr.increment_tile_y()
                elif self.cycle == 257:
                    self.cur_addr.base_name_table = self.tmp_addr.base_name_table
                    self.cur_addr.tile_x = self.tmp_addr.tile_x

            # ------------------------------sprite rendering------------------------------
            if self.show_sprite:
                if 0 <= self.cycle <= 255:
                    self.decrement_sprite_x_counters()
                elif self.cycle == 1:
                    self.clear_secondary_oam()
                elif self.cycle == 256:
                    self.fill_secondary_oam(self.scanline)
                elif self.cycle == 257:
                    self.fill_sprites_shift_registers(self.scanline)
        elif self.scanline == 240 and self.cycle == 0:
            self.frame_cnt += 1

        elif self.scanline == 241 and self.cycle == 1:
            self.status = self.status | (1 << 7)
            if self.enable_nmi:
                self.raise_nmi = True

        self.cycle += 1
        if self.cycle == 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline == 261:
                self.scanline = -1
                self.is_odd = not self.is_odd

    def read(self, address):
        if address == 0x2002:

            if self.sprite_zero_hit:
                self.status = self.status | (1 << 6)
                # print("Zero hit in status")

            val = self.last_written_data & 0x1f | self.status & 0xe0
            # val = self.read_buffer & 0x1f | self.status & 0xe0
            # val = self.status
            # print("PPU STATUS read 0x2002 val:{}".format(hex(val)))
            self.status = self.status & (0 << 7)  # read clears vertical blank
            self.ppu_addr_flag = 0
            self.address_latch = 0
            return val
        elif address == 0x2007:
            # print("PPU read address:{}".format(hex(self.vram_addr)))

            val = 0
            if 0x2000 <= self.vram_addr <= 0x3eff:
                val = self.read_buffer
                self.read_buffer = self.read_video_mem(self.vram_addr)
            elif 0x3f00 <= self.vram_addr <= 0x3fff:
                index = self.vram_addr & 0x3ff
                self.read_buffer = self.name_table_1[index]
                addr = self.vram_addr & 0x001F
                if addr == 0x0010:
                    addr = 0x0000
                if addr == 0x0014:
                    addr = 0x0004
                if addr == 0x0018:
                    addr = 0x0008
                if addr == 0x001C:
                    addr = 0x000C

                val = self.palette_ram[addr]
                # return self.palette_ram[self.vram_addr & 0xff]
            elif 0 <= self.vram_addr <= 0x1fff:
                val = self.read_buffer
                self.read_buffer = self.cardridge.chr[self.vram_addr]
                # return val
            else:
                raise NotImplementedError("PPUREAD for addr:{}".format(hex(self.vram_addr)))

            if self.nametable_inc:
                self.vram_addr += 32
                self.cur_addr.vram_addr += 32
            else:
                self.vram_addr += 1
                self.cur_addr.vram_addr += 1
            return val
        else:
            raise NotImplementedError("PPU read not implemented, address:{}".format(hex(address)))

    def write_oam_data(self, address, data):
        idx = address // 4
        param_idx = address % 4

        if idx >= len(self.oam):
            raise Exception("out of range: {}, address:{}".format(idx, hex(address)))

        if param_idx == 0:
            self.oam[idx].y = data
        elif param_idx == 1:
            self.oam[idx].tile_num = data
        elif param_idx == 2:
            self.oam[idx].attr = data
        elif param_idx == 3:
            self.oam[idx].x = data

    def write(self, address, data):
        if address == 0x2000:
            self.last_written_data = data

            self.ppu_ctrl.from_byte(data)
            # print("PPUCTRL write:{}".format(hex(data)))

            # self.cur_addr.set_name_table(data & 0x3)
            self.tmp_addr.set_base_name_table(data & 0x3)

            if data & 0x80:
                # print("PPU: NMI enabled")
                self.enable_nmi = True
            else:
                self.enable_nmi = False

            if data & 0x04:
                self.nametable_inc = 1
                # print("VRAM INC by 32")
            else:
                self.nametable_inc = 0
                # print("VRAM INC by 1")

            if data & 0x10:
                self.background_half = 1
            else:
                self.background_half = 0

            return
        elif address == 0x2001:
            self.last_written_data = data
            # print("PPUMASK write:{}".format(hex(data)))

            if data & 0x8:
                # self.render_background = True
                # print("Schedule Enable background rendering!")
                # self.enable_bg_render = True
                self.render_background = True
            else:
                # self.render_background = False
                # self.enable_bg_render = False
                self.render_background = False

            if data & 0x10:
                self.show_sprite = True
            else:
                self.show_sprite = False

            return
        elif address == 0x2003:
            self.last_written_data = data
            self.oam_addr = data
            # print("OAM addr:{}".format(hex(self.oam_addr)))

        elif address == 0x2004:
            self.last_written_data = data
            self.write_oam_data(self.oam_addr, data)
            # print("OAM addr:{}   data:{}".format(hex(self.oam_addr), hex(data)))
            self.oam_addr += 1

        elif address == 0x2005:
            self.last_written_data = data
            if self.address_latch == 0:
                self.address_latch = 1
                self.tmp_addr.scroll_x(data)
            else:
                self.address_latch = 0
                self.tmp_addr.scroll_y(data)
            # print("PPU SCROLL write:{}".format(hex(data)))
            return
        elif address == 0x2006:
            self.last_written_data = data
            #print("PPUADDR write:{}".format(hex(data)))
            if self.address_latch == 0:
                self.address_latch = 1
                self.ppu_addr = 0x0000 | ((data & 0x3f) << 8)
                self.tmp_addr.set_address((self.tmp_addr.vram_addr & 0x00ff) | ((data & 0x3f) << 8))
            else:
                self.address_latch = 0
                self.ppu_addr = self.ppu_addr | data
                self.vram_addr = self.ppu_addr

                self.cur_addr.set_address(self.ppu_addr)
                self.tmp_addr.set_address(self.ppu_addr)
            return

        elif address == 0x2007:
            if self.vram_addr >= 0x2000 and self.vram_addr <= 0x3eff:
                index = self.vram_addr & 0x3ff
                if self.cardridge.mirroring == 0:  # horizontal
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

                addr = self.vram_addr & 0x001F
                if addr == 0x0010:
                    addr = 0x0000
                elif addr == 0x0014:
                    addr = 0x0004
                elif addr == 0x0018:
                    addr = 0x0008
                elif addr == 0x001C:
                    addr = 0x000C
                self.palette_ram[addr] = data
            elif 0 <= self.vram_addr <= 0x1fff:
                self.cardridge.chr[self.vram_addr] = data
                pass
            else:
                raise NotImplementedError("PPUWRITE for addr:{}   data:{}".format(hex(self.vram_addr), hex(data)))

            if data != 0:
                # print("PPUWRITE write addr:{}  data:{}".format(hex(self.vram_addr), hex(data)))
                pass

            if self.nametable_inc:
                self.vram_addr += 32

                self.cur_addr.vram_addr += 32
            else:
                self.vram_addr += 1
                self.cur_addr.vram_addr += 1
            return
        else:
            raise NotImplementedError("PPU write not implemented. addr:{}  data:{}".format(hex(address), hex(data)))

    def is_address_valid(self, address):
        return self.start_addr <= address < self.end_addr

    def reset(self):
        self.cycle = 24


class VramRegister:

    def __init__(self):
        self.tile_row = 0
        self.tile_x = 0
        self.tile_y = 0
        self.nametable_x = 0
        self.nametable_y = 0
        self.vram_addr = 0x0000
        self.base_name_table = 0x2000
        self.fine_y = 0

    def set_address(self, address):
        self.vram_addr = address
        self.tile_x = address & 0x1f
        self.tile_y = address & 0x3e0
        self.set_base_name_table(address & 0xc00)

    def get_address(self):
        return self.vram_addr

    def increment_tile_x(self):
        if self.tile_x == 31:
            self.tile_x = 0
            self.base_name_table ^= 0x400
        else:
            self.tile_x += 1
            self.vram_addr += 1

    def increment_tile_y(self):
        if self.fine_y < 7:
            self.fine_y += 1
        else:
            self.fine_y = 0
            if self.tile_y == 29:
                self.tile_y = 0
                self.vram_addr ^= 0x800
            else:
                self.tile_y += 1

    def get_vram_address(self):
        return self.base_name_table | (self.tile_y << 5) | self.tile_x

    def set_base_name_table(self, val):
        if val == 0:
            self.base_name_table = 0x2000
        elif val == 1:
            self.base_name_table = 0x2400
        elif val == 2:
            self.base_name_table = 0x2800
        elif val == 3:
            self.base_name_table = 0x2C00

    def scroll_x(self, px_num):  # 0-255
        self.tile_x = px_num // 8

    def scroll_y(self, px_num):  # 0 - 239
        self.tile_y = px_num // 8

    def __repr__(self):
        return "address:{:04X} tileX:{}  tileY:{}  baseAddr:{:04X}".format(self.get_vram_address(), self.tile_x, self.tile_y, self.base_name_table)


class ShiftRegister:

    def __init__(self, len, val=0):
        self.len = len - 1
        self.mask = 1 << (len - 1)
        self.value = val

    def shift(self):
        b = (self.value & self.mask) >> self.len
        self.value <<= 1
        return b

    def write(self, value):
        self.value = value

    def read(self):
        return self.value


if __name__ == "__main__":
    print("test")
