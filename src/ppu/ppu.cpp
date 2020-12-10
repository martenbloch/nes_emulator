#include "ppu.h"
#include <iostream>
#include <exception>

Ppuctrl byteToPpuCtrl(uint8_t data)
{
    Ppuctrl ctrl;
    uint8_t val{static_cast<uint8_t>(data & 0x3u)};
    if(val == 0)
        ctrl.baseNameTableAddress = 0x2000;
    else if(val == 1)
        ctrl.baseNameTableAddress = 0x2400;
    else if(val == 2)
        ctrl.baseNameTableAddress = 0x2800;
    else
        ctrl.baseNameTableAddress = 0x2C00;

    ctrl.vramAddressIncrement = ((data & 0x4) == 0) ? 1 : 32;
    ctrl.spritePatternTableAddress = ((data & 0x8) == 0) ? 0x0000 : 0x1000;
    ctrl.backgroundPatternTableAddress = ((data & 0x10) == 0) ? 0x0000 : 0x1000;
    ctrl.spriteSize = ((data & 0x20) == 0) ? 0 : 1; 
    ctrl.generateNmi = (data & 0x80) > 0;

    return ctrl;   
}

PpuMask::PpuMask()
: showBackground{false}, showSprites{false}
{

}

PpuMask byteToPpuMask(uint8_t data)
{
    PpuMask mask;

    mask.showBackground = ((data & 0x8) > 0);
    mask.showSprites = ((data & 0x10) > 0);
    return mask;
}

Status::Status()
: verticalBlank{false}, spriteZeroHit{false}
{

}

uint8_t Status::toByte()
{
    return (static_cast<uint8_t>(verticalBlank) << 7) | (static_cast<uint8_t>(spriteZeroHit) << 6);
}

uint16_t VramRegister::getVramAddress() 
{
    return baseNameTable | (tileY << 5) | tileX;
}

void VramRegister::incrementTileX()
{
    if(tileX == 31)
    {
        tileX = 0;
        baseNameTable ^= 0x400;
    }
    else
    {
        tileX += 1;
        vramAddr += 1;
    }
}

void VramRegister::incrementTileY()
{
    if(fineY < 7)
        fineY += 1;
    else
    {
        fineY = 0;
        if(tileY == 29)
        {
            tileY = 0;
            baseNameTable ^= 0x800;
        }
        else
            tileY += 1;
    }
}

void VramRegister::setAddress(uint16_t address)
{
    vramAddr = address;
    tileX = address & 0x1f;
    tileY = address & 0x3e0;
    setBaseNameTable(address & 0xc00);
}

void VramRegister::setBaseNameTable(uint8_t value)
{
    if(value == 0)
        baseNameTable = 0x2000;
    else if(value == 1)
        baseNameTable = 0x2400;
    else if(value == 2)
        baseNameTable = 0x2800;
    else if(value == 3)
        baseNameTable = 0x2C00;
}

void VramRegister::scrollX(uint8_t x)
{
    tileX = x/8;
}

void VramRegister::scrollY(uint8_t y)
{
    tileY = y/8;
}

OamData::OamData()
: x{0xFF},
  tile_num{0xFF},
  attr{0xFF},
  y{0xFF}
{

}

uint8_t OamData::palette()
{
    return attr & 0x3;
}

bool OamData::flipHorizontally()
{
    return (attr & 0x40) > 0;
}

