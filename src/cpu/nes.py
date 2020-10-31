from src.cpu import cpu
from src.cpu import ppu
from src.cpu import frame
import pygame


class Nes:
    def __init__(self, screen):
        #self.cartridge = cpu.Cardrige("tests/nestest.nes")
        self.cartridge = cpu.Cardrige("tests/mario-bros.nes")
        #self.cartridge = cpu.Cardrige("tests/donkey.nes")
        #self.cartridge = cpu.Cardrige("tests/ice-climber.nes")
        #self.cartridge = cpu.Cardrige("tests/tank1990.nes")
        #self.cartridge = cpu.Cardrige("tests/goal3.nes")
        #self.cartridge = cpu.Cardrige("tests/demo_ntsc.nes")
        #self.cartridge = cpu.Cardrige("tests/vram_access.nes")
        #self.cartridge = cpu.Cardrige("tests/palette_ram.nes")
        #self.cartridge = cpu.Cardrige("tests/vbl_clear_time.nes")
        #self.cartridge = cpu.Cardrige("tests/scanline.nes")

        self.ppu = ppu.Ppu(screen, self.cartridge)
        self.bus = cpu.Bus()
        self.c = cpu.Cpu(self.bus, 0xC000)
        self.ram = cpu.RamMemory()
        #self.cartridge = cpu.Cardrige(0xC000, [])#data[16:16 + 16384])
        self.apu = cpu.Apu()
        self.bus.connect(self.ram)
        self.bus.connect(self.cartridge)
        self.bus.connect(self.apu)
        self.bus.connect(self.ppu)
        self.num_of_cycles = 1

    def start(self):
        while True:
            self.ppu.clock()
            if self.num_of_cycles % 3 == 0:
                self.c.clock()

            if self.ppu.raise_nmi and self.c.new_instruction:
                print("NMI request cyc:{}".format(self.c.clock_ticks))
                self.c.nmi()
                fh = open("log.txt", "a")
                fh.write("[NMI - Cycle: {}]\r\n".format(self.c.clock_ticks))
                fh.close()
                self.ppu.raise_nmi = False
                self.ppu.cycle += 21

            self.num_of_cycles += 1

    def reset(self):
        self.c.reset()
        self.ppu.reset()


class Screen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((256*4, 240*4))
        pygame.display.update()

    def update(self, frame):
        d = frame.get_data()
        for x in range(341):
            for y in range(262):
                self.screen.fill(d[x][y], ((x*4, y*4), (4, 4)))

        pygame.display.update()


if __name__ == "__main__":
    print("NES emulator")

    screen = Screen()
    nes = Nes(screen)
    nes.reset()
    nes.start()

