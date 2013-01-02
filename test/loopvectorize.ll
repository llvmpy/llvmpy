; ModuleID = 'loopvectorize.c'
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
;target triple = "x86_64-apple-macosx10.8.0"
target triple = "x86-64-unknown-linux-gnu"

define void @ex1(float* %A, float* %B, float %K, i32 %start, i32 %end) nounwind uwtable ssp {
  %1 = alloca float*, align 8
  %2 = alloca float*, align 8
  %3 = alloca float, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %i = alloca i32, align 4
  store float* %A, float** %1, align 8
  store float* %B, float** %2, align 8
  store float %K, float* %3, align 4
  store i32 %start, i32* %4, align 4
  store i32 %end, i32* %5, align 4
  %6 = load i32* %4, align 4
  store i32 %6, i32* %i, align 4
  br label %7

; <label>:7                                       ; preds = %25, %0
  %8 = load i32* %i, align 4
  %9 = load i32* %5, align 4
  %10 = icmp slt i32 %8, %9
  br i1 %10, label %11, label %28

; <label>:11                                      ; preds = %7
  %12 = load i32* %i, align 4
  %13 = sext i32 %12 to i64
  %14 = load float** %2, align 8
  %15 = getelementptr inbounds float* %14, i64 %13
  %16 = load float* %15, align 4
  %17 = load float* %3, align 4
  %18 = fadd float %16, %17
  %19 = load i32* %i, align 4
  %20 = sext i32 %19 to i64
  %21 = load float** %1, align 8
  %22 = getelementptr inbounds float* %21, i64 %20
  %23 = load float* %22, align 4
  %24 = fmul float %23, %18
  store float %24, float* %22, align 4
  br label %25

; <label>:25                                      ; preds = %11
  %26 = load i32* %i, align 4
  %27 = add nsw i32 %26, 1
  store i32 %27, i32* %i, align 4
  br label %7

; <label>:28                                      ; preds = %7
  ret void
}

define void @ex2(float* %A, float* %B, float %K, i32 %n) nounwind uwtable ssp {
  %1 = alloca float*, align 8
  %2 = alloca float*, align 8
  %3 = alloca float, align 4
  %4 = alloca i32, align 4
  %i = alloca i32, align 4
  store float* %A, float** %1, align 8
  store float* %B, float** %2, align 8
  store float %K, float* %3, align 4
  store i32 %n, i32* %4, align 4
  store i32 0, i32* %i, align 4
  br label %5

; <label>:5                                       ; preds = %23, %0
  %6 = load i32* %i, align 4
  %7 = load i32* %4, align 4
  %8 = icmp slt i32 %6, %7
  br i1 %8, label %9, label %26

; <label>:9                                       ; preds = %5
  %10 = load i32* %i, align 4
  %11 = sext i32 %10 to i64
  %12 = load float** %2, align 8
  %13 = getelementptr inbounds float* %12, i64 %11
  %14 = load float* %13, align 4
  %15 = load float* %3, align 4
  %16 = fadd float %14, %15
  %17 = load i32* %i, align 4
  %18 = sext i32 %17 to i64
  %19 = load float** %1, align 8
  %20 = getelementptr inbounds float* %19, i64 %18
  %21 = load float* %20, align 4
  %22 = fmul float %21, %16
  store float %22, float* %20, align 4
  br label %23

; <label>:23                                      ; preds = %9
  %24 = load i32* %i, align 4
  %25 = add nsw i32 %24, 1
  store i32 %25, i32* %i, align 4
  br label %5

; <label>:26                                      ; preds = %5
  ret void
}

define i32 @ex3(i32* %A, i32* %B, i32 %n) nounwind uwtable ssp {
  %1 = alloca i32*, align 8
  %2 = alloca i32*, align 8
  %3 = alloca i32, align 4
  %sum = alloca i32, align 4
  %i = alloca i32, align 4
  store i32* %A, i32** %1, align 8
  store i32* %B, i32** %2, align 8
  store i32 %n, i32* %3, align 4
  store i32 0, i32* %sum, align 4
  store i32 0, i32* %i, align 4
  br label %4

; <label>:4                                       ; preds = %17, %0
  %5 = load i32* %i, align 4
  %6 = load i32* %3, align 4
  %7 = icmp slt i32 %5, %6
  br i1 %7, label %8, label %20

; <label>:8                                       ; preds = %4
  %9 = load i32* %i, align 4
  %10 = sext i32 %9 to i64
  %11 = load i32** %1, align 8
  %12 = getelementptr inbounds i32* %11, i64 %10
  %13 = load i32* %12, align 4
  %14 = add nsw i32 %13, 5
  %15 = load i32* %sum, align 4
  %16 = add i32 %15, %14
  store i32 %16, i32* %sum, align 4
  br label %17

; <label>:17                                      ; preds = %8
  %18 = load i32* %i, align 4
  %19 = add nsw i32 %18, 1
  store i32 %19, i32* %i, align 4
  br label %4

; <label>:20                                      ; preds = %4
  %21 = load i32* %sum, align 4
  ret i32 %21
}

