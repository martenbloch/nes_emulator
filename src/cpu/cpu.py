
class Bus:

    def __init__(self):
        self.__devices = []

    def write(self, address, data):
        d = self.get_device_by_address(address)
        if d:
            d.write(address, data)
        else:
            raise Exception("device not found for address: {}".format(hex(address)))

    def read(self, address):
        d = self.get_device_by_address(address)
        if d:
            return d.read(address)
        else:
            raise Exception("device not found for address: {}".format(hex(address)))

    def get_device_by_address(self, address):
        for d in self.__devices:
            if d.is_address_valid(address):
                return d
        return None

    def connect(self, device):
        self.__devices.append(device)


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

        self.cycles_left_to_perform_current_instruction = 0
        self.new_instruction = False

    def dbg_inst_bytes(self, i_size):
        b = ""
        for i in range(i_size):
            b += "$" + to_str_hex(self.read(self.pc + i))
        return b

    def fetch(self):
        pass

    def decode(self, a_instruction):
        pass

    def to_hex(self, val, num_fields=2):
        return hex(val)[2:].zfill(num_fields)

    def to_str(self):
        return "A:{} X:{} Y:{} P:{} SP:{}".format(self.to_hex(self.a), self.to_hex(self.x), self.to_hex(self.y), self.to_hex(self.sr.to_byte()), self.to_hex(self.sp))

    def inst_as_bytes(self, instruction_size):
        s = ""
        for i in range(instruction_size):
            s += "${} ".format(self.to_hex(self.read(self.pc + i)))
        return s.upper().ljust(12, " ")

    def clock(self):
        if self.cycles_left_to_perform_current_instruction == 0:
            self.new_instruction = True
            log_msg = ""
            cpu_state_before = ""
            if self.pc == 0x9c0d:
                j=3

            instruction = self.read(self.pc)
            log_msg += "{} ".format(self.to_hex(self.pc, 4)).upper()
            log_msg += self.inst_as_bytes(self.instructions[instruction].size())
            cpu_state_before = self.to_str().upper()
            ppu = self.bus.get_device_by_address(0x2000)
            #cpu_state_before += "CYC:{} SL:{} FC:{} CPU Cycle:{}\r\n".format(str(ppu.cycle).ljust(3, ' '), str(ppu.scanline).ljust(3, ' '), ppu.frame_cnt, self.clock_ticks)
            cpu_state_before += "\r\n"
            self.pc += 1

            self.cycles_left_to_perform_current_instruction = self.instructions[instruction].execute()
            log_msg += ascii(self.instructions[instruction])
            log_msg += cpu_state_before

            #if self.clock_ticks < 100:
            #print(log_msg.upper())
            fh = open("log.txt", "a")
            fh.write(log_msg)
            fh.close()

                #print(ascii(self.instructions[instruction]) + "   " + ascii(self))
            self.clock_ticks += self.cycles_left_to_perform_current_instruction
        else:
            self.new_instruction = False

        self.cycles_left_to_perform_current_instruction -= 1

    def read(self, address):
        if address == 0x7ff:    # FIXIT: just to debug other issues
            return 0xA5
        return self.bus.read(address)

    def write(self, address, data):
        if address == 0x7ff:
            j=3

        return self.bus.write(address, data)

    def push(self, value):
        #print("push: {}  SP:{}".format(hex(value), hex(self.sp)))
        self.write(0x0100 | self.sp, value)
        self.sp -= 1

    def pop(self):
        self.sp += 1
        val = self.read(0x0100 | self.sp)
        #print("pop: {}  SP:{}".format(hex(val), hex(self.sp)))
        return val

    def __repr__(self):
        return "CPU A:{}  X:{}  Y:{}  PC:{}  SP:{}  SR:{}  CYC:{}".format(hex(self.a), hex(self.x), hex(self.y), hex(self.pc), hex(self.sp), ascii(self.sr), self.clock_ticks)

    def reset(self):
        self.clock_ticks = 8
        self.pc = 0xFFFC

        ll = self.read(self.pc + 0)
        hh = self.read(self.pc + 1)

        self.pc = (hh << 8) | ll

        self.a = 0x91
        self.x = 0
        self.y = 0x05
        self.sp = 0xFC    # end of stack

        self.sr = StatusRegister()
        self.sr.from_byte(0x85)

    def nmi(self):
        print("CPU: NMI request")
        self.push((self.pc & 0xFF00) >> 8)
        self.push(self.pc & 0xFF)
        self.push(self.sr.to_byte())

        self.pc = 0xFFFA

        ll = self.read(self.pc + 0)
        hh = self.read(self.pc + 1)

        self.pc = (hh << 8) | ll
        self.sr.i = 1
        self.clock_ticks += 7
        #self.clock_ticks = 8

