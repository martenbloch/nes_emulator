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

    #c.reset()
    while True:
        if c.pc == 0xC66E:
            break
        if c.clock_ticks == 13893:
            x=3
        c.clock()