define void @ex4(float* %A, float* %B, float %K, i32 %n) nounwind uwtable ssp {
  %1 = alloca float*, align 8
  %2 = alloca float*, align 8
  %3 = alloca float, align 4
  %4 = alloca i32, align 4
  %i = alloca i32, align 4
  store float* %A, float** %1, align 8
  store float* %B, float** %2, align 8
  store float %K, float* %3, align 4
  store i32 %n, i32* %4, align 4
  store i32 0, i32* %i, align 4
  br label %5

; <label>:5                                       ; preds = %16, %0
  %6 = load i32* %i, align 4
  %7 = load i32* %4, align 4
  %8 = icmp slt i32 %6, %7
  br i1 %8, label %9, label %19

; <label>:9                                       ; preds = %5
  %10 = load i32* %i, align 4
  %11 = sitofp i32 %10 to float
  %12 = load i32* %i, align 4
  %13 = sext i32 %12 to i64
  %14 = load float** %1, align 8
  %15 = getelementptr inbounds float* %14, i64 %13
  store float %11, float* %15, align 4
  br label %16

; <label>:16                                      ; preds = %9
  %17 = load i32* %i, align 4
  %18 = add nsw i32 %17, 1
  store i32 %18, i32* %i, align 4
  br label %5

; <label>:19                                      ; preds = %5
  ret void
}

define i32 @ex5(i32* %A, i32* %B, i32 %n) nounwind uwtable ssp {
  %1 = alloca i32*, align 8
  %2 = alloca i32*, align 8
  %3 = alloca i32, align 4
  %sum = alloca i32, align 4
  %i = alloca i32, align 4
  store i32* %A, i32** %1, align 8
  store i32* %B, i32** %2, align 8
  store i32 %n, i32* %3, align 4
  store i32 0, i32* %sum, align 4
  store i32 0, i32* %i, align 4
  br label %4

; <label>:4                                       ; preds = %30, %0
  %5 = load i32* %i, align 4
  %6 = load i32* %3, align 4
  %7 = icmp slt i32 %5, %6
  br i1 %7, label %8, label %33

; <label>:8                                       ; preds = %4
  %9 = load i32* %i, align 4
  %10 = sext i32 %9 to i64
  %11 = load i32** %1, align 8
  %12 = getelementptr inbounds i32* %11, i64 %10
  %13 = load i32* %12, align 4
  %14 = load i32* %i, align 4
  %15 = sext i32 %14 to i64
  %16 = load i32** %2, align 8
  %17 = getelementptr inbounds i32* %16, i64 %15
  %18 = load i32* %17, align 4
  %19 = icmp sgt i32 %13, %18
  br i1 %19, label %20, label %29

; <label>:20                                      ; preds = %8
  %21 = load i32* %i, align 4
  %22 = sext i32 %21 to i64
  %23 = load i32** %1, align 8
  %24 = getelementptr inbounds i32* %23, i64 %22
  %25 = load i32* %24, align 4
  %26 = add nsw i32 %25, 5
  %27 = load i32* %sum, align 4
  %28 = add i32 %27, %26
  store i32 %28, i32* %sum, align 4
  br label %29

; <label>:29                                      ; preds = %20, %8
  br label %30

; <label>:30                                      ; preds = %29
  %31 = load i32* %i, align 4
  %32 = add nsw i32 %31, 1
  store i32 %32, i32* %i, align 4
  br label %4

; <label>:33                                      ; preds = %4
  %34 = load i32* %sum, align 4
  ret i32 %34
}

