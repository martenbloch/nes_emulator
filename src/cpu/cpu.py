import pygame


class Bus:

    def __init__(self):
        self.__devices = []
        self.dma_request = False
        self.dma_high_byte = 0x00

    def write(self, address, data):

        if address != 0x4014:
            d = self.get_device_by_address(address)
            if d:
                d.write(address, data)
            else:
                raise Exception("device not found for address: {}".format(hex(address)))

        else:
            self.dma_high_byte = data
            self.dma_request = True

    def read(self, address, num_bytes=1):
        if address != 0x4014:
            d = self.get_device_by_address(address)
            if d:
                return d.read(address)
            else:
                raise Exception("device not found for address: {}".format(hex(address)))
        else:
            return self.dma_high_byte  # TODO: implement it

    def read_many(self, address, num_bytes=1):
        d = self.get_device_by_address(address)
        if d:
            return d.read_many(address, num_bytes)
        else:
            raise Exception("device not found for address: {}".format(hex(address)))

    def get_device_by_address(self, address):
        for d in self.__devices:
            if d.is_address_valid(address):
                return d
        return None

    def connect(self, device):
        self.__devices.append(device)


LOG_WIDTH = 32


class Cpu:

    def __init__(self, bus, pc=0):
        # program counter 16 bit
        self.pc = pc

        self.enable_print = False

        # status register 8 bit
        self.sr = StatusRegister()

        self.clock_ticks = 7

        self.bus = bus

        self.a = 0
        self.x = 0
        self.y = 0
        self.sp = 0xFD    # end of stack

        self.operand = 0x00

        self.instructions = [None for i in range(256)]
        self.instructions[0x61] = Adc(self, AddressModeIndirectX(self))
        self.instructions[0x65] = Adc(self, AddressModeZeroPage(self))
        self.instructions[0x69] = Adc(self, AddressModeImmediate(self))
        self.instructions[0x6D] = Adc(self, AddressModeAbsolute(self))
        self.instructions[0x71] = Adc(self, AddressModeIndirectY(self))
        self.instructions[0x75] = Adc(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0x79] = Adc(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0x7D] = Adc(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0x21] = And(self, AddressModeIndirectX(self))
        self.instructions[0x25] = And(self, AddressModeZeroPage(self))
        self.instructions[0x29] = And(self, AddressModeImmediate(self))
        self.instructions[0x2D] = And(self, AddressModeAbsolute(self))
        self.instructions[0x31] = And(self, AddressModeIndirectY(self))
        self.instructions[0x35] = And(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0x39] = And(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0x3D] = And(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0x06] = Asl(self, AddressModeZeroPage(self, 5))
        self.instructions[0x0A] = Asl(self, AddressModeAccumulator(self))
        self.instructions[0x0E] = Asl(self, AddressModeAbsolute(self, 6))
        self.instructions[0x16] = Asl(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x1E] = Asl(self, AddressModeAbsoluteXIndexed(self, 7))

        self.instructions[0x90] = Bcc(self, AddressModeRelative(self))

        self.instructions[0xB0] = Bcs(self, AddressModeRelative(self))

        self.instructions[0xF0] = Beq(self, AddressModeRelative(self))

        self.instructions[0x24] = Bit(self, AddressModeZeroPage(self))
        self.instructions[0x2C] = Bit(self, AddressModeAbsolute(self))

        self.instructions[0x30] = Bmi(self, AddressModeRelative(self))

        self.instructions[0xD0] = Bne(self, AddressModeRelative(self))

        self.instructions[0x10] = Bpl(self, AddressModeRelative(self))

        self.instructions[0x00] = Brk(self, AddressModeImplied(7))

        self.instructions[0x50] = Bvc(self, AddressModeRelative(self))

        self.instructions[0x70] = Bvs(self, AddressModeRelative(self))

        self.instructions[0x18] = Clc(self, AddressModeImplied())

        self.instructions[0xD8] = Cld(self, AddressModeImplied())

        self.instructions[0x58] = Cli(self, AddressModeImplied())

        self.instructions[0xB8] = Clv(self, AddressModeImplied())

        self.instructions[0xC1] = Cmp(self, AddressModeIndirectX(self))
        self.instructions[0xC5] = Cmp(self, AddressModeZeroPage(self))
        self.instructions[0xC9] = Cmp(self, AddressModeImmediate(self))
        self.instructions[0xCD] = Cmp(self, AddressModeAbsolute(self))
        self.instructions[0xD1] = Cmp(self, AddressModeIndirectY(self))
        self.instructions[0xD5] = Cmp(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0xD9] = Cmp(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0xDD] = Cmp(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0xE0] = Cpx(self, AddressModeImmediate(self))
        self.instructions[0xE4] = Cpx(self, AddressModeZeroPage(self))
        self.instructions[0xEC] = Cpx(self, AddressModeAbsolute(self))

        self.instructions[0xC0] = Cpy(self, AddressModeImmediate(self))
        self.instructions[0xC4] = Cpy(self, AddressModeZeroPage(self))
        self.instructions[0xC4] = Cpy(self, AddressModeZeroPage(self))
        self.instructions[0xCC] = Cpy(self, AddressModeAbsolute(self))

        self.instructions[0xC3] = Dcp(self, AddressModeIndirectX(self, 8))
        self.instructions[0xC7] = Dcp(self, AddressModeZeroPage(self, 5))
        self.instructions[0xCF] = Dcp(self, AddressModeAbsolute(self, 6))
        self.instructions[0xD3] = Dcp(self, AddressModeIndirectY(self, 8, False))
        self.instructions[0xD7] = Dcp(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0xDB] = Dcp(self, AddressModeAbsoluteYIndexed(self, 7, False))
        self.instructions[0xDF] = Dcp(self, AddressModeAbsoluteXIndexed(self, 7, False))

        self.instructions[0xC6] = Dec(self, AddressModeZeroPage(self, 5))
        self.instructions[0xCE] = Dec(self, AddressModeAbsolute(self, 6))
        self.instructions[0xD6] = Dec(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0xDE] = Dec(self, AddressModeAbsoluteXIndexed(self, 7))

        self.instructions[0xCA] = Dex(self, AddressModeImplied())

        self.instructions[0x88] = Dey(self, AddressModeImplied())

        self.instructions[0x41] = Eor(self, AddressModeIndirectX(self))
        self.instructions[0x45] = Eor(self, AddressModeZeroPage(self))
        self.instructions[0x49] = Eor(self, AddressModeImmediate(self))
        self.instructions[0x4D] = Eor(self, AddressModeAbsolute(self))
        self.instructions[0x51] = Eor(self, AddressModeIndirectY(self))
        self.instructions[0x55] = Eor(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0x59] = Eor(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0x5D] = Eor(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0xE6] = Inc(self, AddressModeZeroPage(self, 5))
        self.instructions[0xEE] = Inc(self, AddressModeAbsolute(self, 6))
        self.instructions[0xF6] = Inc(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0xFE] = Inc(self, AddressModeAbsoluteXIndexed(self, 7))

        self.instructions[0xE8] = Inx(self, AddressModeImplied())

        self.instructions[0xC8] = Iny(self, AddressModeImplied())

        self.instructions[0xE3] = Isb(self, AddressModeIndirectX(self, 8))
        self.instructions[0xE7] = Isb(self, AddressModeZeroPage(self, 5))
        self.instructions[0xEF] = Isb(self, AddressModeAbsolute(self, 6))
        self.instructions[0xF3] = Isb(self, AddressModeIndirectY(self, 8, False))
        self.instructions[0xF7] = Isb(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0xFB] = Isb(self, AddressModeAbsoluteYIndexed(self, 7, False))
        self.instructions[0xFF] = Isb(self, AddressModeAbsoluteXIndexed(self, 7, False))

        self.instructions[0x4C] = Jmp(self, AddressModeAbsolute(self, 3))
        self.instructions[0x6C] = Jmp(self, AddressModeIndirect(self, 5))

        self.instructions[0x20] = Jsr(self, AddressModeAbsolute(self, 6))

        self.instructions[0xA3] = Lax(self, AddressModeIndirectX(self))
        self.instructions[0xAF] = Lax(self, AddressModeAbsolute(self))
        self.instructions[0xB3] = Lax(self, AddressModeIndirectY(self))
        self.instructions[0xB7] = Lax(self, AddressModeZeroPageYIndexed(self))
        self.instructions[0xBF] = Lax(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0xA7] = Lax(self, AddressModeZeroPage(self))

        self.instructions[0xA1] = Lda(self, AddressModeIndirectX(self))
        self.instructions[0xA5] = Lda(self, AddressModeZeroPage(self))
        self.instructions[0xA9] = Lda(self, AddressModeImmediate(self))
        self.instructions[0xAD] = Lda(self, AddressModeAbsolute(self))
        self.instructions[0xB1] = Lda(self, AddressModeIndirectY(self))
        self.instructions[0xB5] = Lda(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0xB9] = Lda(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0xBD] = Lda(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0xA2] = Ldx(self, AddressModeImmediate(self))
        self.instructions[0xA6] = Ldx(self, AddressModeZeroPage(self))
        self.instructions[0xAE] = Ldx(self, AddressModeAbsolute(self))
        self.instructions[0xB6] = Ldx(self, AddressModeZeroPageYIndexed(self))
        self.instructions[0xBE] = Ldx(self, AddressModeAbsoluteYIndexed(self, 4))

        self.instructions[0xA0] = Ldy(self, AddressModeImmediate(self))
        self.instructions[0xA4] = Ldy(self, AddressModeZeroPage(self))
        self.instructions[0xAC] = Ldy(self, AddressModeAbsolute(self))
        self.instructions[0xB4] = Ldy(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0xBC] = Ldy(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0x46] = Lsr(self, AddressModeZeroPage(self, 5))
        self.instructions[0x4A] = Lsr(self, AddressModeAccumulator(self))
        self.instructions[0x4E] = Lsr(self, AddressModeAbsolute(self, 6))
        self.instructions[0x56] = Lsr(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x5E] = Lsr(self, AddressModeAbsoluteXIndexed(self, 7))

        self.instructions[0x04] = Nop(AddressModeZeroPage(self))
        self.instructions[0x0C] = Nop(AddressModeAbsolute(self))
        self.instructions[0x14] = Nop(AddressModeZeroPageXIndexed(self))
        self.instructions[0x1A] = Nop(AddressModeImplied())
        self.instructions[0x1C] = Nop(AddressModeAbsoluteXIndexed(self, 4))
        self.instructions[0x34] = Nop(AddressModeZeroPageXIndexed(self))
        self.instructions[0x3A] = Nop(AddressModeImplied())
        self.instructions[0x3C] = Nop(AddressModeAbsoluteXIndexed(self, 4))  # TODO: duplication here
        self.instructions[0x54] = Nop(AddressModeZeroPageXIndexed(self))
        self.instructions[0x5A] = Nop(AddressModeImplied())
        self.instructions[0x7A] = Nop(AddressModeImplied())
        self.instructions[0x44] = Nop(AddressModeZeroPage(self))
        self.instructions[0x5C] = Nop(AddressModeAbsoluteXIndexed(self, 4))  # TODO: duplication here
        self.instructions[0x64] = Nop(AddressModeZeroPage(self))
        self.instructions[0x74] = Nop(AddressModeZeroPageXIndexed(self))
        self.instructions[0x7C] = Nop(AddressModeAbsoluteXIndexed(self, 4))  # TODO: duplication here
        self.instructions[0x80] = Nop(AddressModeImmediate(self))
        self.instructions[0xD4] = Nop(AddressModeZeroPageXIndexed(self))
        self.instructions[0xDA] = Nop(AddressModeImplied())
        self.instructions[0xDC] = Nop(AddressModeAbsoluteXIndexed(self, 4))  # TODO: duplication here
        self.instructions[0xEA] = Nop(AddressModeImplied())
        self.instructions[0xF4] = Nop(AddressModeZeroPageXIndexed(self))
        self.instructions[0xFA] = Nop(AddressModeImplied())
        self.instructions[0xFC] = Nop(AddressModeAbsoluteXIndexed(self, 4)) # TODO: duplication here

        self.instructions[0x01] = Ora(self, AddressModeIndirectX(self))
        self.instructions[0x05] = Ora(self, AddressModeZeroPage(self))
        self.instructions[0x09] = Ora(self, AddressModeImmediate(self))
        self.instructions[0x0D] = Ora(self, AddressModeAbsolute(self))
        self.instructions[0x11] = Ora(self, AddressModeIndirectY(self))
        self.instructions[0x15] = Ora(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0x19] = Ora(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0x1D] = Ora(self, AddressModeAbsoluteXIndexed(self, 4))

        self.instructions[0x48] = Pha(self, AddressModeImplied(3))

        self.instructions[0x08] = Php(self, AddressModeImplied(3))

        self.instructions[0x68] = Pla(self, AddressModeImplied(4))

        self.instructions[0x28] = Plp(self, AddressModeImplied(4))

        self.instructions[0x23] = Rla(self, AddressModeIndirectX(self, 8))
        self.instructions[0x27] = Rla(self, AddressModeZeroPage(self, 5))
        self.instructions[0x2F] = Rla(self, AddressModeAbsolute(self, 6))
        self.instructions[0x33] = Rla(self, AddressModeIndirectY(self, 8, False))
        self.instructions[0x37] = Rla(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x3B] = Rla(self, AddressModeAbsoluteYIndexed(self, 7, False))
        self.instructions[0x3F] = Rla(self, AddressModeAbsoluteXIndexed(self, 7, False))

        self.instructions[0x2A] = Rol(self, AddressModeAccumulator(self))
        self.instructions[0x26] = Rol(self, AddressModeZeroPage(self, 5))
        self.instructions[0x36] = Rol(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x2E] = Rol(self, AddressModeAbsolute(self, 6))
        self.instructions[0x3E] = Rol(self, AddressModeAbsoluteXIndexed(self, 7))

        self.instructions[0x6A] = Ror(self, AddressModeAccumulator(self))
        self.instructions[0x66] = Ror(self, AddressModeZeroPage(self, 5))
        self.instructions[0x76] = Ror(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x6E] = Ror(self, AddressModeAbsolute(self, 6))
        self.instructions[0x7E] = Ror(self, AddressModeAbsoluteXIndexed(self, 7))

        self.instructions[0x63] = Rra(self, AddressModeIndirectX(self, 8))
        self.instructions[0x67] = Rra(self, AddressModeZeroPage(self, 5))
        self.instructions[0x6F] = Rra(self, AddressModeAbsolute(self, 6))
        self.instructions[0x73] = Rra(self, AddressModeIndirectY(self, 8, False))
        self.instructions[0x77] = Rra(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x7B] = Rra(self, AddressModeAbsoluteYIndexed(self, 7, False))
        self.instructions[0x7F] = Rra(self, AddressModeAbsoluteXIndexed(self, 7, False))

        self.instructions[0x40] = Rti(self, AddressModeImplied(6))

        self.instructions[0x60] = Rts(self, AddressModeImplied(6))

        self.instructions[0xCB] = Sax(self, AddressModeImmediate(self))
        self.instructions[0x83] = Sax(self, AddressModeIndirectX(self))
        self.instructions[0x87] = Sax(self, AddressModeZeroPage(self))
        self.instructions[0x8F] = Sax(self, AddressModeAbsolute(self))
        self.instructions[0x97] = Sax(self, AddressModeZeroPageYIndexed(self))

        self.instructions[0xE9] = Sbc(self, AddressModeImmediate(self))
        self.instructions[0xE5] = Sbc(self, AddressModeZeroPage(self))
        self.instructions[0xEB] = Sbc(self, AddressModeImmediate(self))
        self.instructions[0xF5] = Sbc(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0xED] = Sbc(self, AddressModeAbsolute(self))
        self.instructions[0xFD] = Sbc(self, AddressModeAbsoluteXIndexed(self, 4))
        self.instructions[0xF9] = Sbc(self, AddressModeAbsoluteYIndexed(self, 4))
        self.instructions[0xE1] = Sbc(self, AddressModeIndirectX(self))
        self.instructions[0xF1] = Sbc(self, AddressModeIndirectY(self))

        self.instructions[0x38] = Sec(self, AddressModeImplied())

        self.instructions[0xF8] = Sed(self, AddressModeImplied())

        self.instructions[0x78] = Sei(self, AddressModeImplied())

        self.instructions[0x03] = Slo(self, AddressModeIndirectX(self, 8))
        self.instructions[0x07] = Slo(self, AddressModeZeroPage(self, 5))
        self.instructions[0x0F] = Slo(self, AddressModeAbsolute(self, 6))
        self.instructions[0x13] = Slo(self, AddressModeIndirectY(self, 8, False))
        self.instructions[0x17] = Slo(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x1B] = Slo(self, AddressModeAbsoluteYIndexed(self, 7, False))
        self.instructions[0x1F] = Slo(self, AddressModeAbsoluteXIndexed(self, 7, False))

        self.instructions[0x43] = Sre(self, AddressModeIndirectX(self, 8))
        self.instructions[0x47] = Sre(self, AddressModeZeroPage(self, 5))
        self.instructions[0x4F] = Sre(self, AddressModeAbsolute(self, 6))
        self.instructions[0x53] = Sre(self, AddressModeIndirectY(self, 8, False))
        self.instructions[0x57] = Sre(self, AddressModeZeroPageXIndexed(self, 6))
        self.instructions[0x5B] = Sre(self, AddressModeAbsoluteYIndexed(self, 7, False))
        self.instructions[0x5F] = Sre(self, AddressModeAbsoluteXIndexed(self, 7, False))

        self.instructions[0x81] = Sta(self, AddressModeIndirectX(self))
        self.instructions[0x85] = Sta(self, AddressModeZeroPage(self))
        self.instructions[0x8D] = Sta(self, AddressModeAbsolute(self))
        self.instructions[0x91] = Sta(self, AddressModeIndirectY(self, 6, False))
        self.instructions[0x95] = Sta(self, AddressModeZeroPageXIndexed(self, 4))
        self.instructions[0x99] = Sta(self, AddressModeAbsoluteYIndexed(self, 5, False))
        self.instructions[0x9D] = Sta(self, AddressModeAbsoluteXIndexed(self, 5, False))

        self.instructions[0x86] = Stx(self, AddressModeZeroPage(self))
        self.instructions[0x96] = Stx(self, AddressModeZeroPageYIndexed(self))
        self.instructions[0x8E] = Stx(self, AddressModeAbsolute(self))

        self.instructions[0x84] = Sty(self, AddressModeZeroPage(self))
        self.instructions[0x94] = Sty(self, AddressModeZeroPageXIndexed(self))
        self.instructions[0x8C] = Sty(self, AddressModeAbsolute(self))

        self.instructions[0xAA] = Tax(self, AddressModeImplied())

        self.instructions[0xA8] = Tay(self, AddressModeImplied())

        self.instructions[0xBA] = Tsx(self, AddressModeImplied())

        self.instructions[0x8A] = Txa(self, AddressModeImplied())

        self.instructions[0x9A] = Txs(self, AddressModeImplied())

        self.instructions[0x98] = Tya(self, AddressModeImplied())

        self.exec_bit_ins = False
        self.log_msg = ""
        self.cpu_msg = ""

        '''
        self.instructions = {
            0x61: Adc(self, AddressModeIndirectX(self)),
            0x65: Adc(self, AddressModeZeroPage(self)),
            0x69: Adc(self, AddressModeImmediate(self)),
            0x6D: Adc(self, AddressModeAbsolute(self)),
            0x71: Adc(self, AddressModeIndirectY(self)),
            0x75: Adc(self, AddressModeZeroPageXIndexed(self)),
            0x79: Adc(self, AddressModeAbsoluteYIndexed(self, 4)),
            0x7D: Adc(self, AddressModeAbsoluteXIndexed(self, 4)),

            0x21: And(self, AddressModeIndirectX(self)),
            0x25: And(self, AddressModeZeroPage(self)),
            0x29: And(self, AddressModeImmediate(self)),
            0x2D: And(self, AddressModeAbsolute(self)),
            0x31: And(self, AddressModeIndirectY(self)),
            0x35: And(self, AddressModeZeroPageXIndexed(self)),
            0x39: And(self, AddressModeAbsoluteYIndexed(self, 4)),
            0x3D: And(self, AddressModeAbsoluteXIndexed(self, 4)),

            0x06: Asl(self, AddressModeZeroPage(self, 5)),
            0x0A: Asl(self, AddressModeAccumulator(self)),
            0x0E: Asl(self, AddressModeAbsolute(self, 6)),
            0x16: Asl(self, AddressModeZeroPageXIndexed(self, 6)),
            0x1E: Asl(self, AddressModeAbsoluteXIndexed(self, 7)),

            0x90: Bcc(self, AddressModeRelative(self)),

            0xB0: Bcs(self, AddressModeRelative(self)),

            0xF0: Beq(self, AddressModeRelative(self)),

            0x24: Bit(self, AddressModeZeroPage(self)),
            0x2C: Bit(self, AddressModeAbsolute(self)),

            0x30: Bmi(self, AddressModeRelative(self)),

            0xD0: Bne(self, AddressModeRelative(self)),

            0x10: Bpl(self, AddressModeRelative(self)),

            0x00: Brk(self, AddressModeImplied(7)),

            0x50: Bvc(self, AddressModeRelative(self)),

            0x70: Bvs(self, AddressModeRelative(self)),

            0x18: Clc(self, AddressModeImplied()),

            0xD8: Cld(self, AddressModeImplied()),

            0x58: Cli(self, AddressModeImplied()),

            0xB8: Clv(self, AddressModeImplied()),

            0xC1: Cmp(self, AddressModeIndirectX(self)),
            0xC5: Cmp(self, AddressModeZeroPage(self)),
            0xC9: Cmp(self, AddressModeImmediate(self)),
            0xCD: Cmp(self, AddressModeAbsolute(self)),
            0xD1: Cmp(self, AddressModeIndirectY(self)),
            0xD5: Cmp(self, AddressModeZeroPageXIndexed(self)),
            0xD9: Cmp(self, AddressModeAbsoluteYIndexed(self, 4)),
            0xDD: Cmp(self, AddressModeAbsoluteXIndexed(self, 4)),

            0xE0: Cpx(self, AddressModeImmediate(self)),
            0xE4: Cpx(self, AddressModeZeroPage(self)),
            0xEC: Cpx(self, AddressModeAbsolute(self)),

            0xC0: Cpy(self, AddressModeImmediate(self)),
            0xC4: Cpy(self, AddressModeZeroPage(self)),
            0xC4: Cpy(self, AddressModeZeroPage(self)),
            0xCC: Cpy(self, AddressModeAbsolute(self)),

            0xC3: Dcp(self, AddressModeIndirectX(self, 8)),
            0xC7: Dcp(self, AddressModeZeroPage(self, 5)),
            0xCF: Dcp(self, AddressModeAbsolute(self, 6)),
            0xD3: Dcp(self, AddressModeIndirectY(self, 8, False)),
            0xD7: Dcp(self, AddressModeZeroPageXIndexed(self, 6)),
            0xDB: Dcp(self, AddressModeAbsoluteYIndexed(self, 7, False)),
            0xDF: Dcp(self, AddressModeAbsoluteXIndexed(self, 7, False)),

            0xC6: Dec(self, AddressModeZeroPage(self, 5)),
            0xCE: Dec(self, AddressModeAbsolute(self, 6)),
            0xD6: Dec(self, AddressModeZeroPageXIndexed(self, 6)),
            0xDE: Dec(self, AddressModeAbsoluteXIndexed(self, 7)),

            0xCA: Dex(self, AddressModeImplied()),

            0x88: Dey(self, AddressModeImplied()),

            0x41: Eor(self, AddressModeIndirectX(self)),
            0x45: Eor(self, AddressModeZeroPage(self)),
            0x49: Eor(self, AddressModeImmediate(self)),
            0x4D: Eor(self, AddressModeAbsolute(self)),
            0x51: Eor(self, AddressModeIndirectY(self)),
            0x55: Eor(self, AddressModeZeroPageXIndexed(self)),
            0x59: Eor(self, AddressModeAbsoluteYIndexed(self, 4)),
            0x5D: Eor(self, AddressModeAbsoluteXIndexed(self, 4)),

            0xE6: Inc(self, AddressModeZeroPage(self, 5)),
            0xEE: Inc(self, AddressModeAbsolute(self, 6)),
            0xF6: Inc(self, AddressModeZeroPageXIndexed(self, 6)),
            0xFE: Inc(self, AddressModeAbsoluteXIndexed(self, 7)),

            0xE8: Inx(self, AddressModeImplied()),

            0xC8: Iny(self, AddressModeImplied()),

            0xE3: Isb(self, AddressModeIndirectX(self, 8)),
            0xE7: Isb(self, AddressModeZeroPage(self, 5)),
            0xEF: Isb(self, AddressModeAbsolute(self, 6)),
            0xF3: Isb(self, AddressModeIndirectY(self, 8, False)),
            0xF7: Isb(self, AddressModeZeroPageXIndexed(self, 6)),
            0xFB: Isb(self, AddressModeAbsoluteYIndexed(self, 7, False)),
            0xFF: Isb(self, AddressModeAbsoluteXIndexed(self, 7, False)),


            0x4C: Jmp(self, AddressModeAbsolute(self, 3)),
            0x6C: Jmp(self, AddressModeIndirect(self, 5)),

            0x20: Jsr(self, AddressModeAbsolute(self, 6)),

            0xA3: Lax(self, AddressModeIndirectX(self)),
            0xAF: Lax(self, AddressModeAbsolute(self)),
            0xB3: Lax(self, AddressModeIndirectY(self)),
            0xB7: Lax(self, AddressModeZeroPageYIndexed(self)),
            0xBF: Lax(self, AddressModeAbsoluteYIndexed(self, 4)),
            0xA7: Lax(self, AddressModeZeroPage(self)),

            0xA1: Lda(self, AddressModeIndirectX(self)),
            0xA5: Lda(self, AddressModeZeroPage(self)),
            0xA9: Lda(self, AddressModeImmediate(self)),
            0xAD: Lda(self, AddressModeAbsolute(self)),
            0xB1: Lda(self, AddressModeIndirectY(self)),
            0xB5: Lda(self, AddressModeZeroPageXIndexed(self)),
            0xB9: Lda(self, AddressModeAbsoluteYIndexed(self, 4)),
            0xBD: Lda(self, AddressModeAbsoluteXIndexed(self, 4)),

            0xA2: Ldx(self, AddressModeImmediate(self)),
            0xA6: Ldx(self, AddressModeZeroPage(self)),
            0xAE: Ldx(self, AddressModeAbsolute(self)),
            0xB6: Ldx(self, AddressModeZeroPageYIndexed(self)),
            0xBE: Ldx(self, AddressModeAbsoluteYIndexed(self, 4)),

            0xA0: Ldy(self, AddressModeImmediate(self)),
            0xA4: Ldy(self, AddressModeZeroPage(self)),
            0xAC: Ldy(self, AddressModeAbsolute(self)),
            0xB4: Ldy(self, AddressModeZeroPageXIndexed(self)),
            0xBC: Ldy(self, AddressModeAbsoluteXIndexed(self, 4)),

            0x46: Lsr(self, AddressModeZeroPage(self, 5)),
            0x4A: Lsr(self, AddressModeAccumulator(self)),
            0x4E: Lsr(self, AddressModeAbsolute(self, 6)),
            0x56: Lsr(self, AddressModeZeroPageXIndexed(self, 6)),
            0x5E: Lsr(self, AddressModeAbsoluteXIndexed(self, 7)),

            0x04: Nop(AddressModeZeroPage(self)),
            0x0C: Nop(AddressModeAbsolute(self)),
            0x14: Nop(AddressModeZeroPageXIndexed(self)),
            0x1A: Nop(AddressModeImplied()),
            0x1C: Nop(AddressModeAbsoluteXIndexed(self, 4)),
            0x34: Nop(AddressModeZeroPageXIndexed(self)),
            0x3A: Nop(AddressModeImplied()),
            0x3C: Nop(AddressModeAbsoluteXIndexed(self, 4)),    #TODO: duplication here
            0x54: Nop(AddressModeZeroPageXIndexed(self)),
            0x5A: Nop(AddressModeImplied()),
            0x7A: Nop(AddressModeImplied()),
            0x44: Nop(AddressModeZeroPage(self)),
            0x5C: Nop(AddressModeAbsoluteXIndexed(self, 4)),    #TODO: duplication here
            0x64: Nop(AddressModeZeroPage(self)),
            0x74: Nop(AddressModeZeroPageXIndexed(self)),
            0x7C: Nop(AddressModeAbsoluteXIndexed(self, 4)),    #TODO: duplication here
            0x80: Nop(AddressModeImmediate(self)),
            0xD4: Nop(AddressModeZeroPageXIndexed(self)),
            0xDA: Nop(AddressModeImplied()),
            0xDC: Nop(AddressModeAbsoluteXIndexed(self, 4)),    #TODO: duplication here
            0xEA: Nop(AddressModeImplied()),
            0xF4: Nop(AddressModeZeroPageXIndexed(self)),
            0xFA: Nop(AddressModeImplied()),
            0xFC: Nop(AddressModeAbsoluteXIndexed(self, 4)),    #TODO: duplication here

            0x01: Ora(self, AddressModeIndirectX(self)),
            0x05: Ora(self, AddressModeZeroPage(self)),
            0x09: Ora(self, AddressModeImmediate(self)),
            0x0D: Ora(self, AddressModeAbsolute(self)),
            0x11: Ora(self, AddressModeIndirectY(self)),
            0x15: Ora(self, AddressModeZeroPageXIndexed(self)),
            0x19: Ora(self, AddressModeAbsoluteYIndexed(self, 4)),
            0x1D: Ora(self, AddressModeAbsoluteXIndexed(self, 4)),

            0x48: Pha(self, AddressModeImplied(3)),

            0x08: Php(self, AddressModeImplied(3)),

            0x68: Pla(self, AddressModeImplied(4)),

            0x28: Plp(self, AddressModeImplied(4)),

            0x23: Rla(self, AddressModeIndirectX(self, 8)),
            0x27: Rla(self, AddressModeZeroPage(self, 5)),
            0x2F: Rla(self, AddressModeAbsolute(self, 6)),
            0x33: Rla(self, AddressModeIndirectY(self, 8, False)),
            0x37: Rla(self, AddressModeZeroPageXIndexed(self, 6)),
            0x3B: Rla(self, AddressModeAbsoluteYIndexed(self, 7, False)),
            0x3F: Rla(self, AddressModeAbsoluteXIndexed(self, 7, False)),

            0x2A: Rol(self, AddressModeAccumulator(self)),
            0x26: Rol(self, AddressModeZeroPage(self, 5)),
            0x36: Rol(self, AddressModeZeroPageXIndexed(self, 6)),
            0x2E: Rol(self, AddressModeAbsolute(self, 6)),
            0x3E: Rol(self, AddressModeAbsoluteXIndexed(self, 7)),

            0x6A: Ror(self, AddressModeAccumulator(self)),
            0x66: Ror(self, AddressModeZeroPage(self, 5)),
            0x76: Ror(self, AddressModeZeroPageXIndexed(self, 6)),
            0x6E: Ror(self, AddressModeAbsolute(self, 6)),
            0x7E: Ror(self, AddressModeAbsoluteXIndexed(self, 7)),

            0x63: Rra(self, AddressModeIndirectX(self, 8)),
            0x67: Rra(self, AddressModeZeroPage(self, 5)),
            0x6F: Rra(self, AddressModeAbsolute(self, 6)),
            0x73: Rra(self, AddressModeIndirectY(self, 8, False)),
            0x77: Rra(self, AddressModeZeroPageXIndexed(self, 6)),
            0x7B: Rra(self, AddressModeAbsoluteYIndexed(self, 7, False)),
            0x7F: Rra(self, AddressModeAbsoluteXIndexed(self, 7, False)),

            0x40: Rti(self, AddressModeImplied(6)),

            0x60: Rts(self, AddressModeImplied(6)),

            0xCB: Sax(self, AddressModeImmediate(self)),
            0x83: Sax(self, AddressModeIndirectX(self)),
            0x87: Sax(self, AddressModeZeroPage(self)),
            0x8F: Sax(self, AddressModeAbsolute(self)),
            0x97: Sax(self, AddressModeZeroPageYIndexed(self)),

            0xE9: Sbc(self, AddressModeImmediate(self)),
            0xE5: Sbc(self, AddressModeZeroPage(self)),
            0xEB: Sbc(self, AddressModeImmediate(self)),
            0xF5: Sbc(self, AddressModeZeroPageXIndexed(self)),
            0xED: Sbc(self, AddressModeAbsolute(self)),
            0xFD: Sbc(self, AddressModeAbsoluteXIndexed(self, 4)),
            0xF9: Sbc(self, AddressModeAbsoluteYIndexed(self, 4)),
            0xE1: Sbc(self, AddressModeIndirectX(self)),
            0xF1: Sbc(self, AddressModeIndirectY(self)),

            0x38: Sec(self, AddressModeImplied()),

            0xF8: Sed(self, AddressModeImplied()),

            0x78: Sei(self, AddressModeImplied()),

            0x03: Slo(self, AddressModeIndirectX(self, 8)),
            0x07: Slo(self, AddressModeZeroPage(self, 5)),
            0x0F: Slo(self, AddressModeAbsolute(self, 6)),
            0x13: Slo(self, AddressModeIndirectY(self, 8, False)),
            0x17: Slo(self, AddressModeZeroPageXIndexed(self, 6)),
            0x1B: Slo(self, AddressModeAbsoluteYIndexed(self, 7, False)),
            0x1F: Slo(self, AddressModeAbsoluteXIndexed(self, 7, False)),

            0x43: Sre(self, AddressModeIndirectX(self, 8)),
            0x47: Sre(self, AddressModeZeroPage(self, 5)),
            0x4F: Sre(self, AddressModeAbsolute(self, 6)),
            0x53: Sre(self, AddressModeIndirectY(self, 8, False)),
            0x57: Sre(self, AddressModeZeroPageXIndexed(self, 6)),
            0x5B: Sre(self, AddressModeAbsoluteYIndexed(self, 7, False)),
            0x5F: Sre(self, AddressModeAbsoluteXIndexed(self, 7, False)),

            0x81: Sta(self, AddressModeIndirectX(self)),
            0x85: Sta(self, AddressModeZeroPage(self)),
            0x8D: Sta(self, AddressModeAbsolute(self)),
            0x91: Sta(self, AddressModeIndirectY(self, 6)),
            0x95: Sta(self, AddressModeZeroPageXIndexed(self, 4)),
            0x99: Sta(self, AddressModeAbsoluteYIndexed(self, 5)),
            0x9D: Sta(self, AddressModeAbsoluteXIndexed(self, 5, False)),

            0x86: Stx(self, AddressModeZeroPage(self)),
            0x96: Stx(self, AddressModeZeroPageYIndexed(self)),
            0x8E: Stx(self, AddressModeAbsolute(self)),

            0x84: Sty(self, AddressModeZeroPage(self)),
            0x94: Sty(self, AddressModeZeroPageXIndexed(self)),
            0x8C: Sty(self, AddressModeAbsolute(self)),

            0xAA: Tax(self, AddressModeImplied()),

            0xA8: Tay(self, AddressModeImplied()),

            0xBA: Tsx(self, AddressModeImplied()),

            0x8A: Txa(self, AddressModeImplied()),

            0x9A: Txs(self, AddressModeImplied()),

            0x98: Tya(self, AddressModeImplied()),
                            }
        '''

        self.cycles_left_to_perform_current_instruction = 0
        self.new_instruction = False
        self.enable_print = False
        self.clk = 0

    def dbg_inst_bytes(self, i_size):
        b = ""
        for i in range(i_size):
            b += "${:X}".format(self.read(self.pc + i))
        return b

    def fetch(self):
        pass

    def decode(self, a_instruction):
        pass

    #def to_hex(self, val, num_fields=2):
    #    return hex(val)[2:].zfill(num_fields)

    def to_str(self):
        #return "A:{} X:{} Y:{} P:{} SP:{}".format(self.to_hex(self.a), self.to_hex(self.x), self.to_hex(self.y), self.to_hex(self.sr.to_byte()), self.to_hex(self.sp))
        return "A:{:02X} X:{:02X} Y:{:02X} P:{:02X} SP:{:02X}".format(self.a, self.x, self.y, self.sr.to_byte(), self.sp)

    def inst_as_bytes(self, pc, instruction_size):
        #s = ""
        b = self.read_many(pc, instruction_size)
        #s = (len(b) * "{:02X} ").format(*b)
        #for i in range(instruction_size):
        #    s += "${:X} ".format(self.read(self.pc + i))
        #return s.ljust(12, " ")
        return ((len(b) * "${:02X} ").format(*b)).ljust(12, " ")

    def clock(self):

        if self.cycles_left_to_perform_current_instruction == 1 and self.exec_bit_ins == True:
            self.exec_bit_ins = False
            self.instructions[0x2c].execute()
            if self.enable_print:
                log_msg = self.log_msg
                log_msg += ascii(self.instructions[0x2c])
                log_msg += self.cpu_msg
                fh = open("log.txt", "a")
                fh.write(log_msg)
                fh.close()
                self.log_msg = ""
                self.cpu_msg = ""

        if self.cycles_left_to_perform_current_instruction == 0:
            self.new_instruction = True
            log_msg = ""
            cpu_state_before = ""

            instruction = self.read(self.pc)
            #if self.pc == 0x8258 or self.pc == 0x825B:
            #    self.enable_print = True
            #else:
            #    self.enable_print = False

            if self.instructions[instruction] == None:
                raise Exception("Unknown instruction :{:02X}".format(instruction))

            if self.enable_print:
                log_msg += "{:04X} ".format(self.pc)
                log_msg += self.inst_as_bytes(self.pc, self.instructions[instruction].size())
                cpu_state_before = self.to_str()
                ppu = self.bus.get_device_by_address(0x2000)
                #cpu_state_before += " CYC:{:<3} SL:{:<3}".format(ppu.cycle, ppu.scanline)
                cpu_state_before += " CPU Cycle:{}".format(self.clock_ticks)
                cpu_state_before += "\r\n"
            self.pc += 1

            if instruction == 0x2c:
                self.cycles_left_to_perform_current_instruction = 4
                self.exec_bit_ins = True
            else:
                """
                if self.clock_ticks == 2142617:
                    print("Emulate Down Btn =======================================================")
                    d = self.bus.get_device_by_address(0x4016)
                    d.btn_down = True
                if self.clock_ticks == 2321296:
                    print("Emulate Down Btn UP =======================================================")
                    d = self.bus.get_device_by_address(0x4016)
                    d.btn_down = False
                if self.clock_ticks == 2678628:
                    print("Emulate Start Btn =======================================================")
                    d = self.bus.get_device_by_address(0x4016)
                    d.btn_start = True
                if self.clock_ticks == 3005564:
                    print("Emulate Start Btn Up =======================================================")
                    d = self.bus.get_device_by_address(0x4016)
                    d.btn_start = False
                """

                self.cycles_left_to_perform_current_instruction = self.instructions[instruction].execute()

            if self.enable_print and self.exec_bit_ins == False:
                log_msg += ascii(self.instructions[instruction])
                log_msg += cpu_state_before
                #print(log_msg)
                fh = open("log.txt", "a")
                fh.write(log_msg)
                fh.close()
            if self.enable_print and self.exec_bit_ins == True:
                self.log_msg = log_msg
                self.cpu_msg = cpu_state_before

            self.clock_ticks += self.cycles_left_to_perform_current_instruction
        else:
            self.new_instruction = False

        self.cycles_left_to_perform_current_instruction -= 1
        self.clk += 1

    def read(self, address, num_bytes=1):
        return self.bus.read(address)

    def read_many(self, address, num_bytes=1):
        return self.bus.read_many(address, num_bytes)

    def write(self, address, data):
        return self.bus.write(address, data)

    def push(self, value):
        self.write(0x0100 | self.sp, value)
        self.sp -= 1
        if self.sp == -1:
            self.sp = 0xFF

    def pop(self):
        self.sp += 1
        return self.read(0x0100 | self.sp)

    def __repr__(self):
        return "CPU A:{}  X:{}  Y:{}  PC:{}  SP:{}  SR:{}  CYC:{}".format(hex(self.a), hex(self.x), hex(self.y), hex(self.pc), hex(self.sp), ascii(self.sr), self.clock_ticks)

    def reset(self):
        self.clock_ticks = 8
        self.clk = 8
        self.pc = 0xFFFC

        ll = self.read(self.pc + 0)
        hh = self.read(self.pc + 1)

        self.pc = (hh << 8) | ll
        #self.pc = 0xc039
        #print("PC:{:04X}".format(self.pc))
        #exit()

        self.a = 0x00
        self.x = 0x0c
        self.y = 0x02
        self.sp = 0xFc    # end of stack

        self.sr = StatusRegister()
        self.sr.from_byte(0x04)

    def nmi(self):
        self.push((self.pc & 0xFF00) >> 8)
        self.push(self.pc & 0xFF)
        self.push(self.sr.to_byte())

        self.pc = 0xFFFA

        ll = self.read(self.pc + 0)
        hh = self.read(self.pc + 1)

        self.pc = (hh << 8) | ll
        self.sr.i = 1
        self.clock_ticks += 7
        self.clk += 7