Ppu::Ppu(uint8_t* patternTableData, uint16_t len, uint8_t mirroring)
: m_cycle{0}, 
 m_scanline{0}, 
 m_isOddFrame{true}, 
 m_ctrl{}, 
 m_mask{}, 
 m_status{}, 
 m_currAddr{}, 
 m_tmpAddr{}, 
 m_chr(len), 
 m_mirroring{mirroring},
 m_th{0x0000, 0x0000},
 m_paletteIdx{0x0},
 m_backgroundHalf{0},
 m_frameCnt{1},
 m_nextTileId{0},
 m_paletteBaseAddr{0x3F00},
 m_nextTileData{0x0000, 0x0000},
 m_bgPixel{0x0},
 m_frameData(256*240),
 m_raiseNmi{false},
 m_lastWrittenData{0x00},
 m_addressLatch{0},
 m_readBuffer{0x00},
 m_ppuAddr{0x0000},
 m_oam{},
 m_oamAddr{0x00},
 m_secondaryOam{},
 m_numSecondarySprites{0x00},
 m_secondaryOamNumPixelToDraw{{8, 8, 8, 8, 8, 8, 8, 8}},
 m_secondaryOamXCounter{{0, 0, 0, 0, 0, 0, 0, 0}},
 m_secondaryOamAttrBytes{{8, 8, 8, 8, 8, 8, 8, 8}},
 m_sh{TileHelper(0x0000,0x0000), TileHelper(0x0000,0x0000),TileHelper(0x0000,0x0000),TileHelper(0x0000,0x0000),TileHelper(0x0000,0x0000),TileHelper(0x0000,0x0000),TileHelper(0x0000,0x0000),TileHelper(0x0000,0x0000)},
 m_nextAttribDataH{0x0000, 0x0000},
 m_nextAttribData{0x00}
{
    m_chr.assign(patternTableData, patternTableData + len);

    /*
    m_palette[0x00] = {84, 84, 84};
    m_palette[0x01] = {0, 30, 116};
    m_palette[0x02] = {8, 16, 144};
    m_palette[0x03] = {48, 0, 136};
    m_palette[0x04] = {68, 0, 100};
    m_palette[0x05] = {92, 0, 48};
    m_palette[0x06] = {84, 4, 0};
    m_palette[0x07] = {60, 24, 0};
    m_palette[0x08] = {32, 42, 0};
    m_palette[0x09] = {8, 58, 0};
    m_palette[0x0A] = {0, 64, 0};
    m_palette[0x0B] = {0, 60, 0};
    m_palette[0x0C] = {0, 50, 60};
    m_palette[0x0D] = {0, 0, 0};
    m_palette[0x0E] = {0, 0, 0};
    m_palette[0x0F] = {0, 0, 0};

    m_palette[0x10] = {152, 150, 152};
    m_palette[0x11] = {8, 76, 196};
    m_palette[0x12] = {48, 50, 236};
    m_palette[0x13] = {92, 30, 228};
    m_palette[0x14] = {136, 20, 176};
    m_palette[0x15] = {160, 20, 100};
    m_palette[0x16] = {152, 34, 32};
    m_palette[0x17] = {120, 60, 0};
    m_palette[0x18] = {84, 90, 0};
    m_palette[0x19] = {40, 114, 0};
    m_palette[0x1A] = {8, 124, 0};
    m_palette[0x1B] = {0, 118, 40};
    m_palette[0x1C] = {0, 102, 120};
    m_palette[0x1D] = {0, 0, 0};
    m_palette[0x1E] = {0, 0, 0};
    m_palette[0x1F] = {0, 0, 0};

    m_palette[0x20] = {236, 238, 236};
    m_palette[0x21] = {76, 154, 236};
    m_palette[0x22] = {120, 124, 236};
    m_palette[0x23] = {176, 98, 236};
    m_palette[0x24] = {228, 84, 236};
    m_palette[0x25] = {236, 88, 180};
    m_palette[0x26] = {236, 106, 100};
    m_palette[0x27] = {212, 136, 32};
    m_palette[0x28] = {160, 170, 0};
    m_palette[0x29] = {116, 196, 0};
    m_palette[0x2A] = {76, 208, 32};
    m_palette[0x2B] = {56, 204, 108};
    m_palette[0x2C] = {56, 180, 204};
    m_palette[0x2D] = {60, 60, 60};
    m_palette[0x2E] = {0, 0, 0};
    m_palette[0x2F] = {0, 0, 0};

    m_palette[0x30] = {236, 238, 236};
    m_palette[0x31] = {168, 204, 236};
    m_palette[0x32] = {188, 188, 236};
    m_palette[0x33] = {212, 178, 236};
    m_palette[0x34] = {236, 174, 236};
    m_palette[0x35] = {236, 174, 212};
    m_palette[0x36] = {236, 180, 176};
    m_palette[0x37] = {228, 196, 144};
    m_palette[0x38] = {204, 210, 120};
    m_palette[0x39] = {180, 222, 120};
    m_palette[0x3A] = {168, 226, 144};
    m_palette[0x3B] = {152, 226, 180};
    m_palette[0x3C] = {160, 214, 228};
    m_palette[0x3D] = {160, 162, 160};
    m_palette[0x3E] = {0, 0, 0};
    m_palette[0x3F] = {0, 0, 0};
    */

    m_palette[0x00] = 0x545454;
    m_palette[0x01] = 0x001E74;
    m_palette[0x02] = 0x081090;
    m_palette[0x03] = 0x300088;
    m_palette[0x04] = 0x440064;
    m_palette[0x05] = 0x5C0030;
    m_palette[0x06] = 0x540400;
    m_palette[0x07] = 0x3C1800;
    m_palette[0x08] = 0x202A00;
    m_palette[0x09] = 0x083A00;
    m_palette[0x0A] = 0x004000;
    m_palette[0x0B] = 0x003C00;
    m_palette[0x0C] = 0x00323C;
    m_palette[0x0D] = 0x000000;
    m_palette[0x0E] = 0x000000;
    m_palette[0x0F] = 0x000000;
    m_palette[0x10] = 0x989698;
    m_palette[0x11] = 0x084CC4;
    m_palette[0x12] = 0x3032EC;
    m_palette[0x13] = 0x5C1EE4;
    m_palette[0x14] = 0x8814B0;
    m_palette[0x15] = 0xA01464;
    m_palette[0x16] = 0x982220;
    m_palette[0x17] = 0x783C00;
    m_palette[0x18] = 0x545A00;
    m_palette[0x19] = 0x287200;
    m_palette[0x1A] = 0x087C00;
    m_palette[0x1B] = 0x007628;
    m_palette[0x1C] = 0x006678;
    m_palette[0x1D] = 0x000000;
    m_palette[0x1E] = 0x000000;
    m_palette[0x1F] = 0x000000;
    m_palette[0x20] = 0xECEEEC;
    m_palette[0x21] = 0x4C9AEC;
    m_palette[0x22] = 0x787CEC;
    m_palette[0x23] = 0xB062EC;
    m_palette[0x24] = 0xE454EC;
    m_palette[0x25] = 0xEC58B4;
    m_palette[0x26] = 0xEC6A64;
    m_palette[0x27] = 0xD48820;
    m_palette[0x28] = 0xA0AA00;
    m_palette[0x29] = 0x74C400;
    m_palette[0x2A] = 0x4CD020;
    m_palette[0x2B] = 0x38CC6C;
    m_palette[0x2C] = 0x38B4CC;
    m_palette[0x2D] = 0x3C3C3C;
    m_palette[0x2E] = 0x000000;
    m_palette[0x2F] = 0x000000;
    m_palette[0x30] = 0xECEEEC;
    m_palette[0x31] = 0xA8CCEC;
    m_palette[0x32] = 0xBCBCEC;
    m_palette[0x33] = 0xD4B2EC;
    m_palette[0x34] = 0xECAEEC;
    m_palette[0x35] = 0xECAED4;
    m_palette[0x36] = 0xECB4B0;
    m_palette[0x37] = 0xE4C490;
    m_palette[0x38] = 0xCCD278;
    m_palette[0x39] = 0xB4DE78;
    m_palette[0x3A] = 0xA8E290;
    m_palette[0x3B] = 0x98E2B4;
    m_palette[0x3C] = 0xA0D6E4;
    m_palette[0x3D] = 0xA0A2A0;
    m_palette[0x3E] = 0x000000;
    m_palette[0x3F] = 0x000000;

}

