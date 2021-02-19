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

        # MAPPER 0
        #self.cartridge = cpu.Cardrige("tests/nestest.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/super-mario-bros.nes")
        #self.cartridge = cpu.Cardrige("tests/donkey.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/ice-climber.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/tank1990.nes")

        # MAPPER 1
        #self.cartridge = cpu.Cardrige("tests/darkwing-duck.nes")

        # MAPPER 2
        #self.cartridge = cpu.Cardrige("tests/pegasus/duck-tale-2.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/contra.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/castlevania.nes")

        # MAPPER 4
        #self.cartridge = cpu.Cardrige("tests/goal3.nes")
        #self.cartridge = cpu.Cardrige("tests/capitan-america.nes")

        # MAPPER 64
        #self.cartridge = cpu.Cardrige("tests/ballon-fight.nes")

        # MAPPER 71
        #self.cartridge = cpu.Cardrige("tests/pegasus/dizzy.nes")
        self.cartridge = cpu.Cardrige("tests/pegasus/big-nose-freaks-out.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/big-nose-caveman.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/ultimate-stuntman.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/micro-machines.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/fire-hawk.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/linus.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/srh.nes")

        # MAPPER 232
        #self.cartridge = cpu.Cardrige("tests/pegasus/quattro-arcade.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/quattro-a.nes")
        #self.cartridge = cpu.Cardrige("tests/pegasus/q1.nes")

        self.screen = screen
        #self.ppu = ppu.Ppu(screen, self.cartridge)
        self.ppu = ppu_cpp.PpuCpp(self.cartridge.chr, self.cartridge.mirroring)
        self.bus = cpu.Bus()
        self.c = cpu.Cpu(self.bus, 0xC000)
        self.ram = cpu.RamMemory()
        self.apu = cpu.Apu()

        self.bus.connect(self.cartridge)
        self.bus.connect(self.ram)
        self.bus.connect(self.ppu)
        self.bus.connect(self.apu)
        self.num_of_cycles = 1

        self.write_complete = False
        self.dma_data = 0x00
        self.dma_offset = 0x00

        self.dummy_dma = True

    def start(self):
        i=0
        #self.c.enable_print = True

        while True:
        #while i < 8000000:
            self.ppu.clock()
            if self.num_of_cycles % 3 == 0:
                if self.bus.dma_request:
                    # before start we have to wait 1/2 idle cycles
                    if self.dummy_dma == True:
                        if self.c.clock_ticks % 2 == 0:
                            self.dummy_dma = False
                        else:
                            self.c.clock_ticks += 1
                    else:
                        if self.c.clock_ticks % 2 == 0:
                            self.dma_data = self.c.read((self.bus.dma_high_byte << 8) | self.dma_offset)
                        else:
                            self.ppu.write_oam_data(self.dma_offset, self.dma_data)
                            self.dma_offset += 1
                            if self.dma_offset > 0xff:
                                self.bus.dma_request = False
                                self.write_complete = False
                                self.dma_offset = 0x00
                                self.dummy_dma = True
                                self.c.clock_ticks += 1
                        self.c.clock_ticks += 1
                else:
                    self.c.clock()

            if self.ppu.raise_nmi and self.c.cycles_left_to_perform_current_instruction != 0:
                self.c.nmi()
                if self.c.enable_print:
                    fh = open("log.txt", "a")
                    fh.write("[NMI - Cycle: {}]\r\n".format(self.c.clock_ticks-1))
                    fh.close()
                self.ppu.raise_nmi = False
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