class RamMemory:

    def __init__(self):
        self.data = [0 for i in range(0x1FFF)]
        self.data[0x0000] = 0xF1
        self.data[0x0002] = 0xC0
        self.data[0x0004] = 0x88
        self.data[0x0005] = 0x1A
        self.data[0x0007] = 0x08
        self.data[0x0009] = 0x6d
        self.data[0x000A] = 0x06
        self.data[0x0011] = 0x27
        self.data[0x0014] = 0x05
        self.data[0x0018] = 0x20
        self.data[0x00FF] = 0xA0
        #self.data[0x00FF] = 0x10

    def read(self, address):
        #if address == 0x7fe:
        #    print("read 07FE data:{:02X}".format(self.data[address & 0x07FF]))
        return self.data[address & 0x07FF]

    def read_many(self, address, num_bytes=1):
        address &= 0x07FF
        return tuple(self.data[address: address+num_bytes])

    def write(self, address, data):
        #if address == 0x7fe:
        #    print("write 07FE data:{:02X}".format(data))
        self.data[address & 0x07FF] = data

    def is_address_valid(self, address):
        return 0 <= address < 0x1FFF


# Program ROM data 0x4020 - 0xFFFF
class Cardrige:

    def __init__(self, file_name):
        f = open(file_name, "rb")
        data = f.read()
        f.close()

        prg_size = data[4]
        chr_size = data[5]

        print("prg:{}   chr:{}".format(prg_size, chr_size))
        flag6 = data[6]
        flag7 = data[7]
        self.mirroring = flag6 & 0x1    # 0-horizontal, 1-veritcal
        print("mirroring:{}".format(self.mirroring))

        trainer = data[6] & 0x4

        mapperId = ((data[7] >> 4) << 4) | (data[6] >> 4)

        prg_start = 16
        chr_start = 16 + 16384 * prg_size
        if trainer == 1:
            prg_start += 512
            chr_start += 512

        self.prg = bytearray(data[prg_start: prg_start + (16384 * prg_size)])
        self.chr = bytearray(data[chr_start: chr_start + (8192 * chr_size)])
        if chr_size == 0:   # we use CHR RAM
            self.chr = [0 for i in range(8192)]

        self.start_addr = 0x4020
        self.end_addr = 0xFFFF

        self.mapper = None
        print("Mapper:{}".format(mapperId))
        if mapperId == 0:
            self.mapper = Mapper000(prg_size)
        elif mapperId == 1:
            self.mapper = Mapper001(prg_size, chr_size)
        elif mapperId == 2:
            self.mapper = Mapper002(prg_size)
        elif mapperId == 71:
            self.mapper = Mapper071(prg_size)
        elif mapperId == 232:
            self.mapper = Mapper232(prg_size)
        else:
            raise NotImplementedError("unknown mapper id:{}".format(mapperId))
        pass

    def read(self, address, num_bytes=1):
        #mapped_addr = self.mapper.map_cpu_address(address)
        #return self.prg[mapped_addr:mapped_addr+num_bytes]
        handled, mapped_addr, data = self.mapper.map_cpu_read(address)

        if address == 0xffe0:
            print("addr:{:04X}  handled:{}  mapped_addr:{}".format(address, handled, mapped_addr))

        if handled:
            return data
        else:
            if mapped_addr > len(self.prg):
                print("out of range addr:{:04X} mapped:{:04X}".format(address, mapped_addr))

            return self.prg[mapped_addr]

        """
        OLD WAY
        if self.mapper.map_cpu_read(address) > len(self.prg):
            print("out of range addr:{:04X} mapped:{:04X}".format(address, self.mapper.map_cpu_read(address)))

        return self.prg[self.mapper.map_cpu_read(address)]
        """

    def read_many(self, address, num_bytes=1):
        handled, mapped_addr, data = self.mapper.map_cpu_read(address)
        """
        OLD WAY
        mapped_addr = self.mapper.map_cpu_read(address)
        """
        return tuple(self.prg[mapped_addr:mapped_addr+num_bytes])

    def write(self, address, data):
        #print("Write addr:{:04X}  data:{:02X}".format(address, data))
        mapped_addr = self.mapper.map_cpu_write(address, data)
        if mapped_addr != -1:
            self.prg[mapped_addr] = data

    def is_address_valid(self, address):
        return self.start_addr <= address <= self.end_addr

    def get_tile_data(self, tile_number, row, half):
        lower_idx = (16 * tile_number) + row
        upper_idx = lower_idx + 8
        if half == 0:   # left
            return self.chr[self.mapper.map_ppu_read(lower_idx)], self.chr[self.mapper.map_ppu_read(upper_idx)]
            #return self.chr[lower_idx], self.chr[upper_idx]
        else:           # right - background
            return self.chr[self.mapper.map_ppu_read(lower_idx | 0x1000)], self.chr[self.mapper.map_ppu_read(upper_idx | 0x1000)]
            #return self.chr[lower_idx | 0x1000], self.chr[upper_idx | 0x1000]