uint8_t Ppu::readVideoMem(uint16_t address)
{
    if(address >= 0x2000 && address <= 0x3eff)
    {
        uint16_t index{static_cast<uint16_t>(address & 0x03ff)};
        if(m_mirroring == 0)  // horizontal
        {
            if( (address >= 0x2000 && address <= 0x23ff) || (address >= 0x2400 && address <= 0x27ff))
                return m_nt0[index];
            else if((address >= 0x2800 && address <= 0x2bff) || (address >= 0x2c00 && address <= 0x2fff))
                return m_nt1[index];
        }
        else
        {
            if((address >= 0x2000 && address <= 0x23ff) || (address >= 0x2800 && address <= 0x2bff))
                return m_nt0[index];
            else if((address >= 0x2400 && address <= 0x27ff) || (address >= 0x2c00 && address <= 0x2fff))
                return m_nt1[index];
        }
    } 
    else if(address >= 0x3f00 && address <= 0x3fff) 
    {
        if(address == 0x3f04 || address == 0x3F08 || address == 0x3F0C)
        {
            address = 0x3f00;
        }

        address &= 0x001F;

        return m_paletteRam[address & 0xff]; // TODO: check it

    }
    else if( address >= 0 && address <= 0x1fff)
    {
        return m_chr[address];  // TODO: check it
    }
    else
        throw std::exception();
    return 0x0000;
}