class RamMemory:

    def __init__(self):
        self.data = [0 for i in range(0x1FFF)]

    def read(self, address):
        return self.data[address & 0x07FF]

    def write(self, address, data):
        self.data[address & 0x07FF] = data

    def is_address_valid(self, address):
        if 0 <= address < 0x1FFF:
            return True
        return False


# Program ROM data 0x4020 - 0xFFFF
class Cardrige:

    def __init__(self, file_name):
        f = open(file_name, "rb")
        data = f.read()
        f.close()

        prg_size = data[4]
        chr_size = data[5]
        flag6 = data[6]
        flag7 = data[7]
        self.mirroring = flag6 & 0x1    # 0-horizontal, 1-veritcal

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
        if mapperId == 0:
            self.mapper = Mapper000(prg_size)

        #self.data = [0 for i in range(self.end_addr - self.start_addr)]
        #self.data[0xc000 - self.start_addr: len(prog_data)] = prog_data


    #def __init__(self, prog_start_addr, prog_data):
        #self.start_addr = 0x4020
        #self.end_addr = 0xFFFF
        #self.data = [0 for i in range(self.end_addr - self.start_addr)]
        #self.data[prog_start_addr - self.start_addr: len(prog_data)] = prog_data

    def read(self, address):
        #return self.data[address - self.start_addr]
        return self.prg[self.mapper.map_cpu_address(address)]

    def write(self, address, data):
        #self.data[address - self.start_addr] = data
        self.prg[self.mapper.map_cpu_address(address)] = data

    def is_address_valid(self, address):
        if self.start_addr <= address < self.end_addr:
            return True
        return False

    def get_tile_data(self, tile_number, row, half):
        lower_idx = (16 * tile_number) + row
        upper_idx = lower_idx + 8
        if half == 0:   # left
            return self.chr[lower_idx], self.chr[upper_idx]
        else:           # right - background
            return self.chr[lower_idx | 0x1000], self.chr[upper_idx | 0x1000]


class Mapper000:
    def __init__(self, prg_size):
        self.prg_size = prg_size

    def map_cpu_address(self, addr):
        if self.prg_size > 1:
            return addr & 0x7fff
        else:
            return addr & 0x3fff


class Apu:
    def __init__(self):
        self.start_addr = 0x4000
        self.end_addr = 0x4017
        self.data = [0 for i in range(self.end_addr - self.start_addr + 1)]

    def read(self, address):
        return self.data[address - self.start_addr]

    def write(self, address, data):
        self.data[address - self.start_addr] = data

    def is_address_valid(self, address):
        if self.start_addr <= address <= self.end_addr:
            return True
        return False


class StatusRegister:

    def __init__(self):
        self.n = 0  # negative
        self.v = 0  # Overflow
        #  -    ....ignored
        self.b = 0  # break
        self.d = 0  # decimal
        self.i = 0  # interrupt
        self.z = 0  # zero
        self.c = 0  # carry

    def to_byte(self):
        data = (self.n << 7) + (self.v << 6) + (self.b << 4) + (self.d << 3) + (self.i << 2) + (self.z << 1) + self.c
        return data

    def from_byte(self, data):
        self.c = data & 0x1
        self.z = (data >> 1) & 0x1
        self.i = (data >> 2) & 0x1
        self.d = (data >> 3) & 0x1
        self.b = (data >> 4) & 0x1
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
        return "ADC {}".format(self.addressMode)


