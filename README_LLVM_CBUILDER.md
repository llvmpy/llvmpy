LLVM CBuilder
=============

A few short examples:
(TODO: add more later)

```python
from llvm.core import *
from llvm_cbuilder import *
import llvm_cbuilder.shortnames as C
```

```python
class Square(CDefinition):
    _name_ = 'square'
    _retty_ = C.double
    _argtys_ = [ ('x', C.double) ]

    def body(self, x):
        y = x * x
        self.ret(y)
```

```python
m = Module.new('my_module')
llvm_square = Square()(m)
print(m)
```

```
; ModuleID = 'my_module'

define double @square(double %x) {
decl:
  %0 = fmul double %x, %x
  ret double %0
}
```


```python
class IsPrime(CDefinition):
    _name_ = 'isprime'
    _retty_ = C.int
    _argtys_ = [('x', C.int)]

    def body(self, x):
        false = zero = self.constant(C.int, 0)
        true = one = self.constant(C.int, 1)

        two = self.constant(C.int, 2)

        with self.ifelse( x <= two ) as ifelse:
            with ifelse.then():
                self.ret(true)

        with self.ifelse( (x % two) == zero ) as ifelse:
            with ifelse.then():
                self.ret(false)

        idx = self.var(C.int, 3, name='idx')

        with self.loop() as loop:
            with loop.condition() as setcond:
                setcond( idx < x )

            with loop.body():
                with self.ifelse( (x % idx ) == zero ) as ifelse:
                    with ifelse.then():
                        self.ret(false)
                idx += two

        self.ret(true)
```



```
define i32 @isprime(i32 %x) {
decl:
  %0 = icmp sle i32 %x, 2
  br i1 %0, label %if.then, label %if.end

if.then:                                          ; preds = %loop.body, %loop.cond, %if.end, %decl
  %merge = phi i32 [ 1, %decl ], [ 0, %if.end ], [ 1, %loop.cond ], [ 0, %loop.body ]
  ret i32 %merge

if.end:                                           ; preds = %decl
  %1 = srem i32 %x, 2
  %2 = icmp eq i32 %1, 0
  br i1 %2, label %if.then, label %if.end4

if.end4:                                          ; preds = %if.end
  br label %loop.cond

loop.cond:                                        ; preds = %if.end7, %if.end4
  %idx.0 = phi i32 [ 3, %if.end4 ], [ %6, %if.end7 ]
  %3 = icmp slt i32 %idx.0, %x
  br i1 %3, label %loop.body, label %if.then

loop.body:                                        ; preds = %loop.cond
  %4 = srem i32 %x, %idx.0
  %5 = icmp eq i32 %4, 0
  br i1 %5, label %if.then, label %if.end7

if.end7:                                          ; preds = %loop.body
  %6 = add i32 %idx.0, 2
  br label %loop.cond
}

; ModuleID = 'my_module'

define i32 @isprime(i32 %x) {
decl:
  %0 = icmp sle i32 %x, 2
  br i1 %0, label %if.then, label %if.end

if.then:                                          ; preds = %loop.body, %loop.cond, %if.end, %decl
  %merge = phi i32 [ 1, %decl ], [ 0, %if.end ], [ 1, %loop.cond ], [ 0, %loop.body ]
  ret i32 %merge

if.end:                                           ; preds = %decl
  %1 = srem i32 %x, 2
  %2 = icmp eq i32 %1, 0
  br i1 %2, label %if.then, label %if.end4

if.end4:                                          ; preds = %if.end
  br label %loop.cond

loop.cond:                                        ; preds = %if.end7, %if.end4
  %idx.0 = phi i32 [ 3, %if.end4 ], [ %6, %if.end7 ]
  %3 = icmp slt i32 %idx.0, %x
  br i1 %3, label %loop.body, label %if.then

loop.body:                                        ; preds = %loop.cond
  %4 = srem i32 %x, %idx.0
  %5 = icmp eq i32 %4, 0
  br i1 %5, label %if.then, label %if.end7

if.end7:                                          ; preds = %loop.body
  %6 = add i32 %idx.0, 2
  br label %loop.cond
}
```
