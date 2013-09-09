; ModuleID = 'udivmod64_x86_64.bc'
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"

%struct.div_state_ = type { i64, i64 }

define i64 @udivmod64(i64 %dividend, i64 %divisor, i64* %remainder) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = alloca i64*, align 8
  %state = alloca %struct.div_state_, align 8
  %quotient = alloca i64, align 8
  %i = alloca i32, align 4
  %skipahead = alloca i32, align 4
  store i64 %dividend, i64* %2, align 8
  store i64 %divisor, i64* %3, align 8
  store i64* %remainder, i64** %4, align 8
  %5 = getelementptr inbounds %struct.div_state_* %state, i32 0, i32 0
  store i64 0, i64* %5, align 8
  %6 = getelementptr inbounds %struct.div_state_* %state, i32 0, i32 1
  %7 = load i64* %2, align 8
  store i64 %7, i64* %6, align 8
  store i64 0, i64* %quotient, align 8
  %8 = load i64* %3, align 8
  %9 = icmp eq i64 %8, 0
  br i1 %9, label %10, label %11

; <label>:10                                      ; preds = %0
  store i64 0, i64* %1
  br label %57

; <label>:11                                      ; preds = %0
  %12 = load i64* %2, align 8
  %13 = call i32 @clz64(i64 %12)
  store i32 %13, i32* %skipahead, align 4
  store i32 0, i32* %i, align 4
  br label %14

; <label>:14                                      ; preds = %19, %11
  %15 = load i32* %i, align 4
  %16 = load i32* %skipahead, align 4
  %17 = icmp slt i32 %15, %16
  br i1 %17, label %18, label %22

; <label>:18                                      ; preds = %14
  call void @div_state_lshift(%struct.div_state_* %state)
  br label %19

; <label>:19                                      ; preds = %18
  %20 = load i32* %i, align 4
  %21 = add nsw i32 %20, 1
  store i32 %21, i32* %i, align 4
  br label %14

; <label>:22                                      ; preds = %14
  %23 = load i32* %skipahead, align 4
  store i32 %23, i32* %i, align 4
  br label %24

; <label>:24                                      ; preds = %45, %22
  %25 = load i32* %i, align 4
  %26 = icmp slt i32 %25, 64
  br i1 %26, label %27, label %48

; <label>:27                                      ; preds = %24
  call void @div_state_lshift(%struct.div_state_* %state)
  %28 = getelementptr inbounds %struct.div_state_* %state, i32 0, i32 0
  %29 = load i64* %28, align 8
  %30 = load i64* %3, align 8
  %31 = icmp uge i64 %29, %30
  br i1 %31, label %32, label %44

; <label>:32                                      ; preds = %27
  %33 = getelementptr inbounds %struct.div_state_* %state, i32 0, i32 0
  %34 = load i64* %33, align 8
  %35 = load i64* %3, align 8
  %36 = sub i64 %34, %35
  %37 = getelementptr inbounds %struct.div_state_* %state, i32 0, i32 0
  store i64 %36, i64* %37, align 8
  %38 = load i32* %i, align 4
  %39 = sub nsw i32 63, %38
  %40 = zext i32 %39 to i64
  %41 = shl i64 1, %40
  %42 = load i64* %quotient, align 8
  %43 = or i64 %42, %41
  store i64 %43, i64* %quotient, align 8
  br label %44

; <label>:44                                      ; preds = %32, %27
  br label %45

; <label>:45                                      ; preds = %44
  %46 = load i32* %i, align 4
  %47 = add nsw i32 %46, 1
  store i32 %47, i32* %i, align 4
  br label %24

; <label>:48                                      ; preds = %24
  %49 = load i64** %4, align 8
  %50 = icmp ne i64* %49, null
  br i1 %50, label %51, label %55

; <label>:51                                      ; preds = %48
  %52 = getelementptr inbounds %struct.div_state_* %state, i32 0, i32 0
  %53 = load i64* %52, align 8
  %54 = load i64** %4, align 8
  store i64 %53, i64* %54, align 8
  br label %55

; <label>:55                                      ; preds = %51, %48
  %56 = load i64* %quotient, align 8
  store i64 %56, i64* %1
  br label %57

; <label>:57                                      ; preds = %55, %10
  %58 = load i64* %1
  ret i64 %58
}

define internal i32 @clz64(i64 %x) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %total_bits = alloca i32, align 4
  %zc = alloca i32, align 4
  store i64 %x, i64* %1, align 8
  store i32 64, i32* %total_bits, align 4
  store i32 0, i32* %zc, align 4
  br label %2