class Mapper000:
    def __init__(self, prg_size):
        self.prg_size = prg_size

    def map_cpu_read(self, addr):
        if self.prg_size > 1:
            return False, addr & 0x7fff, 0x00
        else:
            return False, addr & 0x3fff, 0x00

    def map_cpu_write(self, addr, data):
        if self.prg_size > 1:
            return addr & 0x7fff
        else:
            return addr & 0x3fff

    def map_ppu_read(self, addr):
        return addr


class Mapper001:

    def __init__(self, num_banks, num_chr_banks):
        self.sr = 0b10000
        self.write_counter = 5
        self.ctrl_data = 0x1C
        self.prg_bank_mode = 0
        self.chr_bank_mode = 0
        self.selected_prg_bank = 0
        self.max_num_bank_16k = num_banks - 1
        self.num_bank_16k = 0
        self.num_bank_32k = 0

        self.num_chr_bank_0 = 0
        self.num_chr_bank_1 = 0
        self.num_chr_bank_8k = 0
        self.chr_switch_mode = 0
        self.num_chr_banks = num_chr_banks

        self.ram = [0 for i in range(8192)]

    def internal_write(self, addr, data):

        if addr >= 0x8000 and addr <= 0x9FFF:
            self.chr_switch_mode = ((data & 0b10000) >> 4)

        if addr >= 0xA000 and addr <= 0xBFFF:
            if self.chr_switch_mode:
                # 4k
                self.num_chr_bank_0 = data & 0b11111
            else:
                # 8k
                self.num_chr_bank_8k = ((data & 0b11110) >> 1)
        if addr >= 0xC000 and addr <= 0xDFFF:
            if self.chr_switch_mode:
                # 4k
                self.num_chr_bank_1 = data & 0b11111
        if addr >= 0xe000 and addr < 0xffff:
            # bank select
            if self.ctrl_data & 0b1000:
                # 16k mode
                self.num_bank_16k = data & 0b1111
            else:
                # 32k mode
                self.num_bank_32k = ((data & 0b1110) >> 1)


        """
        if addr >= 0x8000 and addr <= 0x9fff:
            # control
            self.prg_bank_mode = (data & 0b1100) >> 2
            self.chr_bank_mode = (data & 0b10000) >> 4
            if addr >= 0xa000 and addr <= 0xbfff:
                # chr bank0
                pass
            if addr >= 0xc000 and addr <= 0xdfff:
                # chr bank1
                pass
            if addr >= 0xe000 and addr <= 0xffff:
                # bank select
                self.selected_prg_bank = data & 0b1111
        """

    def map_cpu_write(self, addr, data):
        if addr >= 0x8000 and addr <= 0xFFFF:
            if data & 0x80 > 0:
                # reset
                self.sr = 0b10000
                self.ctrl_data |= 0x0c
                self.write_counter = 0
            else:
                # read data
                bit = (data & 0x01) << 4
                self.sr >>= 1
                self.sr |= bit
                self.write_counter += 1
                if self.write_counter == 5:
                    self.internal_write(addr, self.sr)
                    self.sr = 0b10000
                    self.write_counter = 0
        return -1

    def map_cpu_read(self, addr):
        if addr >= 0x6000 and addr <= 0x7FFF:
            return True, 0x0000, self.ram[addr & 0x1FFF]

        if self.ctrl_data & 0b1000:
            # 16kB Mode
            if self.ctrl_data & 0b100:
                # 0xC000 - 0xFFFF fixed
                if addr >= 0xc000 and addr <= 0xffff:
                    return False, (self.max_num_bank_16k * 0x4000) | (addr & 0x3fff), 0x00
                else:
                    return False, (self.num_bank_16k * 0x4000) | (addr & 0x3fff), 0x00
            else:
                if addr >= 0xc000 and addr <= 0xffff:
                    return False, (0 * 0x4000) | (addr & 0x3fff), 0x00
                else:
                    return False, (self.max_num_bank_16k * 0x4000) | (addr & 0x3fff), 0x00
        else:
            # 32kB mode
            return False, (self.num_bank_32k * 0x8000) | (addr & 0x7fff), 0x00

        """
        if addr >= 0x8000 and addr <= 0xbfff:
            if (self.prg_bank_mode == 0 or self.prg_bank_mode == 1):
                return False, ((self.selected_prg_bank & 0b1110) * 0x8000) | (addr & 0x3fff), 0x00
            elif self.prg_bank_mode == 2:
                return False, (0 * 0x4000) | (addr & 0x3fff), 0x00
            elif self.prg_bank_mode == 3:
                return False, (self.selected_prg_bank * 0x4000) | (addr & 0x3fff), 0x00
        elif addr >= 0xc000 and addr <= 0xffff:
            if (self.prg_bank_mode == 0 or self.prg_bank_mode == 1):
                return False, ((self.selected_prg_bank & 0b1110) * 0x8000) | (addr & 0x3fff), 0x00
            if self.prg_bank_mode == 2:
                return False, (self.selected_prg_bank * 0x4000) | (addr & 0x3fff), 0x00
            elif self.prg_bank_mode == 3:
                return False, (0 * 0x4000) | (addr & 0x3fff), 0x00
        """
        print("unhandled address:{:04X}".format(addr))

    def map_ppu_read(self, addr):
        if addr < 0x2000:
            if self.num_chr_banks == 0:
                return addr
            else:
                if self.chr_switch_mode == 1:
                    # 4k banks
                    if addr >= 0x0000 and addr <= 0x0fff:
                        return (self.num_chr_bank_0 * 0x1000) | (addr & 0x0fff)
                    if addr >= 0x1000 and addr <= 0x1fff:
                        return (self.num_chr_bank_1 * 0x1000) | (addr & 0x0fff)
                else:
                    # 8k banks
                    return (self.num_chr_bank_8k * 0x2000) | (addr & 0x1fff)


