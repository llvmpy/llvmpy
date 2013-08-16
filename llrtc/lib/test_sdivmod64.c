#include <stdio.h>
#include <stdint.h>
#include "llrt.h"

int main(int argc, char * argv[]){
    int64_t n, d, q, r;

    if (argc != 3) {
        printf("invalid argument: %s dividend divisor", argv[0]);
        return 1;
    }
    sscanf(argv[1], "%lld", &n);
    sscanf(argv[2], "%lld", &d);

    q = sdivmod64(n, d, &r);

    printf("%lld\n", q);
    printf("%lld\n", r);

    return 0;
}