; <label>:2                                       ; preds = %16, %0
  %3 = load i32* %zc, align 4
  %4 = icmp slt i32 %3, 64
  br i1 %4, label %5, label %14

; <label>:5                                       ; preds = %2
  %6 = load i64* %1, align 8
  %7 = load i32* %zc, align 4
  %8 = sub nsw i32 64, %7
  %9 = sub nsw i32 %8, 1
  %10 = zext i32 %9 to i64
  %11 = lshr i64 %6, %10
  %12 = and i64 %11, 1
  %13 = icmp eq i64 %12, 0
  br label %14

; <label>:14                                      ; preds = %5, %2
  %15 = phi i1 [ false, %2 ], [ %13, %5 ]
  br i1 %15, label %16, label %19

; <label>:16                                      ; preds = %14
  %17 = load i32* %zc, align 4
  %18 = add nsw i32 %17, 1
  store i32 %18, i32* %zc, align 4
  br label %2

; <label>:19                                      ; preds = %14
  %20 = load i32* %zc, align 4
  ret i32 %20
}

define internal void @div_state_lshift(%struct.div_state_* %state) nounwind uwtable ssp {
  %1 = alloca %struct.div_state_*, align 8
  store %struct.div_state_* %state, %struct.div_state_** %1, align 8
  %2 = load %struct.div_state_** %1, align 8
  %3 = getelementptr inbounds %struct.div_state_* %2, i32 0, i32 0
  %4 = load i64* %3, align 8
  %5 = shl i64 %4, 1
  %6 = load %struct.div_state_** %1, align 8
  %7 = getelementptr inbounds %struct.div_state_* %6, i32 0, i32 1
  %8 = load i64* %7, align 8
  %9 = lshr i64 %8, 63
  %10 = or i64 %5, %9
  %11 = load %struct.div_state_** %1, align 8
  %12 = getelementptr inbounds %struct.div_state_* %11, i32 0, i32 0
  store i64 %10, i64* %12, align 8
  %13 = load %struct.div_state_** %1, align 8
  %14 = getelementptr inbounds %struct.div_state_* %13, i32 0, i32 1
  %15 = load i64* %14, align 8
  %16 = shl i64 %15, 1
  %17 = load %struct.div_state_** %1, align 8
  %18 = getelementptr inbounds %struct.div_state_* %17, i32 0, i32 1
  store i64 %16, i64* %18, align 8
  ret void
}

define i64 @sdivmod64(i64 %dividend, i64 %divisor, i64* %remainder) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %2 = alloca i64, align 8
  %3 = alloca i64*, align 8
  %signbitidx = alloca i32, align 4
  %signed_dividend = alloca i32, align 4
  %signed_divisor = alloca i32, align 4
  %signed_result = alloca i32, align 4
  %quotient = alloca i64, align 8
  %udvd = alloca i64, align 8
  %udvr = alloca i64, align 8
  %uquotient = alloca i64, align 8
  %uremainder = alloca i64, align 8
  store i64 %dividend, i64* %1, align 8
  store i64 %divisor, i64* %2, align 8
  store i64* %remainder, i64** %3, align 8
  store i32 63, i32* %signbitidx, align 4
  %4 = load i64* %1, align 8
  %5 = icmp slt i64 %4, 0
  %6 = zext i1 %5 to i32
  store i32 %6, i32* %signed_dividend, align 4
  %7 = load i64* %2, align 8
  %8 = icmp slt i64 %7, 0
  %9 = zext i1 %8 to i32
  store i32 %9, i32* %signed_divisor, align 4
  %10 = load i32* %signed_divisor, align 4
  %11 = load i32* %signed_dividend, align 4
  %12 = xor i32 %10, %11
  store i32 %12, i32* %signed_result, align 4
  %13 = load i32* %signed_dividend, align 4
  %14 = icmp ne i32 %13, 0
  br i1 %14, label %15, label %18

; <label>:15                                      ; preds = %0
  %16 = load i64* %1, align 8
  %17 = sub nsw i64 0, %16
  br label %20

; <label>:18                                      ; preds = %0
  %19 = load i64* %1, align 8
  br label %20

; <label>:20                                      ; preds = %18, %15
  %21 = phi i64 [ %17, %15 ], [ %19, %18 ]
  store i64 %21, i64* %udvd, align 8
  %22 = load i32* %signed_divisor, align 4
  %23 = icmp ne i32 %22, 0
  br i1 %23, label %24, label %27

; <label>:24                                      ; preds = %20
  %25 = load i64* %2, align 8
  %26 = sub nsw i64 0, %25
  br label %29

; <label>:27                                      ; preds = %20
  %28 = load i64* %2, align 8
  br label %29