class Mapper002:
    def __init__(self, num_banks):
        self.selected_bank = 0
        self.num_banks = num_banks

    def map_cpu_read(self, addr):
        if addr >= 0x8000 and addr <= 0xBFFF:
            return False, (self.selected_bank * 0x4000) | (addr & 0x3fff), 0x00
        elif addr >= 0xc000 and addr <= 0xffff:
            return False, ((self.num_banks - 1) * 0x4000) | (addr & 0x3fff), 0x00
        return addr & 0x3fff

    def map_cpu_write(self, addr, data):
        if addr >= 0x8000 and addr <= 0xffff:
            self.selected_bank = data & 0xF
        return -1

    def map_ppu_read(self, addr):
        return addr


class Mapper071:
    def __init__(self, num_banks):
        self.selected_bank = 0
        self.num_banks = num_banks

    def map_cpu_read(self, addr):
        if addr >= 0x8000 and addr <= 0xBFFF:
            return False, (self.selected_bank * 0x4000) | (addr & 0x3fff), 0x00
        elif addr >= 0xc000 and addr <= 0xffff:
            return False, ((self.num_banks -1) * 0x4000) | (addr & 0x3fff), 0x00
        return False, addr & 0x3fff, 0x00

    def map_cpu_write(self, addr, data):
        if addr >= 0xC000 and addr <= 0xffff:
            self.selected_bank = (data & 0xF) & (self.num_banks - 1)

            if self.selected_bank >= self.num_banks:
                raise Exception("Selected bank:{}  num banks:{}  addr:{:04X}  data:{:02X}".format(self.selected_bank, self.num_banks, addr, data))
        return -1

    def map_ppu_read(self, addr):
        return addr


