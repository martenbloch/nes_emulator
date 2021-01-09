#include <iostream>
#include <array>
#include "ppu.h"

extern "C" {
    
    Ppu* ppu_new(uint8_t* patternTableData, uint16_t len, uint8_t mirroring)
    {
        return new Ppu(patternTableData, len, mirroring);
    }

    void ppu_clock(Ppu* ppu)
    {
        ppu->clock();
    }

    void ppu_reset(Ppu* ppu)
    {
        ppu->reset();
    }

    void ppu_is_nmi_raised(Ppu* ppu)
    {
        ppu->isNmiRaised();
    }

    uint16_t ppu_get_cycle(Ppu* ppu)
    {
        return ppu->getCycle();
    }
    
    int ppu_get_scanline(Ppu* ppu)
    {
        return ppu->getScanline();
    }

    void ppu_clear_nmi(Ppu* ppu)
    {
        ppu->clearNmi();
    }

    bool ppu_is_address_valid(Ppu* ppu, uint16_t address)
    {
        return ppu->isAddressValid(address);
    }

    void ppu_write(Ppu* ppu, uint16_t address, uint8_t data)
    {
        //std::cout << "write addr: " << address << " data: " << int(data) << std::endl;
        ppu->write(address, data);
    }

    uint8_t ppu_read(Ppu* ppu, uint16_t address)
    {
        //std::cout << "read addr: " << address << std::endl; 
        return ppu->read(address);
    }

    const uint32_t* ppu_get_frame_data(Ppu* ppu)
    {
        return ppu->getScreenData().data();
    }

    bool ppu_bg_enabled(Ppu* ppu)
    {
        return ppu->bgRenderingEnabled();
    }

    void ppu_write_oam_data(Ppu* ppu, uint8_t address, uint8_t data)
    {
        ppu->writeOamData(address, data);
    }

    /*
    g++ -c -fPIC ppu.cpp -o ppu.o
    g++ -c -fPIC libppu.cpp -o libppu.o
    g++ -shared -Wl,-soname,libppu.so -o libppu.so libppu.o ppu.o
    mv libppu.so ../cpu/

    TileHelper* TileHelper_new(uint16_t lower, uint16_t upper) { return new TileHelper(lower, upper); }
    void TileHelper_writeLower(TileHelper* tileHelper, uint16_t lower) { tileHelper->writeLower(lower);}
    void TileHelper_writeLowerL(TileHelper* tileHelper, uint8_t lower) { tileHelper->writeLowerL(lower);}
    void TileHelper_writeUpper(TileHelper* tileHelper, uint16_t upper) { tileHelper->writeUpper(upper);}
    void TileHelper_writeUpperL(TileHelper* tileHelper, uint8_t upper) { tileHelper->writeUpperL(upper);}
    uint8_t TileHelper_shift(TileHelper* tileHelper) { return tileHelper->shift(); };
    */
}