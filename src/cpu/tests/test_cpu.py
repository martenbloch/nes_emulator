import pytest
from src.cpu import cpu
from src.cpu import ppu
from src.cpu import screen

from unittest.mock import Mock

"""
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
"""


def test_sbc_case_1():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x85)

    cpu_mock = Mock()
    cpu_mock.a = 0xFF
    cpu_mock.read.return_value = 0x28
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0xD7 == cpu_mock.a
    assert 0x85 == status_register.to_byte()


def test_sbc_case_2():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x07)

    cpu_mock = Mock()
    cpu_mock.a = 0x00
    cpu_mock.read.return_value = 0x00
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x00 == cpu_mock.a
    assert 0x07 == status_register.to_byte()


def test_sbc_case_3():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x07
    cpu_mock.read.return_value = 0x01
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x06 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_4():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x04
    cpu_mock.read.return_value = 0x04
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x00 == cpu_mock.a
    assert 0x07 == status_register.to_byte()


def test_sbc_case_5():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x08
    cpu_mock.read.return_value = 0x01
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x07 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_6():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x09
    cpu_mock.read.return_value = 0x01
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x08 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_7():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x0C
    cpu_mock.read.return_value = 0x04
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x08 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_8():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x10
    cpu_mock.read.return_value = 0x04
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x0C == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_9():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x01
    cpu_mock.read.return_value = 0x01
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x00 == cpu_mock.a
    assert 0x07 == status_register.to_byte()


def test_sbc_case_10():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x01
    cpu_mock.read.return_value = 0x00
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x01 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_11():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x06
    cpu_mock.read.return_value = 0x06
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x00 == cpu_mock.a
    assert 0x07 == status_register.to_byte()


def test_sbc_case_11():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x01
    cpu_mock.read.return_value = 0x00
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x00 == cpu_mock.a
    assert 0x07 == status_register.to_byte()


def test_sbc_case_12():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x01
    cpu_mock.read.return_value = 0x01
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0xFF == cpu_mock.a
    assert 0x84 == status_register.to_byte()


def test_sbc_case_13():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x85)

    cpu_mock = Mock()
    cpu_mock.a = 0xFF
    cpu_mock.read.return_value = 0xB0
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x4F == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_14():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x1C
    cpu_mock.read.return_value = 0x08
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x14 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_15():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x04
    cpu_mock.read.return_value = 0x08
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0xFC == cpu_mock.a
    assert 0x84 == status_register.to_byte()


def test_sbc_case_16():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x07)

    cpu_mock = Mock()
    cpu_mock.a = 0x00
    cpu_mock.read.return_value = 0xB0
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x50 == cpu_mock.a
    assert 0x04 == status_register.to_byte()


def test_sbc_case_17():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x85)

    cpu_mock = Mock()
    cpu_mock.a = 0xDF
    cpu_mock.read.return_value = 0x80
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0x5F == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_sbc_case_18():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x05)

    cpu_mock = Mock()
    cpu_mock.a = 0x5F
    cpu_mock.read.return_value = 0x80
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    sbc_instr = cpu.Sbc(cpu_mock, addr_mode_mock)
    sbc_instr.execute()

    assert 0xDF == cpu_mock.a
    assert 0xC4 == status_register.to_byte()


def test_and_case_1():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x06)

    cpu_mock = Mock()
    cpu_mock.a = 0x54
    cpu_mock.read.return_value = 0x0F
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.And(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x04 == cpu_mock.a
    assert 0x04 == status_register.to_byte()


def test_rol_case_1():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x20
    cpu_mock.read.return_value = 0xAE
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Rol(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x20 == cpu_mock.a
    assert 0x05 == status_register.to_byte()


def test_rol_case_2():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x20
    cpu_mock.read.return_value = 0x5C
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Rol(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x20 == cpu_mock.a
    assert 0x84 == status_register.to_byte()


def test_rol_case_3():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x20
    cpu_mock.read.return_value = 0x00
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Rol(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x20 == cpu_mock.a
    assert 0x06 == status_register.to_byte()


def test_rol_case_4():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x20
    cpu_mock.read.return_value = 0x80
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Rol(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x20 == cpu_mock.a
    assert 0x07 == status_register.to_byte()


def test_rol_case_5():
    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x20
    cpu_mock.read.return_value = 0xC0
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Rol(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x20 == cpu_mock.a
    assert 0x85 == status_register.to_byte()


def test_bit_case_1():

    status_register = cpu.StatusRegister()
    status_register.from_byte(0x04)

    cpu_mock = Mock()
    cpu_mock.a = 0x40
    cpu_mock.read.return_value = 0x00
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Bit(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x06 == status_register.to_byte()


def test_bit_case_2():

    status_register = cpu.StatusRegister()
    status_register.from_byte(0x06)

    cpu_mock = Mock()
    cpu_mock.a = 0x40
    cpu_mock.read.return_value = 0x40
    cpu_mock.read()
    cpu_mock.sr = status_register

    addr_mode_mock = Mock()

    and_instr = cpu.Bit(cpu_mock, addr_mode_mock)
    and_instr.execute()

    assert 0x44 == status_register.to_byte()