class Mapper232:
    def __init__(self, num_banks):
        self.selected_outer_bank = 0
        self.selected_inner_bank = 0
        self.num_banks = num_banks

    def map_cpu_read(self, addr):
        if addr >= 0x8000 and addr <= 0xBFFF:
            return False, (self.selected_outer_bank * 0x10000) | (self.selected_inner_bank * 0x4000) | (addr & 0x3fff), 0x00
        elif addr >= 0xc000 and addr <= 0xffff:
            return False, (self.selected_outer_bank * 0x10000) | (3 * 0x4000) | (addr & 0x3fff), 0x00
            #return ((self.num_banks -1) * 0x4000) | (addr & 0x3fff)
        return False, addr & 0x3fff, 0x00

    def map_cpu_write(self, addr, data):
        if addr >= 0x8000 and addr <= 0xBFFF:
            self.selected_outer_bank = ((data & 0x18) >> 3) & 0x3
        if addr >= 0xC000 and addr <= 0xffff:
            self.selected_inner_bank = (data & 0xF) & 0x3

            #if self.selected_bank >= self.num_banks:
            #    raise Exception("Selected bank:{}  num banks:{}  addr:{:04X}  data:{:02X}".format(self.selected_bank, self.num_banks, addr, data))
        return -1

    def map_ppu_read(self, addr):
        return addr