TileRow Ppu::getTileData(uint8_t tileNum, uint8_t row, uint8_t half)
{
    uint16_t lowerIdx{static_cast<uint16_t>((16 * tileNum) + row)};
    uint16_t upperIdx{static_cast<uint16_t>(lowerIdx + 8)};
    if(half == 0)   // left
        return {m_chr[lowerIdx], m_chr[upperIdx]};
    else           // right - background
        return {m_chr[lowerIdx | 0x1000], m_chr[upperIdx | 0x1000]};
}

void Ppu::getPaletteIdx()
{
    uint8_t attr_data = readVideoMem(m_currAddr.baseNameTable | 0x3c0 | (m_currAddr.tileX >> 2) | ((m_currAddr.tileY >> 2) << 3));

    if(m_currAddr.tileY & 0x02)
        attr_data = attr_data >> 4;
    else if(m_currAddr.tileX & 0x02)
        attr_data = attr_data >> 2;
    attr_data = attr_data & 0x03;
    m_paletteIdx = attr_data;
}

void Ppu::clearSecondaryOam()
{
    m_secondaryOam.fill(OamData());
}

void Ppu::fillSecondaryOam(int y)
{
    m_numSecondarySprites = 0;
    m_secondaryOamNumPixelToDraw.fill(0);
    uint8_t n = (m_ctrl.spriteSize == 1) ? 16 : 8;
    
    for(int i =0; i < 64; ++i)
    {
        if(y >= m_oam[i].y && y < (m_oam[i].y + n))
        {
            m_secondaryOam[m_numSecondarySprites] = m_oam[i];
            m_secondaryOamXCounter[m_numSecondarySprites] = m_oam[i].x;
            m_secondaryOamAttrBytes[m_numSecondarySprites] = m_oam[i].attr;
            m_secondaryOamNumPixelToDraw[m_numSecondarySprites] = 8;
            m_numSecondarySprites += 1;
            if(m_numSecondarySprites == 8)
                break;
        }
    }
}

void Ppu::decrementSpriteXCounters()
{
    for(int i =0; i < m_numSecondarySprites; ++i )
    {
        if(m_secondaryOamXCounter[i] > 0)
            m_secondaryOamXCounter[i] -= 1;
        if(m_secondaryOamXCounter[i] == 0 && m_secondaryOamNumPixelToDraw[i] > 0)
        {
            uint8_t color = m_sh[i].shift();

            uint8_t pallete_idx = m_secondaryOam[i].palette();
            uint8_t idx = (readVideoMem(0x3F10 + (pallete_idx << 2) + color)) & 0x3f;

            uint8_t priority = (m_secondaryOamAttrBytes[i] & 0x20) >> 5;

            if(priority == 0 && color != 0)
            {
                m_frameData[(m_cycle - 1) + m_scanline*256] = m_palette[idx];
            }
            m_secondaryOamNumPixelToDraw[i] -= 1;

            if(!m_status.spriteZeroHit && i == 0 && color != 0 && m_bgPixel != 0)
            {
                m_status.spriteZeroHit = true;
            }
        }
    }
}

void Ppu::fillSpritesShiftRegisters(int y)
{
    for(int i=0; i<8; ++i)
    {
        OamData sprite = m_secondaryOam[i];
        uint8_t row = y - sprite.y;
        uint8_t half = 0;
        if(m_ctrl.spritePatternTableAddress == 0x1000)
            half = 1;
        
        uint8_t tile_num = sprite.tile_num;
        if(m_ctrl.spriteSize == 1)
        {
            row = row % 8;
            tile_num &= 0xFE;
            half = sprite.tile_num & 0x1;
            if(y - sprite.y >= 8)
                tile_num += 1;
        }

        TileRow tr = getTileData(tile_num, row, half);
        
        if(sprite.flipHorizontally())
        {
            tr.lower = reverseBits(tr.lower);
            tr.upper = reverseBits(tr.upper);
        }

        uint16_t l = uint16_t(tr.lower) << 8;
        uint16_t u = uint16_t(tr.upper) << 8;

        m_sh[i].writeLower(l);
        m_sh[i].writeUpper(u);
    }
}


