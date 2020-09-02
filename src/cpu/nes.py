from src.cpu import cpu
from src.cpu import ppu
from src.cpu import frame
import pygame


class Nes:
    def __init__(self, screen):
        self.ppu = ppu.Ppu(screen)
        self.bus = cpu.Bus()
        self.c = cpu.Cpu(self.bus, 0xC000)
        self.ram = cpu.RamMemory()
        #self.cartridge = cpu.Cardrige(0xC000, [])#data[16:16 + 16384])
        self.cartridge = cpu.Cardrige("tests/nestest.nes")
        self.apu = cpu.Apu()
        self.bus.connect(self.ram)
        self.bus.connect(self.cartridge)
        self.bus.connect(self.apu)
        self.num_of_cycles = 0

    def start(self):
        #i=1
        while True:

            self.ppu.clock()
            if self.num_of_cycles % 3 == 0:
                #print(i)
                #self.c.clock()
                #i += 1
                pass
            self.num_of_cycles += 1


class Screen:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((341, 262))
        pygame.display.update()

    def update(self, frame):
        d = frame.get_data()
        for x in range(341):
            for y in range(262):
                self.screen.fill(d[x][y], ((x, y), (1, 1)))

        pygame.display.update()


if __name__ == "__main__":
    print("NES emulator")

    screen = Screen()
    nes = Nes(screen)
    nes.start()

