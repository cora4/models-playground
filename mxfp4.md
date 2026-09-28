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
`Arrow Lake`  does not have `AVX-512`, but it does have AVX-VNNI-INT8 `_mm256_dpbssd_epi32`.
