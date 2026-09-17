```bash
gcc -O3 -mavx512f -mfma main.c fma_test.S -o fma_test
```

main.c
```
#include <stdint.h>
#include <stdio.h>
#include <x86intrin.h>

extern uint64_t fma_only_tpt(uint64_t loops);
extern uint64_t fma_shuffle_tpt(uint64_t loops);

int main(void)
{
    uint64_t fma_shuf[3];
    uint64_t fma_only[3];

    fma_only_tpt(100000);

    for (int i = 0; i < 3; ++i) {
        uint64_t start = __rdtsc();
        fma_shuffle_tpt(1000);
        fma_shuf[i] = __rdtsc() - start;
    }

    for (int i = 0; i < 3; ++i) {
        uint64_t start = __rdtsc();
        fma_only_tpt(1000);
        fma_only[i] = __rdtsc() - start;
    }

    uint64_t shuf_min = fma_shuf[0];
    uint64_t only_min = fma_only[0];

    for (int i = 1; i < 3; ++i) {
        if (fma_shuf[i] < shuf_min)
            shuf_min = fma_shuf[i];

        if (fma_only[i] < only_min)
            only_min = fma_only[i];
    }

    printf("FMA+shuffle: %lu cycles\n", shuf_min);
    printf("FMA only:    %lu cycles\n", only_min);
    printf("ratio:       %.3f\n",
           (double)shuf_min / (double)only_min);

    printf("%d FMA server\n",
           ((double)shuf_min / (double)only_min < 1.5) ? 1 : 2);

    return 0;
}
```

fma_test.S
```c
.intel_syntax noprefix

.text

.p2align 4
.globl fma_only_tpt
.type fma_only_tpt, @function

fma_only_tpt:
    vmovapd zmm0,  [rip + one_vec]
    vmovapd zmm1,  [rip + one_vec]
    vmovapd zmm2,  [rip + one_vec]
    vmovapd zmm3,  [rip + one_vec]
    vmovapd zmm4,  [rip + one_vec]
    vmovapd zmm5,  [rip + one_vec]
    vmovapd zmm6,  [rip + one_vec]
    vmovapd zmm7,  [rip + one_vec]
    vmovapd zmm8,  [rip + one_vec]
    vmovapd zmm9,  [rip + one_vec]
    vmovapd zmm10, [rip + one_vec]
    vmovapd zmm11, [rip + one_vec]

    mov rax, rdi

.Lfma_loop:
    vfmadd231pd zmm0,  zmm0,  zmm0
    vfmadd231pd zmm1,  zmm1,  zmm1
    vfmadd231pd zmm2,  zmm2,  zmm2
    vfmadd231pd zmm3,  zmm3,  zmm3
    vfmadd231pd zmm4,  zmm4,  zmm4
    vfmadd231pd zmm5,  zmm5,  zmm5
    vfmadd231pd zmm6,  zmm6,  zmm6
    vfmadd231pd zmm7,  zmm7,  zmm7
    vfmadd231pd zmm8,  zmm8,  zmm8
    vfmadd231pd zmm9,  zmm9,  zmm9
    vfmadd231pd zmm10, zmm10, zmm10
    vfmadd231pd zmm11, zmm11, zmm11

    dec rax
    jnz .Lfma_loop

    vzeroupper
    ret

.Lfma_only_end:
.size fma_only_tpt, .Lfma_only_end - fma_only_tpt


.p2align 4
.globl fma_shuffle_tpt
.type fma_shuffle_tpt, @function

fma_shuffle_tpt:
    vmovapd zmm0,  [rip + one_vec]
    vmovapd zmm1,  [rip + one_vec]
    vmovapd zmm2,  [rip + one_vec]
    vmovapd zmm3,  [rip + one_vec]
    vmovapd zmm4,  [rip + one_vec]
    vmovapd zmm5,  [rip + one_vec]
    vmovapd zmm6,  [rip + one_vec]
    vmovapd zmm7,  [rip + one_vec]
    vmovapd zmm8,  [rip + one_vec]
    vmovapd zmm9,  [rip + one_vec]
    vmovapd zmm10, [rip + one_vec]
    vmovapd zmm11, [rip + one_vec]

    vmovdqa32 zmm30, [rip + shuf_vec]

    mov rax, rdi

.Lfma_shuffle_loop:
    vfmadd231pd zmm0,  zmm0,  zmm0
    vfmadd231pd zmm1,  zmm1,  zmm1
    vfmadd231pd zmm2,  zmm2,  zmm2
    vfmadd231pd zmm3,  zmm3,  zmm3
    vfmadd231pd zmm4,  zmm4,  zmm4
    vfmadd231pd zmm5,  zmm5,  zmm5
    vfmadd231pd zmm6,  zmm6,  zmm6
    vfmadd231pd zmm7,  zmm7,  zmm7
    vfmadd231pd zmm8,  zmm8,  zmm8
    vfmadd231pd zmm9,  zmm9,  zmm9
    vfmadd231pd zmm10, zmm10, zmm10
    vfmadd231pd zmm11, zmm11, zmm11

    vpermd zmm12, zmm30, zmm30
    vpermd zmm13, zmm30, zmm30
    vpermd zmm14, zmm30, zmm30
    vpermd zmm15, zmm30, zmm30
    vpermd zmm16, zmm30, zmm30
    vpermd zmm17, zmm30, zmm30
    vpermd zmm18, zmm30, zmm30
    vpermd zmm19, zmm30, zmm30
    vpermd zmm20, zmm30, zmm30
    vpermd zmm21, zmm30, zmm30
    vpermd zmm22, zmm30, zmm30
    vpermd zmm23, zmm30, zmm30

    dec rax
    jnz .Lfma_shuffle_loop

    vzeroupper
    ret

.Lfma_shuffle_end:
.size fma_shuffle_tpt, .Lfma_shuffle_end - fma_shuffle_tpt


.section .rodata
.p2align 6

one_vec:
    .double 1.0, 1.0, 1.0, 1.0
    .double 1.0, 1.0, 1.0, 1.0

.p2align 6

shuf_vec:
    .long 0, 1, 2, 3
    .long 4, 5, 6, 7
    .long 8, 9, 10, 11
    .long 12, 13, 14, 15

.section .note.GNU-stack,"",@progbits
```