const std::vector<uint32_t>& Ppu::getScreenData()
{
    return m_frameData;
}

void Ppu::write(uint16_t address, uint8_t data)
{
    if(address == 0x2000)
    {
        m_lastWrittenData = data;
        m_ctrl = byteToPpuCtrl(data);
        m_tmpAddr.setBaseNameTable(data & 0x3);

        if(data & 0x10)    // TODO: remove it
            m_backgroundHalf = 1;
        else
            m_backgroundHalf = 0;
        return;
    }
    else if(address == 0x2001)
    {
        m_lastWrittenData = data;
        m_mask = byteToPpuMask(data);
        return;
    }
    else if(address == 0x2003)
    {
        m_lastWrittenData = data;
        m_oamAddr = data;
    }
    else if(address == 0x2004)
    {
        m_lastWrittenData = data;
        writeOamData(m_oamAddr, data);
        m_oamAddr += 1;
    }
    else if(address == 0x2005)
    {
        m_lastWrittenData = data;
        if(m_addressLatch == 0)
        {
            m_addressLatch = 1;
            m_tmpAddr.scrollX(data);
        }
        else
        {
            m_addressLatch = 0;
            m_tmpAddr.scrollY(data);
        }
    }
    else if(address == 0x2006)
    {
        m_lastWrittenData = data;
        if(m_addressLatch == 0)
        {
            m_addressLatch = 1;
            m_ppuAddr = 0x0000 | ((data & 0x3f) << 8);
            m_tmpAddr.setAddress((m_tmpAddr.vramAddr & 0x00ff) | ((data & 0x3f) << 8));
        }
        else
        {
            m_addressLatch = 0;
            m_ppuAddr = m_ppuAddr | data;
            
            m_currAddr.setAddress(m_ppuAddr);
            m_tmpAddr.setAddress(m_ppuAddr);
        }
        return;
    }
    else if(address == 0x2007)
    {
        if(m_currAddr.vramAddr >= 0x2000 && m_currAddr.vramAddr <= 0x3eff)
        {
            uint16_t index = m_currAddr.vramAddr & 0x3ff;
            if(m_mirroring == 0)
            {
                if(m_currAddr.vramAddr >= 0x2000 && m_currAddr.vramAddr <= 0x23ff)
                    m_nt0[index] = data;
                else if(m_currAddr.vramAddr >= 0x2400 && m_currAddr.vramAddr <= 0x27ff)
                    m_nt0[index] = data;
                else if(m_currAddr.vramAddr >= 0x2800 && m_currAddr.vramAddr <= 0x2bff)
                    m_nt1[index] = data;
                else if(m_currAddr.vramAddr >= 0x2c00 && m_currAddr.vramAddr <= 0x2fff)
                    m_nt1[index] = data;
            }
            else
                if(m_currAddr.vramAddr >= 0x2000 && m_currAddr.vramAddr <= 0x23ff)
                    m_nt0[index] = data;
                else if(m_currAddr.vramAddr >= 0x2400 && m_currAddr.vramAddr <= 0x27ff)
                    m_nt1[index] = data;
                else if(m_currAddr.vramAddr >= 0x2800 && m_currAddr.vramAddr <= 0x2bff)
                    m_nt0[index] = data;
                else if(m_currAddr.vramAddr >= 0x2c00 && m_currAddr.vramAddr <= 0x2fff)
                    m_nt1[index] = data;
        }
        else if(m_currAddr.vramAddr >= 0x3f00 && m_currAddr.vramAddr <= 0x3fff)
        {
            uint16_t addr = m_currAddr.vramAddr & 0x001F;
            if(addr == 0x0010)
                addr = 0x0000;
            else if(addr == 0x0014)
                addr = 0x0004;
            else if(addr == 0x0018)
                addr = 0x0008;
            else if(addr == 0x001C)
                addr = 0x000C;
            m_paletteRam[addr] = data;
        }
        else if(m_currAddr.vramAddr >= 0 && m_currAddr.vramAddr <= 0x1fff)
            m_chr[m_currAddr.vramAddr] = data;
        else
            std::cout << "Eception, unhandled vram addr: " << m_currAddr.vramAddr << " data: " << int(data) << std::endl;

        m_currAddr.vramAddr += m_ctrl.vramAddressIncrement;
    }
    else
        std::cout << "Exception, unhandled address: " << address << " data: " << int(data) << std::endl;
}