class Apu:
    def __init__(self):
        self.start_addr = 0x4000
        self.end_addr = 0x4017
        self.data = [0 for i in range(self.end_addr - self.start_addr + 1)]
        self.read_button = False
        self.cnt = 0
        self.f = False
        self.btn_down = False
        self.btn_up = False
        self.btn_start = False
        self.btn_select = False
        self.btn_left = False
        self.btn_right = False
        self.btn_a = False
        self.btn_b = False

    def read(self, address):
        if address == 0x4016:
            #print("Controller read")
            d = 0x40
            if self.read_button:
                if self.cnt == 7 and self.btn_right:
                    d = 0x41
                    #self.btn_right = False
                elif self.cnt == 6 and self.btn_left:
                    d = 0x41
                    #self.btn_left = False
                elif self.cnt == 5 and self.btn_down:
                    d = 0x41
                    #self.btn_down = False
                elif self.cnt == 4 and self.btn_up:
                    d = 0x43
                    #self.btn_up = False
                elif self.cnt == 3 and self.btn_start:
                    d = 0x41
                    #self.btn_start = False
                elif self.cnt == 2 and self.btn_select:
                    d = 0x41
                    #self.btn_select = False
                elif self.cnt == 1 and self.btn_b:
                    d = 0x41
                    #self.btn_b = False
                elif self.cnt == 0 and self.btn_a:
                    d = 0x41
                    #self.btn_a = False
                elif self.cnt > 7:
                    d = 0x40

                self.cnt += 1
            return d
        elif address == 0x4017:
            return 0x40

        return self.data[address - self.start_addr]

    def get_pressed_button(self):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pressed_up()
                elif event.key == pygame.K_DOWN:
                    self.pressed_down()
                elif event.key == pygame.K_LEFT:
                    self.pressed_left()
                elif event.key == pygame.K_RIGHT:
                    self.pressed_right()
                elif event.key == pygame.K_RETURN:
                    self.pressed_start()
                elif event.key == pygame.K_1:
                    self.select_pressed()
                elif event.key == pygame.K_a:
                    self.btn_a = True
                elif event.key == pygame.K_s:
                    self.btn_b = True

        for event in pygame.event.get(pygame.KEYUP):
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    #self.pressed_up()
                    self.btn_up = False
                elif event.key == pygame.K_DOWN:
                    #self.pressed_down()
                    self.btn_down = False
                elif event.key == pygame.K_LEFT:
                    #self.pressed_left()
                    self.btn_left = False
                elif event.key == pygame.K_RIGHT:
                    #self.pressed_right()
                    self.btn_right = False
                elif event.key == pygame.K_RETURN:
                    self.btn_start = False
                elif event.key == pygame.K_1:
                    self.btn_select = False
                elif event.key == pygame.K_a:
                    self.btn_a = False
                elif event.key == pygame.K_s:
                    self.btn_b = False

    def write(self, address, data):
        if address == 0x4016:
            self.cnt = 0
            if data & 0x1 == 0:
                self.read_button = True
                self.get_pressed_button()
            else:
                self.read_button = False

        self.data[address - self.start_addr] = data

    def is_address_valid(self, address):
        return self.start_addr <= address <= self.end_addr and address != 0x4014

    def pressed_down(self):
        self.btn_down = True

    def pressed_up(self):
        self.btn_up = True

    def pressed_start(self):
        self.btn_start = True

    def select_pressed(self):
        self.btn_select = True

    def pressed_right(self):
        self.btn_right = True

    def pressed_left(self):
        self.btn_left = True


class StatusRegister:

    def __init__(self):
        self.n = 0  # negative
        self.v = 0  # Overflow
        self.unused = 0 #  -    ....ignored
        self.b = 0  # break
        self.d = 0  # decimal
        self.i = 0  # interrupt
        self.z = 0  # zero
        self.c = 0  # carry

    def to_byte(self):
        return (self.n << 7) + (self.v << 6) + (self.unused << 5) + (self.b << 4) + (self.d << 3) + (self.i << 2) + (self.z << 1) + self.c

    def from_byte(self, data):
        self.c = data & 0x1
        self.z = (data >> 1) & 0x1
        self.i = (data >> 2) & 0x1
        self.d = (data >> 3) & 0x1
        self.b = (data >> 4) & 0x1
        self.unused = (data >> 5) & 0x1
        self.v = (data >> 6) & 0x1
        self.n = (data >> 7) & 0x1

    def __repr__(self):
        return "N:{}  V:{}  D:{}  I:{}  Z:{}  C:{}".format(self.n, self.v, self.d, self.i, self.z, self.c)


# ------------------------------------------------------------------------------
#                             INSTRUCTIONS
# ------------------------------------------------------------------------------


class Adc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        result = self.cpu.a + operand + self.cpu.sr.c

        self.cpu.sr.n = (result & 0x80) >> 7

        if result & 0x00FF == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        if result > 255:
            self.cpu.sr.c = 1
        else:
            self.cpu.sr.c = 0

        self.cpu.sr.v = 0
        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (result & 0x80) > 0:
            self.cpu.sr.v = 1

        if (self.cpu.a & 0x80) > 0 and (operand & 0x80) > 0 and (result & 0x80) == 0:
            self.cpu.sr.v = 1

        self.cpu.a = result & 0xFF

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("ADC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("ADC " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class And:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.data = 0x00

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)
        self.data = operand

        self.cpu.a = self.cpu.a & operand

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("AND " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("AND " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Asl:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        if address == 0xA0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)
        tmp = (operand << 1)

        self.cpu.sr.n = (tmp & 0x80) >> 7
        if tmp > 255:
            self.cpu.sr.c = 1
        else:
            self.cpu.sr.c = 0

        tmp = tmp & 0xff

        if address == 0xA0000:
            self.cpu.a = tmp
        else:
            self.cpu.write(address, tmp)

        if tmp == 0x00:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("ASL " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("ASL " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


# branch on carry clear
class Bcc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()

        if self.cpu.sr.c == 0:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BCC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BCC " + ascii(self.addressMode) + "${:X}".format(self.cpu.read(addr))).ljust(LOG_WIDTH, " ")


# branch on carry set
class Bcs:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()

        if self.cpu.sr.c == 1:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BCS " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BCS " + ascii(self.addressMode) + "${:X}".format(self.cpu.read(addr))).ljust(LOG_WIDTH, " ")


class Beq:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()

        if self.cpu.sr.z == 1:
            self.cpu.pc = address
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BEQ " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")


class Bit:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.cpu.sr.n = (operand >> 7) & 0x1
        self.cpu.sr.v = (operand >> 6) & 0x1
        if operand & self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BIT " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BIT " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Bmi:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        if self.cpu.sr.n == 1:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BMI " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BMI " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Bne:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()

        if self.cpu.sr.z == 0:
            self.cpu.pc = address
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BNE " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")


class Bpl:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()

        if self.cpu.sr.n == 0:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BPL " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BPL " + ascii(self.addressMode) + "${:X}".format(self.cpu.read(addr))).ljust(LOG_WIDTH, " ")


class Brk:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):

        self.cpu.sr.i = 1

        hh = (self.cpu.pc & 0xFF00) >> 8
        ll = self.cpu.pc & 0xFF

        self.cpu.write(self.cpu.sp, hh)
        self.cpu.sp -=1
        self.cpu.write(self.cpu.sp, ll)
        self.cpu.sp -= 1
        self.cpu.write(self.cpu.sp, self.cpu.sr.to_byte())
        self.cpu.sp -= 1

        ll = self.cpu.read(0xFFFE)
        hh = self.cpu.read(0xFFFF)

        self.cpu.pc = (hh << 8) | ll

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size


