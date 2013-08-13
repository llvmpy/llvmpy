#include <stdio.h>
#include <stdint.h>

extern uint64_t
udivmod64(uint64_t dividend, uint64_t divisor, uint64_t *remainder);

int main(int argc, char * argv[]){
    uint64_t n, d, q, r;
    if (argc != 3) {
        printf("invalid argument: %s dividend divisor", argv[0]);
        return 1;
    }
    sscanf(argv[1], "%llu", &n);
    sscanf(argv[2], "%llu", &d);

    q = udivmod64(n, d, &r);

    printf("%llu\n", q);
    printf("%llu\n", r);

    return 0;
}