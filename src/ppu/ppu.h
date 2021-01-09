#pragma once

#include <cstdint>
#include <array>
#include <vector>

struct Ppuctrl
{
    uint16_t baseNameTableAddress;
    uint8_t vramAddressIncrement;
    uint16_t spritePatternTableAddress;
    uint16_t backgroundPatternTableAddress;
    uint8_t spriteSize;
    bool generateNmi;
};

Ppuctrl byteToPpuCtrl(uint8_t data);

class PpuMask
{
    public:
        PpuMask();
        bool showBackground;
        bool showSprites;
};

PpuMask byteToPpuMask(uint8_t data);

struct Status
{
    Status();
    bool verticalBlank;
    bool spriteZeroHit;

    uint8_t toByte();
};

struct VramRegister
{
    uint8_t tile_row;
    uint8_t tileX;
    uint8_t tileY;
    uint8_t nametableX;
    uint8_t nametableY;
    uint16_t vramAddr;
    uint16_t baseNameTable;
    uint8_t fineY;

    uint16_t getVramAddress();
    void incrementTileX();
    void incrementTileY();
    void setAddress(uint16_t address);
    void setBaseNameTable(uint8_t value);
    void scrollX(uint8_t x);
    void scrollY(uint8_t y);
};

class TileHelper
{
    public:
        TileHelper(uint16_t lower, uint16_t upper):
        m_lower{lower}, m_upper{upper}
        {

        }

        void writeLower(uint16_t lower){
            m_lower = lower;
        }


        void writeLowerL(uint8_t lower){
            m_lower = (m_lower & 0xFF00) | lower;
        }

        void writeUpper(uint16_t upper){
            m_upper = upper;
        }

        void writeUpperL(uint8_t upper) {
            m_upper = (m_upper & 0xFF00) | upper;
        }

        uint8_t shift() {
            uint8_t b1 = (m_lower & 0x8000) > 0;
            uint8_t b2 = (m_upper & 0x8000) > 0;
            m_lower <<= 1;
            m_upper <<= 1;
            return (b2 << 1) | b1;
        }


    private:
        uint16_t m_lower;
        uint16_t m_upper;
};

struct TileRow
{
    uint8_t lower;
    uint8_t upper;
};

struct Pixel
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
};

struct OamData
{
    OamData();
    uint8_t palette();
    bool flipHorizontally();
    bool flipVertical();
    uint8_t x;
    uint8_t tile_num;
    uint8_t attr;
    uint8_t y;
};

class Ppu
{
    public:
        Ppu(uint8_t* patternTableData, uint16_t len, uint8_t mirroring);
        void clock();
        const std::vector<uint32_t>& getScreenData();
        void write(uint16_t address, uint8_t data);
        uint8_t read(uint16_t address);
        void reset();
        bool isAddressValid(uint16_t address);
        bool isNmiRaised();
        void clearNmi();
        bool bgRenderingEnabled();
        void writeOamData(uint8_t address, uint8_t data);
        uint8_t readOamData(uint8_t address);
        uint16_t getCycle();
        int getScanline();

    private:
        uint16_t m_cycle;
        int m_scanline;
        bool m_isOddFrame;

        Ppuctrl m_ctrl;
        PpuMask m_mask;
        Status m_status;

        VramRegister m_currAddr;
        VramRegister m_tmpAddr;

        std::array<uint8_t, 1024> m_nt0;
        std::array<uint8_t, 1024> m_nt1;
        std::array<uint8_t, 32> m_paletteRam;

        std::vector<uint8_t> m_chr;
        const uint8_t m_mirroring;

        TileHelper m_th;

        uint8_t m_paletteIdx;

        uint8_t m_backgroundHalf;

        int m_frameCnt;

        uint8_t m_nextTileId;

        uint16_t m_paletteBaseAddr;

        TileRow m_nextTileData;

        uint8_t m_bgPixel;

        bool m_raiseNmi;

        std::vector<uint32_t> m_frameData;
        std::array<uint32_t, 64> m_palette;

        uint8_t m_lastWrittenData;

        uint8_t m_addressLatch;

        uint8_t m_readBuffer;

        uint16_t m_ppuAddr;

        std::array<OamData, 64> m_oam;
        uint8_t m_oamAddr;
        std::array<OamData, 8> m_secondaryOam;
        uint8_t m_numSecondarySprites;
        std::array<uint8_t, 8> m_secondaryOamNumPixelToDraw;
        std::array<uint8_t, 8> m_secondaryOamXCounter;
        std::array<uint8_t, 8> m_secondaryOamAttrBytes;
        std::array<TileHelper, 8> m_sh;

        TileHelper m_nextAttribDataH;
        uint8_t m_nextAttribData;

        uint8_t readVideoMem(uint16_t address);
        TileRow getTileData(uint8_t tileNum, uint8_t row, uint8_t half);
        void getPaletteIdx();
        void clearSecondaryOam();
        void fillSecondaryOam(int y);
        void decrementSpriteXCounters();
        void fillSpritesShiftRegisters(int y);
};

uint8_t reverseBits(uint8_t val);