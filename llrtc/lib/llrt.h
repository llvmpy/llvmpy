#ifndef LLRT_H_
#define LLRT_H_

#include <stdint.h>

#define BITS_PER_BYTE 8

uint64_t udivmod64(uint64_t dividend, uint64_t divisor, uint64_t *remainder);
int64_t sdivmod64(int64_t dividend, int64_t divisor, int64_t *remainder);

#endif /* LLRT_H_ */

