/*
Implements unsigned divmod using for platform missing 64-bit division and/or
modulo functions.
*/
#include "llrt.h"

/*
count left zero for 64-bit words

*/
static
int clz64(uint64_t x)
{
    const int total_bits = sizeof(x) * BITS_PER_BYTE;
    int zc = 0;

    while (zc < total_bits && ((x >> (total_bits - zc - 1)) & 1) == 0) {
        ++zc;
    }
    return zc;
}

typedef struct div_state_
{
    uint64_t tmp, dvd;
} div_state;

/*
Left shift div_state by 1 bit
*/
static
void div_state_lshift(div_state *state)
{
    state->tmp = (state->tmp << 1) | (state->dvd >> 63);
    state->dvd = state->dvd << 1;
}

/*
Division of unsigned 64-bit word using 64-bit addition and subtration following
the shift-restore division algorithm.
For those interested in 32-bit implementation,
mapping of 64-bit addition and subtraction to 32-bit should be trivial.

Reference: 
    - IBM. The PowerPC Compiler Writer's Guide
    - LLVM compiler-rt

Assumptions:
    - all operands and results are positive
    - unsigned wrapped around
*/
uint64_t udivmod64(uint64_t dividend, uint64_t divisor, uint64_t *remainder)
{
    div_state state = {0, dividend};
    uint64_t quotient = 0;
    int i;
    int skipahead;

    if (divisor == 0) {
        return 1 / 0;               /* intentionally div by zero */
    }

    /*
    skipahead to reduce iteration
    */
    skipahead = clz64(dividend);

    for (i = 0; i < skipahead; ++i) {
        div_state_lshift(&state);
    }

    /*
    division loop
    */
    for (i = skipahead; i < 64; ++i) {
        div_state_lshift(&state);
        if (state.tmp >= divisor) {
            state.tmp = state.tmp - divisor;
            quotient |= 1ull << (63 - i);
        }
    }
    if (remainder) *remainder = state.tmp;
    return quotient;
}
