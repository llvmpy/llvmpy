#ifndef LLRT_UDIVMOD_H_
#define LLRT_UDIVMOD_H_

#include <stdint.h>

#define BITS_PER_BYTE 8

uint64_t udivmod64(uint64_t dividend, uint64_t divisor, uint64_t *remainder);

#endif /* LLRT_UDIVMOD_H_ */