uint8_t Ppu::read(uint16_t address)
{
    if(address == 0x2002)
    {
        //std::cout << "mask: " << std::hex << int(m_status.toByte()) << std::endl;
        uint8_t val = m_lastWrittenData & 0x1f | m_status.toByte() & 0xe0;
        m_status.verticalBlank = false;
        m_addressLatch = 0;
        return val;
    }
    else if(address == 0x2007)
    {
        uint8_t val{0};
        if( m_currAddr.vramAddr >= 0x2000 && m_currAddr.vramAddr <= 0x3eff)
        {
            val = m_readBuffer;
            m_readBuffer = readVideoMem(m_currAddr.vramAddr);
        }
        else if(m_currAddr.vramAddr >= 0x3f00 && m_currAddr.vramAddr <= 0x3fff)
        {
            uint8_t index = m_currAddr.vramAddr & 0x3ff;
            m_readBuffer = m_nt1[index];
            uint8_t addr = m_currAddr.vramAddr & 0x001F;
            if(addr == 0x0010)
                addr = 0x0000;
            else if(addr == 0x0014)
                addr = 0x0004;
            else if(addr == 0x0018)
                addr = 0x0008;
            else if(addr == 0x001C)
                addr = 0x000C;

            val = m_paletteRam[addr];
        }
        else if(m_currAddr.vramAddr >= 0 && m_currAddr.vramAddr <= 0x1fff)
        {
            val = m_readBuffer;
            m_readBuffer = m_chr[m_currAddr.vramAddr];
        }
        else
            throw std::exception();

        m_currAddr.vramAddr += m_ctrl.vramAddressIncrement;

        return val;
    }
    else
        throw std::exception();
}

void Ppu::reset()
{
    m_cycle = 24;
}

bool Ppu::isAddressValid(uint16_t address)
{
    return address >= 0x2000 && address < 0x2008;
}

bool Ppu::isNmiRaised()
{
    return m_raiseNmi;
}

void Ppu::clearNmi()
{
    m_raiseNmi = false;
    m_cycle += 21;
}

bool Ppu::bgRenderingEnabled()
{
    return m_mask.showBackground;
}

void Ppu::writeOamData(uint8_t address, uint8_t data)
{
        uint8_t idx = address/4;
        uint8_t param_idx = address % 4;

        if(idx >= m_oam.size())
        {
            std::cout << "out of range" << std::endl;
        }

        if(param_idx == 0)
            m_oam[idx].y = data;
        else if(param_idx == 1)
            m_oam[idx].tile_num = data;
        else if(param_idx == 2)
            m_oam[idx].attr = data;
        else if(param_idx == 3)
            m_oam[idx].x = data;
}

