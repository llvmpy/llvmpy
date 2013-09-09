#include "llrt.h"

uint64_t umod64(uint64_t dividend, uint64_t divisor)
{
    uint64_t rem;
    udivmod64(dividend, divisor, &rem);
    return rem;
}

int64_t smod64(int64_t dividend, int64_t divisor)
{
    int64_t rem;
    sdivmod64(dividend, divisor, &rem);
    return rem;
}
