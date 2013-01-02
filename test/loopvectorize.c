void ex1(float *A, float* B, float K, int start, int end) {
    for (int i = start; i < end; ++i)
        A[i] *= B[i] + K;
}

void ex2(float *A, float* B, float K, int n) {
    for (int i = 0; i < n; ++i)
        A[i] *= B[i] + K;
}

int ex3(int *A, int *B, int n) {
    unsigned sum = 0;
    for (int i = 0; i < n; ++i)
        sum += A[i] + 5;
    return sum;
}

void ex4(float *A, float* B, float K, int n) {
    for (int i = 0; i < n; ++i)
        A[i] = i;
}

int ex5(int *A, int *B, int n) {
    unsigned sum = 0;
    for (int i = 0; i < n; ++i)
        if (A[i] > B[i])
            sum += A[i] + 5;
    return sum;
}

void ex6(int *A, int *B, int n) {
    for (int i = n; i > 0; --i)
        A[i] +=1;
}

void ex7(int *A, int *B, int n, int k) {
    for (int i = 0; i < n; ++i)
        A[i*7] += B[i*k];
}

void ex8(int *A, char *B, int n, int k) {
    for (int i = 0; i < n; ++i)
        A[i] += 4 * B[i];
}