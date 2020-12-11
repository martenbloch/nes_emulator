from src.cpu import cpu
from src.cpu import ppu
from src.cpu import frame
import pygame
import cProfile
import pstats
import re
import ppu_cpp
import numpy as np


class Nes:
    def __init__(self, screen):
        #self.cartridge = cpu.Cardrige("tests/nestest.nes")
        #self.cartridge = cpu.Cardrige("tests/mario-bros.nes")
        #self.cartridge = cpu.Cardrige("tests/donkey.nes")
        self.cartridge = cpu.Cardrige("tests/ice-climber.nes")
        #self.cartridge = cpu.Cardrige("tests/tank1990.nes")

        #self.cartridge = cpu.Cardrige("tests/dizzy-adventure.nes")
        #self.cartridge = cpu.Cardrige("tests/duck-tale-2.nes")
        #self.cartridge = cpu.Cardrige("tests/Contra.nes")

        #self.cartridge = cpu.Cardrige("tests/big-nose-freaks-out.nes")
        #self.cartridge = cpu.Cardrige("tests/big-nose-cave-man.nes")

        #self.cartridge = cpu.Cardrige("tests/goal3.nes")
        #self.cartridge = cpu.Cardrige("tests/demo_ntsc.nes")
        #self.cartridge = cpu.Cardrige("tests/vram_access.nes")
        #self.cartridge = cpu.Cardrige("tests/palette_ram.nes")
        #self.cartridge = cpu.Cardrige("tests/vbl_clear_time.nes")
        #self.cartridge = cpu.Cardrige("tests/scanline.nes")
        #self.cartridge = cpu.Cardrige("tests/allpads.nes")
        #self.cartridge = cpu.Cardrige("tests/read_joy3/test_buttons.nes")
        #self.cartridge = cpu.Cardrige("tests/quatro-arcade.nes")

        #self.cartridge = cpu.Cardrige("tests/instr_test-v5/all_instrs.nes")
        self.screen = screen
        #self.ppu = ppu.Ppu(screen, self.cartridge)
        self.ppu = ppu_cpp.PpuCpp(self.cartridge.chr, self.cartridge.mirroring)
        self.bus = cpu.Bus()
        self.c = cpu.Cpu(self.bus, 0xC000)
        self.ram = cpu.RamMemory()
        #self.cartridge = cpu.Cardrige(0xC000, [])#data[16:16 + 16384])
        self.apu = cpu.Apu()

        self.bus.connect(self.cartridge)
        self.bus.connect(self.ram)
        self.bus.connect(self.ppu)
        self.bus.connect(self.apu)
        self.num_of_cycles = 1

        self.write_complete = False
        self.odd_cycle_checked = False
        self.dma_data = 0x00
        self.dma_offset = 0x00

        self.cpu_cycles_to_add = 0

    """
    def get_pressed_button(self):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.apu.pressed_up()
                elif event.key == pygame.K_DOWN:
                    self.apu.pressed_down()
                elif event.key == pygame.K_LEFT:
                    self.apu.pressed_left()
                    #print("key left - enable print")
                    #self.c.enable_print = True
                elif event.key == pygame.K_RIGHT:
                    self.apu.pressed_right()
                    #print("key right - disable print")
                    #self.c.enable_print = False
                elif event.key == pygame.K_RETURN:
                    self.apu.pressed_start()
                elif event.key == pygame.K_1:
                    self.apu.select_pressed()
    """

    def start(self):
        i=0
        while True:
        #while i < 8000000:
            self.ppu.clock()
            if self.num_of_cycles % 3 == 0:
                if self.bus.dma_request:
                    # suspend CPU, it takes 513/514 clock cycles
                    if self.write_complete == False:
                        self.write_complete = True
                    elif self.odd_cycle_checked == False and self.num_of_cycles % 2 == 1:
                        self.odd_cycle_checked = True
                        self.cpu_cycles_to_add += 1
                    else:
                        if self.num_of_cycles % 2 == 0:
                            # read data
                            addr = (self.bus.dma_high_byte << 8) | self.dma_offset
                            #print("PPU OAM read from addr:{}".format(hex(addr)))
                            self.dma_data = self.c.read((self.bus.dma_high_byte << 8) | self.dma_offset)
                        else:
                            # write data to ppu
                            #print("PPU OAM write idx:{}   data:{}".format(self.dma_offset, hex(self.dma_data)))
                            self.ppu.write_oam_data(self.dma_offset, self.dma_data)
                            self.dma_offset += 1
                            if self.dma_offset > 0xff:
                                self.cpu_cycles_to_add += 513
                                self.bus.dma_request = False
                                self.write_complete = False
                                self.odd_cycle_checked = False
                                self.dma_offset = 0x00
                                self.c.clock_ticks += self.cpu_cycles_to_add
                                #print("add extra ticks: {}".format(self.cpu_cycles_to_add))
                                self.cpu_cycles_to_add = 0
                else:
                    self.c.clock()

            if self.ppu.raise_nmi and self.c.new_instruction:
                #print("NMI request cyc:{}".format(self.c.clock_ticks))
                if self.c.clock_ticks == 1010347:
                    j=3
                self.c.nmi()
                #fh = open("log.txt", "a")
                #fh.write("[NMI - Cycle: {}]\r\n".format(self.c.clock_ticks))
                #fh.close()
                self.ppu.raise_nmi = False
                #print("[NMI - Cycle: {}]".format(self.c.clock_ticks))
                #self.ppu.cycle += 21

                #self.screen.update(self.ppu.get_frame_data())
                #self.screen.update(self.ppu.screen_data)
                if self.ppu.render_background:
                    self.screen.update(self.ppu.screen_data)

            self.num_of_cycles += 1

            #self.get_pressed_button()
            i+=1

    def reset(self):
        self.c.reset()
        self.ppu.reset()


class Screen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((256*4, 240*4))   # return surface

    def update(self, frameN):
        a = np.transpose(np.array(frameN).reshape(240, 256))
        surface = pygame.Surface((256, 240))
        pygame.surfarray.blit_array(surface, a)
        sc = pygame.transform.scale(surface, (256 * 4, 240 * 4))
        self.screen.blit(sc, (0, 0))
        pygame.display.update()


def nes_main():
    screen = Screen()
    nes = Nes(screen)
    nes.reset()
    nes.start()


def nes_main_profile():
    profiler = cProfile.Profile()
    profiler.enable()
    nes_main()
    profiler.disable()
    #stats = pstats.Stats(profiler).sort_stats('tottime')
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()


if __name__ == "__main__":
    print("NES emulator")

    nes_main()
    #nes_main_profile()