class Bvc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        if self.cpu.sr.v == 0:
            self.cpu.pc = address
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BVC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BVC " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Bvs:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        if self.cpu.sr.v == 1:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("BVS " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("BVS " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Clc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.c = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("CLC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("CLC " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Cld:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.d = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "CLD".ljust(LOG_WIDTH, ' ')


class Cli:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def size(self):
        return self.addressMode.size

    def execute(self):
        self.cpu.sr.i = 0
        return self.addressMode.cycles


class Clv:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.v = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "CLV".ljust(LOG_WIDTH, " ")


class Cmp:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        result = self.cpu.a - operand

        if result & 0x80 > 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        if self.cpu.a == operand:
            self.cpu.sr.z = 1
            self.cpu.sr.c = 1
        elif self.cpu.a < operand:
            self.cpu.sr.z = 0
            self.cpu.sr.c = 0
        elif self.cpu.a > operand:
            self.cpu.sr.z = 0
            self.cpu.sr.c = 1

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("CMP " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("CMP " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Cpx:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        result = self.cpu.x - operand

        if result & 0x80 > 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        if self.cpu.x == operand:
            self.cpu.sr.z = 1
            self.cpu.sr.c = 1
        elif self.cpu.x < operand:
            self.cpu.sr.z = 0
            self.cpu.sr.c = 0
        elif self.cpu.x > operand:
            self.cpu.sr.z = 0
            self.cpu.sr.c = 1

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("CPX " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("CPX " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Cpy:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        result = self.cpu.y - operand

        if result & 0x80 > 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        if self.cpu.y == operand:
            self.cpu.sr.z = 1
            self.cpu.sr.c = 1
        elif self.cpu.y < operand:
            self.cpu.sr.z = 0
            self.cpu.sr.c = 0
        elif self.cpu.y > operand:
            self.cpu.sr.z = 0
            self.cpu.sr.c = 1

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("CPY " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("CPY " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Dcp:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        if operand == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (operand & 0x80) >> 7
        b = operand
        operand -= 1
        operand &= 0xff

        r = self.cpu.a - operand
        if r & 0x80 > 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        #if b & 0x80 == 0 and operand & 0x80 > 0:
        #    self.cpu.sr.n = 1
        #else:
        #    self.cpu.sr.n = 0

        self.cpu.write(addr, operand)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "DCP {}".format(ascii(self.addressMode))


class Dec:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        operand -= 1

        if operand == -1:
            operand = 0xff

        if operand == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (operand & 0x80) >> 7

        self.cpu.write(address, operand)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("DEC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("DEC " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Dex:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.x -= 1
        self.cpu.x = self.cpu.x & 0xff
        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "DEX".ljust(LOG_WIDTH, " ")


class Dey:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.y -= 1
        self.cpu.y = self.cpu.y & 0xff
        if self.cpu.y == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.y & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "DEY".ljust(LOG_WIDTH, " ")


class Eor:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.cpu.a = operand ^ self.cpu.a

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("EOR " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("EOR " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Inc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        operand += 1
        operand = operand & 0xff

        if operand == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (operand & 0x80) >> 7

        self.cpu.write(address, operand)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("INC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("INC " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Inx:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.x += 1
        self.cpu.x = self.cpu.x & 0xff

        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("INX " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("INX " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Iny:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.y += 1
        self.cpu.y = self.cpu.y & 0xff

        if self.cpu.y == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.y & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "INY".ljust(LOG_WIDTH, " ")


class Isb:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        o = hex_to_signed_int(self.cpu.read(address))
        o += 1
        old_c = self.cpu.sr.c

        if operand == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        operand += 1
        operand &= 0xff



        self.cpu.write(address, operand)

        tmp = operand - self.cpu.a

        if tmp & 0x80 > 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        self.cpu.sr.v = 0

        #self.cpu.sr.c = 1
        #if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (signed_int_to_hex(self.cpu.a) < signed_int_to_hex(operand)):
        #    self.cpu.sr.c = 0

        #if (self.cpu.a & 0x80) > 0 and (operand & 0x80) > 0 and (signed_int_to_hex(self.cpu.a) > signed_int_to_hex(operand)):
        #    self.cpu.sr.c = 0

        #if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (signed_int_to_hex(self.cpu.a) < signed_int_to_hex((operand))) and operand - self.cpu.a > 0x7F:
        #    self.cpu.sr.v = 1

        #if (self.cpu.a & 0x80) > 0 and (operand & 0x80) == 0 and tmp & 0x80 == 0:
        #    self.cpu.sr.v = 1

        #if tmp < -128:
        #    self.cpu.sr.v = 1

        signed_val = hex_to_signed_int(self.cpu.a) - hex_to_signed_int(o) - (1 - old_c)
        if signed_val < 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        if signed_val < -128 or signed_val > 127:
            self.cpu.sr.v = 1

        self.cpu.a = signed_int_to_hex(signed_val)

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "ISB {}".format(ascii(self.addressMode))


class Jmp:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.pc = self.addressMode.get_address()
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("JMP " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")


# Jump to new location, save return address
class Jsr:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()

        self.cpu.push(((self.cpu.pc-1) & 0xFF00) >> 8)  # -1 because address mode will move pc to the next instruction
        self.cpu.push((self.cpu.pc-1) & 0xFF)

        self.cpu.pc = addr
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("JSR " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("JSR " + ascii(self.addressMode) + "${:X}".format(self.cpu.read(addr))).ljust(LOG_WIDTH, " ")


class Lax:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        self.cpu.a = operand
        self.cpu.x = operand

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "LAX {}".format(ascii(self.addressMode))


class Lda:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        self.cpu.a = self.cpu.read(address)

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("LDA " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")


class Ldx:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.data = 0x00

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)
        self.data = operand
        self.cpu.x = operand

        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("LDX " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("LDX " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Ldy:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        self.cpu.y = operand

        if self.cpu.y == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.y & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("LDY " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("LDY " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Lsr:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = 0
        if address == 0xA0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)

        self.cpu.sr.c = operand & 0x0001
        tmp = operand >> 1

        if address == 0xA0000:
            self.cpu.a = tmp
        else:
            self.cpu.write(address, tmp)

        self.cpu.sr.n = 0

        if tmp == 0x00:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("LSR " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("LSR " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Nop:

    def __init__(self, address_mode):
        self.addressMode = address_mode

    def execute(self):
        self.addressMode.get_address()
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "NOP".ljust(LOG_WIDTH, " ")


class Ora:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.cpu.a = self.cpu.a | operand

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7

        if self.cpu.a == 0x00:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("ORA " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("ORA " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Pha:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.push(self.cpu.a)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("PHA " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("PHA " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Php:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        # PHP sets 4 and 5 bit of status register to 1
        val = self.cpu.sr.to_byte()# | (1 << 5) | (1 << 4)
        self.cpu.push(val)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "PHP".ljust(LOG_WIDTH, " ")


class Pla:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.a = self.cpu.pop()

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7

        if self.cpu.a == 0x00:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("PLA " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("PLA " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Plp:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        val = self.cpu.pop()
        #if val & 0x10 == 0x10:
        #    val = val & 0xef
        #else:
        #    val = val | (1 << 5)

        self.cpu.sr.from_byte(val)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "PLP".ljust(LOG_WIDTH, " ")


class Rla:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        old_c = self.cpu.sr.c
        self.cpu.sr.c = (operand & 0x80) >> 7
        operand = ((operand << 1) + old_c) & 0xff

        self.cpu.write(address, operand)
        self.cpu.a = self.cpu.a & operand

        if self.cpu.a == 0:
            self.cpu.sr.z = 1

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "RLA {}".format(ascii(self.addressMode))


class Rol:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        if address == 0xa0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)

        old_c = self.cpu.sr.c
        self.cpu.sr.c = (operand & 0x80) >> 7  # FIXED thanks to logs
        operand = ((operand << 1) + old_c) & 0xff

        if address == 0xa0000:
            self.cpu.a = operand
        else:
            self.cpu.write(address, operand)

        if operand == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (operand & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("ROL " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("ROL " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Ror:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        if address == 0xa0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)

        old_c = self.cpu.sr.c
        self.cpu.sr.c = operand & 0x01
        operand = (operand >> 1) | (old_c << 7)

        if address == 0xa0000:
            self.cpu.a = operand
        else:
            self.cpu.write(address, operand)

        if operand == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (operand & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("ROR " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("ROR " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Rra:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        old_c = self.cpu.sr.c
        #self.cpu.sr.c = operand & 0x0001
        #tmp = operand >> 1
        old_c = self.cpu.sr.c

        #self.cpu.sr.c = operand & 0x01
        tmp = (operand >> 1) | (old_c << 7)

        if old_c == 1 and operand & 0x01 == 1:
            old_c = 0

        self.cpu.write(address, tmp)

        if (operand & 0x80 == 0 and tmp & 0x80 > 0) or (operand & 0x80 > 0 and tmp & 0x80 == 0):
            self.cpu.sr.c = 1
        #self.cpu.sr.n = 0

        #if tmp == 0x00:
        #    self.cpu.sr.z = 1
        #else:
        #    self.cpu.sr.z = 0

        result = hex_to_signed_int(self.cpu.a) + hex_to_signed_int(tmp) + (1 - old_c)

        if result < 0:
            self.cpu.sr.n = 1
        else:
            self.cpu.sr.n = 0

        if result & 0x00FF == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        #if result > 255:
        #    self.cpu.sr.c = 1
        #else:
        #    self.cpu.sr.c = 0

        self.cpu.sr.v = 0
        if result < -128 or result > 127:
            self.cpu.sr.v = 1
        #self.cpu.sr.v = 0
        #if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (result & 0x80) > 0:
        #    self.cpu.sr.v = 1

        #if (self.cpu.a & 0x80) > 0 and (operand & 0x80) > 0 and (result & 0x80) == 0:
        #    self.cpu.sr.v = 1

        self.cpu.a = result & 0xFF

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "RRA {}".format(ascii(self.addressMode))


class Rti:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        val = self.cpu.pop()
        if val & 0x10 == 0x10:
            val = val & 0xef
        else:
            val = val | (1 << 5)

        if val & 0x20 == 0x20:
            val = val & 0xdf
        else:
            val = val | (1 << 6)

        self.cpu.sr.from_byte(val)
        ll = self.cpu.pop()
        hh = self.cpu.pop()
        self.cpu.pc = (hh << 8) | ll
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "RTI".ljust(LOG_WIDTH, " ")


class Rts:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        ll = self.cpu.pop()
        hh = self.cpu.pop()
        self.cpu.pc = (hh << 8) | ll
        self.cpu.pc += 1

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "RTS ".ljust(LOG_WIDTH, " ")


class Sax:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        tmp = self.cpu.a & self.cpu.x
        x = tmp
        tmp = tmp - operand

        self.cpu.write(addr, x)
        #self.cpu.x = tmp

        #self.cpu.sr.c = 1
        #if (x & 0x80) == 0 and (operand & 0x80) == 0 and (x < operand):
        #    self.cpu.sr.c = 0

        #if (x & 0x80) > 0 and (operand & 0x80) > 0 and (x > operand):
        #    self.cpu.sr.c = 0

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "SAX {}".format(ascii(self.addressMode))


class Sbc:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        # A - M - (1 - C)
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        #tmp = self.cpu.a - operand - (1 - self.cpu.sr.c)
        tmp = signed_int_to_hex(self.cpu.a - operand - (1 - self.cpu.sr.c))
        res = signed_int_to_hex(self.cpu.a - operand - (1 - self.cpu.sr.c))

        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) > 0:
            tmp -= 1

        """
        OLD
        if self.cpu.a == operand:
            self.cpu.sr.z = 1
            tmp = 0
        else:
            self.cpu.sr.z = 0
        """
        if res == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (tmp & 0x80) >> 7

        self.cpu.sr.v = 0

        sig_a = hex_to_signed_int(self.cpu.a)
        sig_o = hex_to_signed_int(operand)


        if (self.cpu.a > operand) or (self.cpu.a == operand and self.cpu.sr.c == 1):
            self.cpu.sr.c = 1
        elif self.cpu.a < operand:
            self.cpu.sr.c = 0
        elif self.cpu.a == operand and self.cpu.sr.c == 0:
            self.cpu.sr.c = 0

        """
        self.cpu.sr.c = 1
        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (self.cpu.a < operand):   # old (self.cpu.a < operand)
            self.cpu.sr.c = 0

        if (self.cpu.a & 0x80) > 0 and (operand & 0x80) > 0 and (self.cpu.a > operand):     # old (self.cpu.a > operand)
            self.cpu.sr.c = 0
        """

        u = sig_a - sig_o
        if u > 127 or u < -128:
            self.cpu.sr.v = 1
        """
        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (self.cpu.a < operand) and operand - self.cpu.a > 0x7F:
            self.cpu.sr.v = 1

        if (self.cpu.a & 0x80) > 0 and (operand & 0x80) == 0 and tmp & 0x80 == 0:
            self.cpu.sr.v = 1

        if tmp < -128:
            self.cpu.sr.v = 1
        """
        if tmp < 0:
            tmp = hex(tmp & 0xff)
            tmp = int(tmp, 16)

        if tmp == -128:
            tmp = 0x7f

        if self.cpu.a == 0x80 and operand == 0x00:
            tmp = 0x7f

        self.cpu.a = res

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("SBC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("SBC " + ascii(self.addressMode) + "${:X}".format(operand)).ljust(LOG_WIDTH, " ")


class Sec:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.c = 1

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("SEC " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("SEC " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Sed:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.d = 1
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "SED".ljust(LOG_WIDTH, " ")


class Sei:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.i = 1
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "SEI".ljust(LOG_WIDTH, " ")


class Slo:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        old_c = self.cpu.sr.c
        self.cpu.sr.c = (operand & 0x80) >> 7
        operand = ((operand << 1)) & 0xff

        self.cpu.write(address, operand)

        self.cpu.a = self.cpu.a | operand

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7

        if self.cpu.a == 0x00:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "SLO {}".format(ascii(self.addressMode))


class Sre:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        old_c = self.cpu.sr.c
        self.cpu.sr.c = operand & 0x01
        operand = (operand >> 1) #| (old_c << 7)

        self.cpu.write(address, operand)

        self.cpu.a = operand ^ self.cpu.a

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "SRE {}".format(ascii(self.addressMode))


class Sta:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        address = self.addressMode.get_address()
        self.cpu.write(address, self.cpu.a)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("STA " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")


class Stx:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        abs_addr = self.addressMode.get_address()

        self.cpu.write(abs_addr, self.cpu.x)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("STX " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("STX " + ascii(self.addressMode) + "${:X}".format(self.cpu.read(abs_addr))).ljust(LOG_WIDTH, " ")


class Sty:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        addr = self.addressMode.get_address()
        #self.addressMode.fetch()
        #abs_addr = self.addressMode.abs_address()

        self.cpu.write(addr, self.cpu.y)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("STY " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("STY " + ascii(self.addressMode) + "${:X}".format(self.cpu.read(addr))).ljust(LOG_WIDTH, " ")


class Tax:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.x = self.cpu.a

        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("TAX " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("TAX " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Tay:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.y = self.cpu.a

        if self.cpu.y == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.y & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return ("TAY " + ascii(self.addressMode)).ljust(LOG_WIDTH, " ")
        #self.str = ("TAY " + ascii(self.addressMode)).upper().ljust(LOG_WIDTH, " ")


class Tsx:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.x = self.cpu.sp

        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "TSX {}".format(ascii(self.addressMode))


class Txa:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.a = self.cpu.x

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "TXA".ljust(LOG_WIDTH, ' ')


class Txs:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        #self.cpu.sr.from_byte(self.cpu.x)
        self.cpu.sp = self.cpu.x
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "TXS".ljust(LOG_WIDTH, ' ')


class Tya:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.a = self.cpu.y

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "TYA".ljust(LOG_WIDTH, ' ')

# ------------------------------------------------------------------------------
#                            ADDRESSING MODES
# ------------------------------------------------------------------------------


class AddressModeAccumulator:

    def __init__(self, cpu):
        self.cpu = cpu
        self.cycles = 2
        self.size = 1

    def fetch(self):
        return self.cpu.a

    def get_address(self):
        return 0xA0000

    def write(self, val):
        self.cpu.a = val

    def __repr__(self):
        return "A"


class AddressModeAbsolute:

    def __init__(self, cpu, cycles=4):
        self.cpu = cpu
        self.abs_address = 0x0000
        self.cycles = cycles
        self.ll = 0x00
        self.hh = 0x00
        self.size = 3

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.ll, self.hh = self.cpu.read_many(self.cpu.pc, 2)
        self.cpu.pc += 2
        self.abs_address = (self.hh << 8) | self.ll
        return self.abs_address

    def __repr__(self):
        return "${:04X}".format(self.abs_address)


class AddressModeAbsoluteXIndexed:

    def __init__(self, cpu, cycles, extra_cycle=True):
        self.cpu = cpu
        self.abs_address = 0x0000
        self.ll = 0
        self.hh = 0
        self.cycles = cycles
        self.cycles_o = cycles
        self.extra_cycle = extra_cycle
        self.size = 3

    def abs_address(self):
        return self.abs_address

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.cycles = self.cycles_o
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.hh = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1

        addr = ((self.hh << 8) | self.ll) + self.cpu.x
        addr = addr & 0xffff
        #self.cpu.operand = self.cpu.read(addr)

        if (addr & 0xFF00) != (self.hh << 8) and self.extra_cycle:
            self.cycles += 1
        return addr

    def __repr__(self):
        base_addr = (self.hh << 8) | self.ll
        abs_addr = base_addr + self.cpu.x
        return "${:04X},X @ ${:04X}".format(base_addr, abs_addr)


class AddressModeAbsoluteYIndexed:

    def __init__(self, cpu, cycles, extra_cycles=True):
        self.cpu = cpu
        self.ll = 0
        self.hh = 0
        self.cycles = cycles
        self.cycles_o = cycles
        self.extra_cycles = extra_cycles
        self.size = 3

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.cycles = self.cycles_o
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.hh = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1

        addr = ((self.hh << 8) | self.ll) + self.cpu.y
        addr = addr & 0xffff
        self.cpu.operand = self.cpu.read(addr)

        if (addr & 0xFF00) != (self.hh << 8) and self.extra_cycles:
            self.cycles += 1
        return addr

    #def get_bytes(self):
    #    return "${} ${} ".format(to_str_hex(self.ll), to_str_hex(self.hh))

    def __repr__(self):
        base_addr = ((self.hh << 8) | self.ll)
        addr = base_addr + self.cpu.y
        return "${:04X},Y @ ${:04X}".format(base_addr, addr)


class AddressModeImmediate:

    def __init__(self, cpu):
        self.cpu = cpu
        self.addr = 0
        self.cycles = 2
        self.size = 2

    def fetch(self):
        # data is stored just after instruction
        #self.pc += 1
        #self.operand = self.cpu.read(self.cpu.pc)
        #self.cpu.pc += 1
        #return self.operand
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.addr = self.cpu.pc
        self.cpu.pc += 1
        return self.addr

    def get_bytes(self):
        return "${}".format(to_str_hex(self.cpu.read(self.addr))).ljust(8, " ")

    def __repr__(self):
        return "#${:02X}".format(self.cpu.read(self.addr))


class AddressModeImplied:

    def __init__(self, cycles=2):
        self.cycles = cycles
        self.size = 1

    def fetch(self):
        pass

    def get_address(self):
        pass

    def __repr__(self):
        return ""


class AddressModeIndirect:

    def __init__(self, cpu, cycles=5):
        self.cpu = cpu
        self.cycles = cycles
        self.ptr = 0x0000
        self.ll = 0x00
        self.hh = 0x00
        self.size = 3
        self.addr = 0x0000

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.hh = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1

        self.ptr = (self.hh << 8) | self.ll

        if self.ll == 0xFF:  # emulate bug
            self.addr = (self.cpu.read(self.ptr & 0xFF00) << 8) | self.cpu.read(self.ptr + 0);
        else:  # Behave normally
            self.addr = (self.cpu.read(self.ptr+1) << 8) | self.cpu.read(self.ptr)

        return self.addr

    #def get_bytes(self):
    #    return "${} ${} ".format(to_str_hex(self.ll), to_str_hex(self.hh))

    def __repr__(self):
        return "(${:04X}) @ ${:04X}".format(self.ptr, self.addr)


class AddressModeIndirectX:

    def __init__(self, cpu, cycles=6):
        self.cpu = cpu
        self.addr = 0x00
        self.ll = 0x00
        self.cycles = cycles
        self.size = 2

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        ll = self.cpu.read(self.cpu.pc)
        self.ll = ll
        self.cpu.pc += 1
        self.addr = (self.cpu.read((ll + self.cpu.x + 1) & 0xff) << 8) | self.cpu.read((ll + self.cpu.x) & 0xff)
        return self.addr

    def cycles(self):
        return 6

    def __repr__(self):
        return "({}, X)".format(hex(self.ll))


class AddressModeIndirectY:

    def __init__(self, cpu, cycles=5, extra_cycles=True):
        self.cpu = cpu
        self.addr = 0x0000
        self.ll = 0x00
        self.cycles = cycles
        self.cycles_o = cycles
        self.extra_cycles = extra_cycles
        self.size = 2

    def get_address(self):
        self.cycles = self.cycles_o
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1

        ll = self.cpu.read(self.ll)
        hh = self.cpu.read((self.ll + 1) & 0xff)

        self.addr = (hh << 8) | ll
        self.addr += self.cpu.y
        self.addr = self.addr & 0xffff

        if self.addr & 0xff00 != (hh << 8) and self.extra_cycles:
            self.cycles += 1

        return self.addr

    #def get_bytes(self):
    #    return "${} ".format(to_str_hex(self.ll))

    def __repr__(self):
        return "(${:04X}),Y @ ${:04X}".format(self.ll, self.addr)


class AddressModeRelative:

    def __init__(self, cpu):
        self.cpu = cpu
        self.addr = 0x0000
        self.cycles = 2
        self.data = 0x00
        self.size = 2

    #def fetch(self):
    #    self.addr = self.cpu.read(self.cpu.pc)
    #    if self.rel_addr & 0x80:
            # negative number, which we must extend to 16bit value
    #        self.rel_addr |= 0xff

    #    # TODO: something more?

    #    return 1

    def get_address(self):
        self.cycles = 2
        self.data = self.cpu.read(self.cpu.pc)
        self.addr = self.data
        if self.addr & 0x80:
            # negative number, which we must extend to 16bit value
            self.addr = ~ self.addr & 0xff
            self.addr = self.cpu.pc - self.addr

            if self.addr & 0xff00 != self.cpu.pc & 0xff00:
                self.cycles += 2
            else:
                self.cycles += 1

            self.cpu.pc += 1
            return self.addr
        else:
            self.cpu.pc += 1
            self.addr += self.cpu.pc

            if self.addr & 0xff00 != self.cpu.pc & 0xff00:
                self.cycles += 2
            else:
                self.cycles += 1

            return self.addr

    def get_bytes(self):
        return "${} ".format(to_str_hex(self.data))

    def __repr__(self):
        return "${:04X}".format(self.addr)
        #return "${}".format(to_str_hex(self.addr, 4)) #NESDEV


class AddressModeZeroPage:

    def __init__(self, cpu, cycles=3):
        self.cpu = cpu
        self.address = 0x0000
        self.cycles = cycles
        self.size = 2
        #self.operand = 0x00

    def fetch(self):
    #    self.abs_address = self.cpu.read(self.cpu.pc)
    #    self.cpu.pc += 1
    #    self.abs_address &= 0x00FF
    #    self.operand = self.cpu.read(self.abs_address)
    #    return self.operand
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.address = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.address &= 0x00FF
        return self.address

    def write(self, value):
        address = self.get_address()
        self.cpu.write(address, value)

    #def get_bytes(self):
    #    return "${} ".format(to_str_hex(self.address))

    def __repr__(self):
        return "${:04X}".format(self.address)
        #return "${} = ".format(to_str_hex(self.address, 2))
        #return "${}".format(to_str_hex(self.address, 4))


class AddressModeZeroPageXIndexed:

    def __init__(self, cpu, cycles=4):
        self.cpu = cpu
        self.abs_address = 0x0000
        self.ll = 0
        self.cycles = cycles
        self.size = 2
        self.addr = 0x0000

    def fetch(self):
        return self.cpu.read(self.get_address())

    def abs_address(self):
        return self.abs_address

    def get_address(self):
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.addr = self.ll + self.cpu.x
        self.addr &= 0x00FF
        return self.addr

    def __repr__(self):
        return "${:04X},X @ ${:02X}".format(self.ll, self.addr)


class AddressModeZeroPageYIndexed:

    def __init__(self, cpu):
        self.cpu = cpu
        self.ll = 0
        self.cycles = 4
        self.size = 2
        self.addr = 0x0000

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.addr = self.ll + self.cpu.y
        self.addr &= 0x00FF
        return self.addr

    def __repr__(self):
        return "{:04X},Y @ ${:02X}".format(self.ll, self.addr)


def hex_to_signed_int(v):
    if v & 0x80:
        # negative number
        return -((~ v + 1) & 0xff)
    return v


def signed_int_to_hex(v):
    if v < 0:
        return (v & (2**32-1)) & 0xff
    else:
        return v
    #if v & 0x80:
    #    v *= -1
    #    return (~ v + 1) & 0xff
    #else:
    #    return v


def to_str_hex(val, num_fields=2):
        return "{:02X}".format(val)
        #hex(val)[2:].zfill(num_fields)


if __name__ == "__main__":
    print("cpu impl")
    print(hex_to_signed_int(0xec))
    print(hex_to_signed_int(0x14))

    print(hex(signed_int_to_hex(-20)))
    print(hex(signed_int_to_hex(20)))
