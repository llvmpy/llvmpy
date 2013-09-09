#include "llrt.h"
#include <stdio.h>

/*
Calls to udivmod64 internally.
Note: remainder uses sign of divisor.
*/
int64_t sdivmod64(int64_t dividend, int64_t divisor, int64_t *remainder)
{
    int signbitidx = BITS_PER_BYTE * sizeof(dividend) - 1;
    int signed_dividend = dividend < 0;
    int signed_divisor = divisor < 0;
    int signed_result = signed_divisor ^ signed_dividend;

    int64_t quotient;
    uint64_t udvd, udvr, uquotient, uremainder;

    udvd = signed_dividend ? -dividend : dividend;
    udvr = signed_divisor ? -divisor : divisor;
    uquotient = udivmod64(udvd, udvr, &uremainder);

    if (signed_result){
        if (uremainder) {
            quotient = -(int64_t)uquotient - 1;
        } else {
            quotient = -(int64_t)uquotient;
        }
        if (remainder) {
            /* if signed, there could be unsigned overflow
               causing undefined behavior */
            *remainder = (uint64_t)dividend - (uint64_t)quotient * (uint64_t)divisor;
        }
    } else {
        quotient = (int64_t)uquotient;
        if (remainder) {
            *remainder = signed_divisor ? -uremainder : uremainder;
        }
    }
    return quotient;
}
