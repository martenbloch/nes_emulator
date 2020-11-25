#include "ppu.h"
#include <iostream>

int main() {
    std::cout << "ppu impl" << std::endl;
    std::array<uint8_t, 8192> chr;
    Ppu ppu(chr, 0);
    ppu.clock();
}