class And:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.data = 0x00
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)
        self.data = operand

        self.str = ("AND " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

        self.cpu.a = self.cpu.a & operand

        if self.cpu.a == 0:
            self.cpu.sr.z = 1

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "AND {} = {}".format(self.addressMode, self.data)


class Asl:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        if address == 0xA0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)
        tmp = (operand << 1)

        self.str = ("ASL " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

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
        return self.str
        #return "ASL {}".format(ascii(self.addressMode))


# branch on carry clear
class Bcc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()

        self.str = ("BCC " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr))).upper().ljust(38, " ")

        if self.cpu.sr.c == 0:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "BCC {}".format(ascii(self.addressMode))


# branch on carry set
class Bcs:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()

        self.str = ("BCS " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr), 2)).upper().ljust(38, " ")

        if self.cpu.sr.c == 1:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "BCS {}".format(ascii(self.addressMode))


class Beq:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()

        self.str = ("BEQ " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr), 2)).upper().ljust(38, " ")

        if self.cpu.sr.z == 1:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "BEQ {}".format(ascii(self.addressMode))


class Bit:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.str = ("BIT " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

        self.cpu.sr.n = (operand >> 7) & 0x1
        self.cpu.sr.v = (operand >> 6) & 0x1
        if operand & self.cpu.a == 0:
            self.cpu.sr.z = 1

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "BIT {}".format(ascii(self.addressMode))


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
        return "BMI {}".format(ascii(self.addressMode))


class Bne:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()

        self.str = ("BNE " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr)) ).upper().ljust(38, " ")

        if self.cpu.sr.z == 0:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "BNE {}".format(ascii(self.addressMode))


class Bpl:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        self.str = ("BPL " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr))).upper().ljust(38, " ")
        if self.cpu.sr.n == 0:
            self.cpu.pc = addr
            return self.addressMode.cycles
        return 2

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "BPL {}".format(ascii(self.addressMode))


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
        return "BVC {}".format(ascii(self.addressMode))


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
        return "BVS {}".format(ascii(self.addressMode))


class Clc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.sr.c = 0
        self.str = ("CLC " + ascii(self.addressMode)).upper().ljust(38, " ")
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "CLC {}".format(ascii(self.addressMode))


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
        return "CLD".ljust(38, ' ')


class Cli:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def size(self):
        return self.addressMode.size

    def execute(self):
        self.cpu.sr.i = 0


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
        return "CLV {}".format(ascii(self.addressMode))