; <label>:29                                      ; preds = %27, %24
  %30 = phi i64 [ %26, %24 ], [ %28, %27 ]
  store i64 %30, i64* %udvr, align 8
  %31 = load i64* %udvd, align 8
  %32 = load i64* %udvr, align 8
  %33 = call i64 @udivmod64(i64 %31, i64 %32, i64* %uremainder)
  store i64 %33, i64* %uquotient, align 8
  %34 = load i32* %signed_result, align 4
  %35 = icmp ne i32 %34, 0
  br i1 %35, label %36, label %57

; <label>:36                                      ; preds = %29
  %37 = load i64* %uremainder, align 8
  %38 = icmp ne i64 %37, 0
  br i1 %38, label %39, label %43

; <label>:39                                      ; preds = %36
  %40 = load i64* %uquotient, align 8
  %41 = sub nsw i64 0, %40
  %42 = sub nsw i64 %41, 1
  store i64 %42, i64* %quotient, align 8
  br label %46

; <label>:43                                      ; preds = %36
  %44 = load i64* %uquotient, align 8
  %45 = sub nsw i64 0, %44
  store i64 %45, i64* %quotient, align 8
  br label %46

; <label>:46                                      ; preds = %43, %39
  %47 = load i64** %3, align 8
  %48 = icmp ne i64* %47, null
  br i1 %48, label %49, label %56

; <label>:49                                      ; preds = %46
  %50 = load i64* %1, align 8
  %51 = load i64* %quotient, align 8
  %52 = load i64* %2, align 8
  %53 = mul i64 %51, %52
  %54 = sub i64 %50, %53
  %55 = load i64** %3, align 8
  store i64 %54, i64* %55, align 8
  br label %56

; <label>:56                                      ; preds = %49, %46
  br label %73

; <label>:57                                      ; preds = %29
  %58 = load i64* %uquotient, align 8
  store i64 %58, i64* %quotient, align 8
  %59 = load i64** %3, align 8
  %60 = icmp ne i64* %59, null
  br i1 %60, label %61, label %72

; <label>:61                                      ; preds = %57
  %62 = load i32* %signed_divisor, align 4
  %63 = icmp ne i32 %62, 0
  br i1 %63, label %64, label %67

; <label>:64                                      ; preds = %61
  %65 = load i64* %uremainder, align 8
  %66 = sub i64 0, %65
  br label %69

; <label>:67                                      ; preds = %61
  %68 = load i64* %uremainder, align 8
  br label %69

; <label>:69                                      ; preds = %67, %64
  %70 = phi i64 [ %66, %64 ], [ %68, %67 ]
  %71 = load i64** %3, align 8
  store i64 %70, i64* %71, align 8
  br label %72

; <label>:72                                      ; preds = %69, %57
  br label %73

; <label>:73                                      ; preds = %72, %56
  %74 = load i64* %quotient, align 8
  ret i64 %74
}

define i64 @udiv64(i64 %dividend, i64 %divisor) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %2 = alloca i64, align 8
  store i64 %dividend, i64* %1, align 8
  store i64 %divisor, i64* %2, align 8
  %3 = load i64* %1, align 8
  %4 = load i64* %2, align 8
  %5 = call i64 @udivmod64(i64 %3, i64 %4, i64* null)
  ret i64 %5
}

define i64 @sdiv64(i64 %dividend, i64 %divisor) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %2 = alloca i64, align 8
  store i64 %dividend, i64* %1, align 8
  store i64 %divisor, i64* %2, align 8
  %3 = load i64* %1, align 8
  %4 = load i64* %2, align 8
  %5 = call i64 @sdivmod64(i64 %3, i64 %4, i64* null)
  ret i64 %5
}

define i64 @umod64(i64 %dividend, i64 %divisor) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %2 = alloca i64, align 8
  %rem = alloca i64, align 8
  store i64 %dividend, i64* %1, align 8
  store i64 %divisor, i64* %2, align 8
  %3 = load i64* %1, align 8
  %4 = load i64* %2, align 8
  %5 = call i64 @udivmod64(i64 %3, i64 %4, i64* %rem)
  %6 = load i64* %rem, align 8
  ret i64 %6
}

define i64 @smod64(i64 %dividend, i64 %divisor) nounwind uwtable ssp {
  %1 = alloca i64, align 8
  %2 = alloca i64, align 8
  %rem = alloca i64, align 8
  store i64 %dividend, i64* %1, align 8
  store i64 %divisor, i64* %2, align 8
  %3 = load i64* %1, align 8
  %4 = load i64* %2, align 8
  %5 = call i64 @sdivmod64(i64 %3, i64 %4, i64* %rem)
  %6 = load i64* %rem, align 8
  ret i64 %6
}
