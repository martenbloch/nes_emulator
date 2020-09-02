import pytest
from src.cpu import cpu


def test_cpu():
    #f = open("cpu/tests/nestest.nes", "rb")
    #data = f.read()
    #f.close()

    bus = cpu.Bus()
    c = cpu.Cpu(bus, 0xC000)
    ram = cpu.RamMemory()
    cartridge = cpu.Cardrige("cpu/tests/nestest.nes")
    apu = cpu.Apu()
    bus.connect(ram)
    bus.connect(cartridge)
    bus.connect(apu)

    i = 1
    while True:
        print(i)
        if i == 8991:
            x=3
            c.clock()
            break
        c.clock()
        i += 1