class Cmp:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.str = ("CMP " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

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
        return self.str
        #return "CMP {}".format(ascii(self.addressMode))


class Cpx:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.str = ("CPX " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

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
        return self.str
        #return "CPX {}".format(ascii(self.addressMode))


class Cpy:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.str = ("CPY " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

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
        return self.str
        #return "CPY {}".format(ascii(self.addressMode))


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
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        self.str = ("DEC " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

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
        return self.str
        #return "DEC {}".format(ascii(self.addressMode))


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
        return "DEX".ljust(38, " ")


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
        return "DEY".ljust(38, " ")


class Eor:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.str = ("EOR " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")
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
        return self.str
        #return "EOR {}".format(ascii(self.addressMode))


class Inc:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        operand += 1
        operand = operand & 0xff

        self.str = ("INC " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38," ")

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
        return self.str
        #return "INC {}".format(ascii(self.addressMode))


class Inx:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.x += 1
        self.cpu.x = self.cpu.x & 0xff

        self.str = ("INX " + ascii(self.addressMode)).upper().ljust(38, " ")

        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "INX {}".format(ascii(self.addressMode))


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
        return "INY".ljust(38, " ")


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
        self.str = ""

    def execute(self):
        #address = self.addressMode.get_address()
        #self.addressMode.fetch()
        self.cpu.pc = self.addressMode.get_address()

        self.str = ("JMP " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(self.cpu.pc))).upper().ljust(38, " ")
        #self.cpu.pc = (self.cpu.read(self.cpu.pc + 2) << 8) | self.cpu.read(self.cpu.pc + 1)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "JMP {}".format(ascii(self.addressMode))


# Jump to new location, save return address
class Jsr:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()

        self.str = ("JSR " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr))).upper().ljust(38, " ")

        self.cpu.push(((self.cpu.pc-1) & 0xFF00) >> 8)  # -1 because address mode will move pc to the next instruction
        self.cpu.push((self.cpu.pc-1) & 0xFF)

        #self.addressMode.fetch()
        self.cpu.pc = addr
        #self.cpu.pc = (self.cpu.read(self.cpu.pc + 2) << 8) + self.cpu.read(self.cpu.pc + 1)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "JSR {}".format(ascii(self.addressMode))


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
        self.data = 0x00
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        self.data = operand
        self.cpu.a = operand

        self.str = ("LDA " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

        if self.cpu.a == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "LDA {} ={}".format(ascii(self.addressMode), self.data)


class Ldx:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.data = 0x00
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)
        self.data = operand
        self.cpu.x = operand

        self.str = ("LDX " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")
        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "LDX {} = {}".format(ascii(self.addressMode), self.data)


class Ldy:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)
        self.cpu.y = operand

        self.str = ("LDY " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

        if self.cpu.y == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        self.cpu.sr.n = (self.cpu.y & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "LDY {}".format(ascii(self.addressMode))


class Lsr:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        operand = 0
        if address == 0xA0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)

        self.str = ("LSR " + ascii(self.addressMode)).upper().ljust(38, " ")

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
        return self.str
        #return "LSR {}".format(ascii(self.addressMode))


class Nop:

    def __init__(self, address_mode):
        self.addressMode = address_mode

    def execute(self):
        self.addressMode.get_address()
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "NOP {}".format(ascii(self.addressMode))


class Ora:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()
        operand = self.cpu.read(addr)

        self.str = ("ORA " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

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
        return self.str
        #return "ORA {}".format(ascii(self.addressMode))


class Pha:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.push(self.cpu.a)

        self.str = ("PHA " + ascii(self.addressMode)).upper().ljust(38, " ")

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "PHA {}".format(ascii(self.addressMode))


class Php:

    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        # PHP sets 4 and 5 bit of status register to 1
        val = self.cpu.sr.to_byte() | (1 << 5) | (1 << 4)
        self.cpu.push(val)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "PHP {}".format(ascii(self.addressMode))


class Pla:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.a = self.cpu.pop()

        self.str = ("PLA " + ascii(self.addressMode)).upper().ljust(38, " ")

        self.cpu.sr.n = (self.cpu.a & 0x80) >> 7

        if self.cpu.a == 0x00:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "PLA {}".format(ascii(self.addressMode))


class Plp:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        self.cpu.sr.from_byte(self.cpu.pop())
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "PLP {}".format(ascii(self.addressMode))


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
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        if address == 0xa0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)

        self.str = ("ROL " + ascii(self.addressMode)).upper().ljust(38, " ")

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
        #print("set C: {}".format(self.cpu.sr.c))
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "ROL {}".format(ascii(self.addressMode))


class Ror:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        address = self.addressMode.get_address()
        if address == 0xa0000:
            operand = self.cpu.a
        else:
            operand = self.cpu.read(address)

        self.str = ("ROR " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")
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
        #print("set C: {}".format(self.cpu.sr.c))
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "ROR {}".format(ascii(self.addressMode))


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
        print("old_c {}".format(old_c))
        print("new_c {}".format(operand & 0x01))

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
        self.cpu.sr.from_byte(self.cpu.pop())
        ll = self.cpu.pop()
        hh = self.cpu.pop()
        self.cpu.pc = (hh << 8) | ll
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "RTI {}".format(ascii(self.addressMode))


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
        return "RTS ".ljust(38, " ")


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
        self.str = ""

    def execute(self):
        # A - M - (1 - C)
        address = self.addressMode.get_address()
        operand = self.cpu.read(address)

        self.str = ("SBC " + ascii(self.addressMode) + "$" + to_str_hex(operand)).upper().ljust(38, " ")

        tmp = self.cpu.a - operand

        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) > 0:
            tmp -= 1

        if self.cpu.a == operand:
            self.cpu.sr.z = 1
            tmp = 0
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (tmp & 0x80) >> 7

        self.cpu.sr.v = 0
        self.cpu.sr.c = 1
        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (self.cpu.a < operand):
            self.cpu.sr.c = 0

        if (self.cpu.a & 0x80) > 0 and (operand & 0x80) > 0 and (self.cpu.a > operand):
            self.cpu.sr.c = 0

        if (self.cpu.a & 0x80) == 0 and (operand & 0x80) == 0 and (self.cpu.a < operand) and operand - self.cpu.a > 0x7F:
            self.cpu.sr.v = 1

        if (self.cpu.a & 0x80) > 0 and (operand & 0x80) == 0 and tmp & 0x80 == 0:
            self.cpu.sr.v = 1

        if tmp < -128:
            self.cpu.sr.v = 1

        if tmp < 0:
            tmp = hex(tmp & 0xff)
            tmp = int(tmp, 16)

        if tmp == -128:
            tmp = 0x7f

        if self.cpu.a == 0x80 and operand == 0x00:
            tmp = 0x7f

        self.cpu.a = tmp

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "SBC {}".format(ascii(self.addressMode))


class Sec:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.sr.c = 1

        self.str = ("SEC " + ascii(self.addressMode)).upper().ljust(38, " ")

        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "SEC {}".format(ascii(self.addressMode))


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
        return "SED {}".format(self.addressMode)


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
        return "SEI".ljust(38, " ")


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
        self.str = ""

    def execute(self):
        addr = self.addressMode.get_address()

        if addr >= 0x2000 and addr <= 0x2007: #fixit
            ppu = self.cpu.bus.get_device_by_address(0x2000)
            self.str = ("STA " + ascii(self.addressMode) + "$" + to_str_hex(ppu.last_written_data)).upper().ljust(38, " ")
        else:
            self.str = ("STA " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(addr))).upper().ljust(38, " ")

        self.cpu.write(addr, self.cpu.a)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "STA {}".format(ascii(self.addressMode))


class Stx:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        abs_addr = self.addressMode.get_address()

        self.str = ("STX " + ascii(self.addressMode) + "$" + to_str_hex(self.cpu.read(abs_addr))).upper().ljust(38, " ")

        self.cpu.write(abs_addr, self.cpu.x)
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "STX {}".format(ascii(self.addressMode))


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
        return "STY {}".format(ascii(self.addressMode))


class Tax:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.x = self.cpu.a

        self.str = ("TAX " + ascii(self.addressMode)).upper().ljust(38, " ")

        if self.cpu.x == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.x & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "TAX {}".format(ascii(self.addressMode))


class Tay:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode
        self.str = ""

    def execute(self):
        self.cpu.y = self.cpu.a

        self.str = ("TAY " + ascii(self.addressMode)).upper().ljust(38, " ")

        if self.cpu.y == 0:
            self.cpu.sr.z = 1
        else:
            self.cpu.sr.z = 0

        self.cpu.sr.n = (self.cpu.y & 0x80) >> 7
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return self.str
        #return "TAY {}".format(ascii(self.addressMode))


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
        return "TXA".ljust(38, ' ')


class Txs:
    def __init__(self, cpu, address_mode):
        self.cpu = cpu
        self.addressMode = address_mode

    def execute(self):
        #self.cpu.sr.from_byte(self.cpu.x)
        self.cpu.sp = self.cpu.x
        print(ascii(self.cpu.sr))
        print(ascii(self.cpu))
        return self.addressMode.cycles

    def size(self):
        return self.addressMode.size

    def __repr__(self):
        return "TXS".ljust(38, ' ')


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
        return "TYA {}".format(self.addressMode)

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
        # after instruction we have 16bit address
        # 1. get address of the data
        #self.cpu.pc += 1
        #ll = self.cpu.read(self.cpu.pc)
        #self.cpu.pc += 1
        #hh = self.cpu.read(self.cpu.pc)

        #self.abs_address = (hh << 8) | ll
        #self.cpu.operand = self.cpu.read(self.abs_address)
        return self.cpu.read(self.get_address())

    #def abs_address(self):
    #    return self.abs_address
    def get_address(self):
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.hh = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        self.abs_address = (self.hh << 8) | self.ll
        return self.abs_address

    #def get_bytes(self):
    #    return "${} ${} ".format(to_str_hex(self.ll), to_str_hex(self.hh))

    def __repr__(self):
        return "${} = ".format(to_str_hex(self.abs_address, 4))


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
        self.cpu.operand = self.cpu.read(addr)

        if (addr & 0xFF00) != (self.hh << 8) and self.extra_cycle:
            self.cycles += 1
        return addr

    #def get_bytes(self):
    #    return "${} ${} ".format(to_str_hex(self.ll), to_str_hex(self.hh))

    def __repr__(self):
        base_addr = (self.hh << 8) | self.ll
        abs_addr = base_addr + self.cpu.x
        return "${},X @ ${} = ".format(to_str_hex(base_addr, 4), to_str_hex(abs_addr, 4))


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
        return "${},Y @ ${} = ".format(to_str_hex(base_addr, 4), to_str_hex(addr, 4))


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
        return "#"


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
        return "(${}) @ ${} = ".format(to_str_hex(self.ptr, 4), to_str_hex(self.addr, 4))


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
        return "(${}),Y @ ${} = ".format(to_str_hex(self.ll, 4), to_str_hex(self.addr, 4))


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
        return "${} = ".format(to_str_hex(self.addr, 4))


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
        return "${} = ".format(to_str_hex(self.address, 4))


class AddressModeZeroPageXIndexed:

    def __init__(self, cpu, cycles=4):
        self.cpu = cpu
        self.abs_address = 0x0000
        self.ll = 0
        self.cycles = cycles
        self.size = 2

    def fetch(self):
        return self.cpu.read(self.get_address())

    def abs_address(self):
        return self.abs_address

    def get_address(self):
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        addr = self.ll + self.cpu.x
        addr &= 0x00FF
        return addr

    def __repr__(self):
        return "{},X".format(hex(self.ll))


class AddressModeZeroPageYIndexed:

    def __init__(self, cpu):
        self.cpu = cpu
        self.ll = 0
        self.cycles = 4
        self.size = 2

    def fetch(self):
        return self.cpu.read(self.get_address())

    def get_address(self):
        self.ll = self.cpu.read(self.cpu.pc)
        self.cpu.pc += 1
        addr = self.ll + self.cpu.y
        addr &= 0x00FF
        return addr

    def __repr__(self):
        return "{},Y".format(hex(self.ll))


def hex_to_signed_int(v):
    if v & 0x80:
        # negative number
        return -((~ v + 1) & 0xff)
    return v


def signed_int_to_hex(v):
    if v & 0x80:
        v *= -1
        return (~ v + 1) & 0xff
    else:
        return v


def to_str_hex(val, num_fields=2):
        return hex(val)[2:].zfill(num_fields)


if __name__ == "__main__":
    print("cpu impl")
    print(hex_to_signed_int(0xec))
    print(hex_to_signed_int(0x14))

    print(hex(signed_int_to_hex(-20)))
    print(hex(signed_int_to_hex(20)))