void Ppu::clock() 
{
    if (m_scanline == -1) 
    {
        if (m_cycle == 1) {
            m_status.verticalBlank = false;
            m_status.spriteZeroHit = false;
        }
        else if(m_cycle >= 280 && m_cycle <= 304) {
            m_currAddr.baseNameTable = m_tmpAddr.baseNameTable;
            m_currAddr.tileY = m_tmpAddr.tileY;
            m_currAddr.fineY = m_tmpAddr.fineY;
        }
        else if(m_cycle == 322 && m_mask.showBackground)
        {
            uint8_t firstTileId = readVideoMem(m_currAddr.getVramAddress());
            getPaletteIdx();
            m_currAddr.incrementTileX();
            uint8_t secondTileId = readVideoMem(m_currAddr.getVramAddress());
            m_currAddr.incrementTileX();

            TileRow tr1 = getTileData(firstTileId, m_currAddr.fineY, m_backgroundHalf);
            TileRow tr2 = getTileData(secondTileId, m_currAddr.fineY, m_backgroundHalf);

            m_th.writeLower((tr1.lower << 8) | tr2.lower);
            m_th.writeUpper((tr1.upper << 8) | tr2.upper);
        }
    }
        // visible scanline section
    else if( m_scanline >= 0 && m_scanline <= 239)
    {
        if(m_mask.showBackground)
        {
            if(m_scanline == 0 && m_cycle == 0 && m_isOddFrame)
                m_cycle = 1;

            else if((m_cycle >= 1 && m_cycle <= 256) || (m_cycle >= 321 && m_cycle <= 340))
            {
                uint8_t r = m_cycle % 8;
                if(r == 2)
                    m_nextTileId = readVideoMem(m_currAddr.getVramAddress());

                else if(r == 4)
                {
                    uint16_t addr = m_currAddr.baseNameTable | 0x3c0 | (m_currAddr.tileX >> 2) | ((m_currAddr.tileY >> 2) << 3);

                    uint8_t attrData = readVideoMem(addr);

                    if(m_currAddr.tileY & 0x02)
                        attrData >>= 4;
                    else if( m_currAddr.tileX & 0x02)
                        attrData >>= 2;
                    attrData &= 0x03;
                    m_nextAttribData = attrData;
                    m_paletteIdx = attrData;
                    m_paletteBaseAddr = 0x3F00 + (m_paletteIdx << 2);
                }
                // performcne improvement, read tile data at once
                //else if( m_cycle % 8 == 6:
                //    self.next_tile_low, u1 = self.cardridge.get_tile_data(self.next_tile_id, m_currAddr.fine_y,
                //                                                          self.background_half)

                else if(r == 0)
                {
                    m_nextTileData = getTileData(m_nextTileId, m_currAddr.fineY, m_backgroundHalf);
                    m_currAddr.incrementTileX();
                }
                else if( r == 1 && m_cycle > 1)
                {
                    m_th.writeLowerL(m_nextTileData.lower);
                    m_th.writeUpperL(m_nextTileData.upper);

                    m_nextAttribDataH.writeLowerL((m_nextAttribData & 0x1) ? 0xFF : 0x00);
                    m_nextAttribDataH.writeUpperL((m_nextAttribData & 0x2) ? 0xFF : 0x00);
                }
            }
            if(m_cycle >=1 && m_cycle <= 336)
            {
                m_bgPixel = m_th.shift();
                m_paletteIdx = m_nextAttribDataH.shift();
                if(m_cycle >=1 && m_cycle <= 256)
                {
                    uint8_t idx = (readVideoMem(0x3F00 + (m_paletteIdx << 2) + m_bgPixel)) & 0x3f;
                    m_frameData[(m_cycle - 1) + m_scanline*256] = m_palette[idx];
                }
            }
            if(m_cycle == 256)
                m_currAddr.incrementTileY();
            else if( m_cycle == 257)
            {
                m_currAddr.baseNameTable = m_tmpAddr.baseNameTable;
                m_currAddr.tileX = m_tmpAddr.tileX;
            }
        }
        // ------------------------------sprite rendering------------------------------
        if(m_mask.showSprites)
        {
            if(m_cycle>=0 && m_cycle <= 255)
                decrementSpriteXCounters();
            else if( m_cycle == 1)
                clearSecondaryOam();
            else if( m_cycle == 256)
                fillSecondaryOam(m_scanline);
            else if( m_cycle == 257)
                fillSpritesShiftRegisters(m_scanline);
        }
    }
    else if(m_scanline == 240 && m_cycle == 0)
        m_frameCnt += 1;
    else if(m_scanline == 241 && m_cycle == 1)
    {
        m_status.verticalBlank = true;
        if(m_ctrl.generateNmi)
            m_raiseNmi = true;
    }


    m_cycle += 1;
    if(m_cycle == 341) {
        m_cycle = 0;
        m_scanline += 1;
        if(m_scanline == 261) {
            m_scanline = -1;
            m_isOddFrame = !m_isOddFrame;
        }
    }
}

uint8_t reverseBits(uint8_t val)
{
    uint8_t res = 0x00;
    uint8_t pos = 7;
    uint8_t bit = 0x00;
    for(int i=0;i<8;++i)
    {
        bit = val & 0x1;
        res |= bit << pos;
        pos--; 
        val >>= 1;
    }
    return res;
}

int main()
{
    std::cout << std::hex << int(reverseBits(0xd8)) << std::endl;
}