```bash
fma_test
```

Tiger Lake
```text
FMA+shuffle: 22418 cycles
FMA only:    22453 cycles
ratio:       0.998
1 FMA server
```

Granite Rapids
```text
FMA+shuffle: 8066 cycles
FMA only: 4054 cycles
ratio: 1.990
2 FMA server
```

Ice Lake-SP
```text
FMA+shuffle: 10536 cycles
FMA only:    5286 cycles
ratio:       1.993
2 FMA server
```
***
The key is that the assembly deliberately creates **12 independent FMA chains**, and the second test adds **12 `VPERMD` instructions**. Let's walk through the assembly piece by piece.

## 1. Function entry and calling convention

Your function starts approximately like this:

```asm
.intel_syntax noprefix

.text
.globl fma_only_tpt
.type fma_only_tpt, @function

fma_only_tpt:
```

`fma_only_tpt` is callable from C:

```c
extern uint64_t fma_only_tpt(uint64_t loops);
```

On Linux x86-64 using the System V ABI, the first integer argument arrives in:

```text
RDI = loop count
```

So:

```asm
mov rax, rdi
```

copies the loop count into `RAX`.

We use `RAX` as the loop counter because we don't want to overwrite `RDI` unnecessarily.

---

# 2. Loading the FMA accumulators

You have:

```asm
vmovapd zmm0,  [rip + one_vec]
vmovapd zmm1,  [rip + one_vec]
...
vmovapd zmm11, [rip + one_vec]
```

`one_vec` contains:

```asm
one_vec:
    .double 1.0, 1.0, 1.0, 1.0
    .double 1.0, 1.0, 1.0, 1.0
```

A ZMM register is 512 bits:

```text
512 bits / 64 bits = 8 doubles
```

Therefore each register contains:

```text
zmm0 = [1,1,1,1,1,1,1,1]
zmm1 = [1,1,1,1,1,1,1,1]
...
zmm11 = [1,1,1,1,1,1,1,1]
```

You have **12 independent accumulator registers**.

That's very important.

---

# 3. The FMA instruction

The core instruction is:

```asm
vfmadd231pd zmm0, zmm0, zmm0
```

The Intel syntax for:

```asm
vfmadd231pd dest, src1, src2
```

