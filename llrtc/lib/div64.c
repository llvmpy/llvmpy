#include "llrt.h"

uint64_t udiv64(uint64_t dividend, uint64_t divisor)
{
    return udivmod64(dividend, divisor, NULL);
}

int64_t sdiv64(int64_t dividend, int64_t divisor)
{
    return sdivmod64(dividend, divisor, NULL);
}
