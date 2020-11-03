import pytest
from src.cpu import cpu
from src.cpu import ppu
from src.cpu import screen


def test_cpu():

    bus = cpu.Bus()
    c = cpu.Cpu(bus, 0xC000)
    ram = cpu.RamMemory()
    cartridge = cpu.Cardrige("cpu/tests/nestest.nes")
    apu = cpu.Apu()
    s = screen.Screen()
    p = ppu.Ppu(s, cartridge)
    bus.connect(ram)
    bus.connect(cartridge)
    bus.connect(apu)
    bus.connect(p)

    c.enable_print = True
    #c.reset()
    p.cycle = 18
    c.sr.from_byte(0x24)
    i=0
    num_of_cycles = 1
    while True:
        p.clock()
        if num_of_cycles % 3 == 0:
            c.clock()

        #if i == 500:
        #    break
        i+=1
        num_of_cycles += 1



