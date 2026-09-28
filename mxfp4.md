<details><summary>Benchmarks</summary>

### qwen3-4B on AVX2 (`zen3`)
Built with `GCC 14.2.0` on `Ubuntu 24.04`
***
### ik_llama.cpp
| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     26.37 ± 0.02 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |     10.53 ± 0.04 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     32.56 ± 0.08 |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |     10.91 ± 0.02 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     26.35 ± 0.01 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      8.94 ± 0.03 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         pp512 |     26.39 ± 0.06 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         tg128 |      4.62 ± 0.00 |
***
### ik_llama.cpp  (-rtr 1)
| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     31.13 ± 0.04 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     12.98 ± 0.10 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     39.56 ± 0.09 |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     12.87 ± 0.09 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     22.61 ± 0.02 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     11.82 ± 0.05 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     28.76 ± 0.06 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     11.34 ± 0.02 |
***
### llama.cpp
load_backend: loaded CPU backend from libggml-cpu-haswell.so
| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         21.50 ± 0.02 |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |         11.15 ± 0.04 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         24.39 ± 0.05 |
| qwen3 4B Q4_K - Medium         |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |         11.49 ± 0.07 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         21.51 ± 0.02 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |         11.02 ± 0.04 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           pp512 |         21.24 ± 0.06 |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           tg128 |         10.85 ± 0.03 |
</details>

### MXFP4 `zen3` Comparison

| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 26.39 | **28.76** | 21.24 |
| **tg128** | 4.62 | **11.34** | 10.85 |
***
<details><summary>Benchmarks</summary>

### qwen3-4B on AVX-512-VNNI (`Granite Rapids`)
Built with `GCC 14.2.0` on `Ubuntu 24.04`
***
### ik_llama.cpp
| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     58.73 ± 1.03 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      3.98 ± 0.03 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     56.85 ± 0.52 |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      4.42 ± 0.03 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     58.37 ± 0.61 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      3.50 ± 0.04 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         pp512 |     59.02 ± 0.43 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         tg128 |      2.93 ± 0.02 |
***
### ik_llama.cpp  (-rtr 1)
| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     65.16 ± 0.74 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     11.08 ± 0.07 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     48.45 ± 0.45 |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     11.04 ± 0.04 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     50.54 ± 0.93 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |      9.55 ± 0.04 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     58.66 ± 1.10 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     10.11 ± 0.08 |
***
### llama.cpp
load_backend: loaded CPU backend from libggml-cpu-icelake.so
| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         35.33 ± 0.23 |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |          8.13 ± 0.10 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         43.67 ± 0.26 |
| qwen3 4B Q4_K - Medium         |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |          8.90 ± 0.12 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         35.15 ± 0.61 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |          7.89 ± 0.05 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           pp512 |         34.45 ± 0.30 |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           tg128 |          7.38 ± 0.04 |
</details>

### MXFP4 `Granite Rapids` Comparison

| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 59.02 | **58.66** | 34.45 |
| **tg128** | 2.93 | **10.11** | 7.38 |
***
### qwen3-4B on AVX-512-VNNI (`Ice Lake`)
<details><summary>Benchmarks</summary>

Built with `GCC 13.3.0` on `Ubuntu 24.04`
### ik_llama.cpp
| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     45.65 ± 0.12 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      6.96 ± 0.05 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     46.45 ± 0.24 |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      7.62 ± 0.03 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     45.07 ± 0.23 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |      6.63 ± 0.04 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         pp512 |     47.49 ± 0.30 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         tg128 |      4.14 ± 0.01 |
***
### ik_llama.cpp  (-rtr 1)
| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     45.78 ± 0.22 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |      8.88 ± 0.02 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     37.60 ± 0.05 |
| qwen3 4B Q4_K - Medium         |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |      8.56 ± 0.04 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     31.71 ± 0.03 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |      8.05 ± 0.10 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     45.18 ± 0.16 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |      8.42 ± 0.05 |
***
### llama.cpp
load_backend: loaded CPU backend from libggml-cpu-icelake.so
| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         29.00 ± 0.03 |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |          7.66 ± 0.04 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_K - Medium         |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         29.27 ± 0.24 |
| qwen3 4B Q4_K - Medium         |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |          8.21 ± 0.04 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         29.01 ± 0.04 |
| qwen3 4B IQ4_NL - 4.5 bpw      |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |          7.69 ± 0.04 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           pp512 |         28.02 ± 0.12 |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           tg128 |          7.49 ± 0.05 |
</details>
  
* `llama.cpp` was built with `GNU 11.4.0`
### MXFP4 `Ice Lake` comparison with `GCC 12.4.0`
| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 48.61 | **46.41** | 28.36 |
| **tg128** | 4.20 | **8.54** | 7.84 |

### MXFP4 `Ice Lake` comparison with `GCC 13.3.0`
| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 47.49 | **45.18** | 28.02 |
| **tg128** | 4.14 | **8.42** | 7.49 |

### MXFP4 `Ice Lake` comparison with `GCC 14.2.0`
| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 45.51 | **43.82** | 28.16 |
| **tg128** | 4.15 | **8.73** | 7.74 |
***
## AMD EPYC `zen4`
<details><summary>Benchmarks</summary>

### ik_llama.cpp
| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         pp512 |     57.08 ± 0.05 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |         tg128 |     13.27 ± 1.41 |

| model                          |       size |     params | backend    | threads |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         pp512 |     56.81 ± 0.19 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |         tg128 |      5.47 ± 0.01 |
### ik_llama.cpp (-rtr 1)
| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     53.19 ± 0.08 |
| qwen3 4B Q4_0                  |   2.31 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     15.44 ± 0.08 |

| model                          |       size |     params | backend    | threads | rtr |          test |              t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --: | ------------: | ---------------: |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         pp512 |     55.22 ± 0.20 |
| qwen3 4B MXFP4 - 4.25 bpw      |   2.18 GiB |     4.41 B | CPU        |       2 |   1 |         tg128 |     13.52 ± 0.11 |
### llama.cpp
| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           pp512 |         36.92 ± 0.03 |
| qwen3 4B Q4_0                  |   2.11 GiB |     4.02 B | CPU        |       2 |           tg128 |         14.60 ± 0.16 |

| model                          |       size |     params | backend    | threads |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | --------------: | -------------------: |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           pp512 |         36.10 ± 0.05 |
| qwen3 4B MXFP4 MoE             |   1.99 GiB |     4.02 B | CPU        |       2 |           tg128 |         13.64 ± 0.06 |
</details>

### `Q4_0` `zen4`
| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 57.08 | 53.19 | 36.92 |
| **tg128** | 13.27 | **15.44** | **14.60** |

### `MXFP4` `zen4`
| Item | Before | After | `llama.cpp` |
| :--- | :--- | :--- | :--- |
| **pp512** | 56.81 | 55.22 | 36.10 |
| **tg128** | 5.47 | **13.52** | **13.64** |

> ### `IQ4_NL`-only CPU architecture comparison (without repacking)
> | Name | pp512 | tg128 |
> | :--- | :--- | :--- |
> | Zen 3 (AVX2) | 26.35 | 8.94 |
> | Ice Lake | 42.44 | 6.94 |
> | **Zen 4** | 55.74 | **13.74** |
> | Emerald Rapids | 54.08 | 5.88 |
> | Granite Rapids | 62.13 | 3.50 |

***
`Arrow Lake` has AVX-VNNI-INT8 `_mm256_dpbssd_epi32`.