means:

```text
dest = src1 * src2 + dest
```

Therefore:

```asm
vfmadd231pd zmm0, zmm0, zmm0
```

does:

```text
zmm0 = zmm0 * zmm0 + zmm0
```

For each of the 8 double elements:

```text
x = x*x + x
```

So if initially:

```text
x = 1
```

then:

```text
1 → 2 → 6 → 42 → ...
```

The actual numerical value doesn't matter for this benchmark. What matters is that each FMA is a real vector FMA instruction.

You repeat it for:

```asm
zmm0
zmm1
zmm2
...
zmm11
```

giving:

```text
12 vector FMA instructions / loop iteration
```

Each vector FMA operates on:

```text
8 doubles
```

so architecturally that's:

```text
12 × 8 = 96 scalar FP operations
```

per loop iteration.

And because an FMA counts as two floating-point operations:

```text
96 × 2 = 192 FLOPs
```

per iteration.

---

# 4. Why 12 independent ZMM registers?

This is probably the most important part of the benchmark.

Consider this:

```asm
vfmadd231pd zmm0, zmm0, zmm0
vfmadd231pd zmm0, zmm0, zmm0
vfmadd231pd zmm0, zmm0, zmm0
```

There is a dependency:

```text
FMA
 ↓
zmm0
 ↓
FMA
 ↓
zmm0
 ↓
FMA
```

The processor can't execute the second FMA until the first produces its result.

Instead you have:

```text
zmm0 → FMA ─┐
zmm1 → FMA  │
zmm2 → FMA  │
zmm3 → FMA  │
zmm4 → FMA  │
zmm5 → FMA  │
zmm6 → FMA  │
zmm7 → FMA  ├──> execution engine
zmm8 → FMA  │
zmm9 → FMA  │
zmm10 → FMA │
zmm11 → FMA ┘
```

These are independent.

That gives the CPU's out-of-order scheduler enough work to keep multiple FMA execution units busy.

---

# 5. The loop

The loop is:

```asm
.Lfma_loop:
    vfmadd231pd zmm0,  zmm0,  zmm0
    vfmadd231pd zmm1,  zmm1,  zmm1
    ...
    vfmadd231pd zmm11, zmm11, zmm11

    dec rax
    jnz .Lfma_loop
```

Each iteration contains:

```text
12 × VFMADD231PD
1 × DEC
1 × JNZ
```

The `DEC/JNZ` overhead is tiny compared with the 12 vector FMAs.

---

# 6. Why the FMA-only test measures FMA throughput

Your Ice Lake result:

```text
5286 cycles / 1000 iterations
≈ 5.286 cycles/iteration
```

There are 12 FMAs per iteration:

```text
12 / 5.286
≈ 2.27 FMA instructions/cycle
```

That's consistent with a processor capable of sustaining roughly two 512-bit FMA instructions per cycle, with the exact result affected by loop/control overhead, measurement overhead, CPU frequency behavior, etc.

In other words, the benchmark is successfully putting substantial pressure on the FMA execution resources.

---

# 7. Now the shuffle version

The second function first does the same thing:

```asm
vmovapd zmm0,  [rip + one_vec]
...
vmovapd zmm11, [rip + one_vec]
```

Then:

```asm
vmovdqa32 zmm30, [rip + shuf_vec]
```

The data is:

```asm
shuf_vec:
    .long 0, 1, 2, 3
    .long 4, 5, 6, 7
    .long 8, 9, 10, 11
    .long 12, 13, 14, 15
```

So:

```text
zmm30 =
[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
```

These are **16 × 32-bit integers**.

That's because `VPERMD` works on 32-bit integer elements.

---

# 8. `VPERMD`

The shuffle instructions are:

```asm
vpermd zmm12, zmm30, zmm30
vpermd zmm13, zmm30, zmm30
...
vpermd zmm23, zmm30, zmm30
```

Intel syntax is:

```text
VPERMD destination, index, source
```

Conceptually:

```c
dest[i] = source[index[i]]
```

So:

```asm
vpermd zmm12, zmm30, zmm30
```

means:

```text
zmm12[i] = zmm30[zmm30[i]]
```

Because `zmm30` contains:

```text
0,1,2,3,...,15
```

the result is:

```text
0,1,2,3,...,15
```