define void @ex6(i32* %A, i32* %B, i32 %n) nounwind uwtable ssp {
  %1 = alloca i32*, align 8
  %2 = alloca i32*, align 8
  %3 = alloca i32, align 4
  %i = alloca i32, align 4
  store i32* %A, i32** %1, align 8
  store i32* %B, i32** %2, align 8
  store i32 %n, i32* %3, align 4
  %4 = load i32* %3, align 4
  store i32 %4, i32* %i, align 4
  br label %5

; <label>:5                                       ; preds = %15, %0
  %6 = load i32* %i, align 4
  %7 = icmp sgt i32 %6, 0
  br i1 %7, label %8, label %18

; <label>:8                                       ; preds = %5
  %9 = load i32* %i, align 4
  %10 = sext i32 %9 to i64
  %11 = load i32** %1, align 8
  %12 = getelementptr inbounds i32* %11, i64 %10
  %13 = load i32* %12, align 4
  %14 = add nsw i32 %13, 1
  store i32 %14, i32* %12, align 4
  br label %15

; <label>:15                                      ; preds = %8
  %16 = load i32* %i, align 4
  %17 = add nsw i32 %16, -1
  store i32 %17, i32* %i, align 4
  br label %5

; <label>:18                                      ; preds = %5
  ret void
}

define void @ex7(i32* %A, i32* %B, i32 %n, i32 %k) nounwind uwtable ssp {
  %1 = alloca i32*, align 8
  %2 = alloca i32*, align 8
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %i = alloca i32, align 4
  store i32* %A, i32** %1, align 8
  store i32* %B, i32** %2, align 8
  store i32 %n, i32* %3, align 4
  store i32 %k, i32* %4, align 4
  store i32 0, i32* %i, align 4
  br label %5

; <label>:5                                       ; preds = %24, %0
  %6 = load i32* %i, align 4
  %7 = load i32* %3, align 4
  %8 = icmp slt i32 %6, %7
  br i1 %8, label %9, label %27

; <label>:9                                       ; preds = %5
  %10 = load i32* %i, align 4
  %11 = load i32* %4, align 4
  %12 = mul nsw i32 %10, %11
  %13 = sext i32 %12 to i64
  %14 = load i32** %2, align 8
  %15 = getelementptr inbounds i32* %14, i64 %13
  %16 = load i32* %15, align 4
  %17 = load i32* %i, align 4
  %18 = mul nsw i32 %17, 7
  %19 = sext i32 %18 to i64
  %20 = load i32** %1, align 8
  %21 = getelementptr inbounds i32* %20, i64 %19
  %22 = load i32* %21, align 4
  %23 = add nsw i32 %22, %16
  store i32 %23, i32* %21, align 4
  br label %24

; <label>:24                                      ; preds = %9
  %25 = load i32* %i, align 4
  %26 = add nsw i32 %25, 1
  store i32 %26, i32* %i, align 4
  br label %5

; <label>:27                                      ; preds = %5
  ret void
}

define void @ex8(i32* %A, i8* %B, i32 %n, i32 %k) nounwind uwtable ssp {
  %1 = alloca i32*, align 8
  %2 = alloca i8*, align 8
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %i = alloca i32, align 4
  store i32* %A, i32** %1, align 8
  store i8* %B, i8** %2, align 8
  store i32 %n, i32* %3, align 4
  store i32 %k, i32* %4, align 4
  store i32 0, i32* %i, align 4
  br label %5

; <label>:5                                       ; preds = %23, %0
  %6 = load i32* %i, align 4
  %7 = load i32* %3, align 4
  %8 = icmp slt i32 %6, %7
  br i1 %8, label %9, label %26

; <label>:9                                       ; preds = %5
  %10 = load i32* %i, align 4
  %11 = sext i32 %10 to i64
  %12 = load i8** %2, align 8
  %13 = getelementptr inbounds i8* %12, i64 %11
  %14 = load i8* %13, align 1
  %15 = sext i8 %14 to i32
  %16 = mul nsw i32 4, %15
  %17 = load i32* %i, align 4
  %18 = sext i32 %17 to i64
  %19 = load i32** %1, align 8
  %20 = getelementptr inbounds i32* %19, i64 %18
  %21 = load i32* %20, align 4
  %22 = add nsw i32 %21, %16
  store i32 %22, i32* %20, align 4
  br label %23

; <label>:23                                      ; preds = %9
  %24 = load i32* %i, align 4
  %25 = add nsw i32 %24, 1
  store i32 %25, i32* %i, align 4
  br label %5

; <label>:26                                      ; preds = %5
  ret void
}