So yes, this particular permutation is an **identity permutation**.

That's okay for your particular throughput test because you're interested in the execution resources consumed by `VPERMD`, rather than the mathematical transformation.

---

# 9. Why use 12 `VPERMD`s?

You have:

```asm
vpermd zmm12, zmm30, zmm30
vpermd zmm13, zmm30, zmm30
...
vpermd zmm23, zmm30, zmm30
```

That's another:

```text
12 vector instructions / iteration
```

So the combined loop contains:

```text
12 × FMA
12 × VPERMD
```

per iteration.

This creates a resource-contention experiment.

---

# 10. Why `zmm30` doesn't change

Notice:

```asm
vpermd zmm12, zmm30, zmm30
```

but `zmm30` itself isn't modified.

Therefore all 12 permutations are independent:

```text
             ┌── VPERMD → zmm12
zmm30 ───────┼── VPERMD → zmm13
             ├── VPERMD → zmm14
             ├── ...
             └── VPERMD → zmm23
```

The CPU can therefore have many of them in flight simultaneously.

That's important because you're measuring **throughput**, not latency.

---

# 11. Why the result doubles on Ice Lake

Your numbers:

```text
FMA only:
5286 cycles
```

versus:

```text
FMA + shuffle:
10536 cycles
```

The ratio:

```text
10536 / 5286 = 1.993
```

That's remarkably close to:

```text
2.0
```

So the additional `VPERMD` workload roughly doubles the time of the loop.

Your classifier consequently sees:

```c
if (ratio < 1.5)
    number_of_fma_units_per_core = 1;
```

Since:

```text
1.993 > 1.5
```

it leaves:

```text
number_of_fma_units_per_core = 2
```

and prints:

```text
2 FMA server
```

---

# 12. `dec` and `jnz`

At the end:

```asm
dec rax
jnz .Lfma_shuffle_loop
```

Suppose:

```text
RAX = 1000
```

The loop runs:

```text
1000
→ 999
→ 998
...
→ 1
→ 0
```

When `DEC` produces zero, it sets ZF, and:

```asm
jnz
```

doesn't jump.

So you get exactly 1000 iterations.

I prefer `jnz` here over the original `jg`.

Your original:

```asm
dec rdx
jg loop1
```

uses the signed condition "greater than zero."

For a loop counter that is conceptually unsigned, `jnz` is cleaner.

---

# 13. `vzeroupper`

At the end:

```asm
vzeroupper
ret
```

`vzeroupper` clears the upper portions of the YMM/ZMM state.

It's mainly there to avoid AVX → legacy SSE transition penalties when returning to ordinary code.

It isn't part of the measured loop because it occurs after the loop.

---

# 14. Why the two functions are useful together

Conceptually, you're doing:

### Test A

```text
                FMA resources
                    ↓
12 × VFMADD ────────────────→ time A
```

### Test B

```text
                FMA resources
                    ↓
12 × VFMADD ────────────────┐
                            ├──→ time B
12 × VPERMD ────────────────┘
                ↑
         shuffle resources
```

Then:

```text
ratio = time B / time A
```

Your two observed architectures give:

```text
1-FMA-server CPU:
    A ≈ B
    ratio ≈ 1

Ice Lake-SP:
    B ≈ 2A
    ratio ≈ 2

Granite Rapids:
    B ≈ 2A
    ratio ≈ 2
```

That's why your simple threshold:

```text
ratio < 1.5 → 1
ratio ≥ 1.5 → 2
```

separates the machines you've tested.

---

## One caveat about the assembly

There is one thing I would **not** claim from this benchmark alone: that `VPERMD` is literally occupying an FMA execution port. The benchmark demonstrates a very strong throughput signature, but the precise execution-port mechanism is microarchitecture-specific.

For Ice Lake-SP, the useful way to analyze this rigorously is to look at the documented/known execution-port mapping for:

```text
VFMADD231PD zmm,zmm,zmm
VPERMD zmm,zmm,zmm
```

and then connect that to your measured ~2× ratio.

Also, your `VPERMD` uses an identity index vector. If you want, I can show you **exactly which Ice Lake-SP execution ports these two instructions use, why 12+12 instructions produce the ~1.993 ratio, and how to modify the benchmark to prove the port contention rather than merely infer it from timing**.
