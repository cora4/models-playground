The key idea is that **`--kl-divergence-base` does not compare two quantized models directly**. It first records the output logits of a reference model—normally FP16—over the evaluation dataset. Then `--kl-divergence` takes those saved FP16 logits and compares a quantized model's output distribution against them.

 ## 1\. Think of it as a two-pass experiment

 Suppose you have:

```
Llama-3-8B-F16.gguf
Llama-3-8B-Q5_1.gguf
Llama-3-8B-Q4_1.gguf
```

 You first establish the **FP16 reference**:

```
                 Wikitext-2
                     │
                     ▼
               FP16 model
                     │
                     ▼
             logits for every
                 token
                     │
                     ▼
             fp16.kld file
```

 Then you can test each quantization against that _same_ reference:

```
                 fp16.kld
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Q5_1 model          Q4_1 model
          │                   │
          ▼                   ▼
      statistics           statistics
```

 This is useful because otherwise ordinary perplexity only tells you how well each model predicts the actual next token. KLD tells you **how much the entire probability distribution changed relative to FP16**.

---

 ## 2\. First command: create the `.kld` reference

 Run the FP16 model with:

```
./build/bin/llama-perplexity \
    -m ./models/Llama-3-8B-F16.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --kl-divergence-base ./fp16.kld
```

 The important part is:

```
--kl-divergence-base ./fp16.kld
```

 **Without `--kl-divergence`, this means "record the base model's logits."**

 The resulting file contains the reference logits needed for subsequent comparisons. The llama.cpp documentation warns that these files are huge: approximately **11 GiB for Llama 2** and **37 GiB for Llama 3** using Wikitext-2.

 So don't think of `fp16.kld` as a normal little statistics file. It's effectively a cached representation of the FP16 model's outputs for the whole test corpus.

---

 ## 3\. Then test Q5\_1

 Now:

```
./build/bin/llama-perplexity \
    -m ./models/Llama-3-8B-Q5_1.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --kl-divergence-base ./fp16.kld \
    --kl-divergence
```

 And Q4\_1:

```
./build/bin/llama-perplexity \
    -m ./models/Llama-3-8B-Q4_1.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --kl-divergence-base ./fp16.kld \
    --kl-divergence
```

 Notice that you **reuse exactly the same `fp16.kld` file**.

 That's important.

---

 # What is actually being compared?

 For a particular token, imagine FP16 produces:

```
                FP16       Q4_1
"the"           0.40       0.35
"cat"           0.20       0.22
"dog"           0.10       0.12
"sat"           0.05       0.06
...
```

 These are probability distributions over the vocabulary.

 Perplexity primarily asks:

 > How much probability did you assign to the **correct next token**?

 KLD asks something broader:

 > How different is the **entire Q4\_1 probability distribution** from FP16's distribution?

 Mathematically, llama.cpp is measuring the KL divergence between the reference and quantized distributions:

 $$
D_{KL}(P_{\mathrm{FP16}}\parallel P_Q)
=
\sum_i P_{\mathrm{FP16}}(i)
\log\frac{P_{\mathrm{FP16}}(i)}{P_Q(i)}
$$

 Conceptually:

```
KLD = 0
    ↓
identical probability distributions

small KLD
    ↓
quantization changed the distribution only slightly

large KLD
    ↓
quantization substantially changed the distribution
```

 The llama.cpp documentation explicitly defines **0 as identical distributions**.

---

 # Why KLD is interesting for quantization

 Consider these two situations.

 ### Case A

 FP16:

```
cat  90%
dog   5%
car   1%
...
```

 Q4:

```
cat  89%
dog   6%
car   1%
...
```

 The model's behavior barely changed.

 ### Case B

 FP16:

```
cat  90%
dog   5%
car   1%
...
```

 Q4:

```
cat  40%
dog  35%
car  15%
...
```

 The correct token might still be `cat`, so ordinary PPL might not look catastrophically different, but the **distribution has changed dramatically**.

 KLD captures that.

---

 # The really useful output

 When you run `--kl-divergence`, llama.cpp produces several groups of statistics.

 For example:

```
====== Perplexity statistics ======

Mean PPL(Q)       : 6.337857
Mean PPL(base)    : 6.233160

Mean PPL(Q)/PPL(base) : 1.016...
Mean PPL(Q)-PPL(base) : 0.104...

====== KL divergence statistics ======

Mean KLD:     0.018045
...
Median KLD:   ...
99.0% KLD:    ...

====== Token probability statistics ======

Mean Δp:      -0.287 %
...
RMS Δp:        4.123 %
Same top p:   ...
```

 There are several different questions being answered.

 ### `Mean KLD`

 This is the big one.

```
Mean KLD: 0.018
```

 means that, averaged over the evaluated tokens, the quantized model's probability distributions differ from the FP16 distributions by that amount according to KL divergence.

 **Lower means closer to FP16.**

 For example, the current llama.cpp Llama 3 8B scoreboard reports:

 | Quantization | PPL | KLD | RMS Δp |
| --- | --- | --- | --- |
| FP16 | 6.2332 | 0.000551 | 0.787% |
| Q5\_1 | 6.3379 | 0.018045 | 4.123% |
| Q4\_1 | 6.6827 | 0.071683 | 8.512% |

Those are llama.cpp's documented measurements for that particular test configuration.

 So you can see that Q4\_1 isn't merely getting a somewhat worse PPL—it is also producing substantially more distributional change relative to FP16.

---

 # `Mean Δp`

 This is particularly interesting.

 It measures the change in probability assigned to the **correct token**.

 For example:

```
Mean Δp: -0.927%
```

 means that, on average, the quantized model assigned about 0.927 percentage points less probability to the correct token than the reference.

 The llama.cpp documentation says positive means better prediction and negative means worse prediction.

 But don't overinterpret the mean alone.

---

 # `RMS Δp`

 This tells you the **typical magnitude of the probability changes**, regardless of direction.

 For example:

```
RMS Δp: 4.123%
```

 means the probability assigned to the correct token is moving around by several percentage points in typical magnitude.

 This is useful for distinguishing:

```
small random perturbations
```

 from

```
systematic degradation
```

 The llama.cpp documentation describes this as related to treating the quantization effect as noise on token probabilities.

---

 # `Same top p`

 This one is very intuitive.

 Suppose FP16 says:

```
1. cat   40%
2. dog   25%
3. bird  10%
```

 and Q4 says:

```
1. cat   35%
2. dog   30%
3. bird  12%
```

 The top prediction is still `cat`.

 That's a **same-top-p event**.

 If Q4 instead says:

```
1. dog   36%
2. cat   35%
3. bird  10%
```

 then the top prediction changed.

 So:

```
Same top p: 98%
```

 means the quantized model selected the same highest-probability token as the reference about 98% of the time.

 The llama.cpp documentation calls this "Same top p" and describes it as the percentage of times both models assigned the highest probability to the same token.

---

 # Why the percentiles are useful

 You might see:

```
KLD:

99.0%    0.59
95.0%    0.24
90.0%    0.14
Median   0.005
```

 This tells you something that the mean hides.

 For example, if:

```
Median KLD = 0.005
Mean KLD   = 0.05
```

 then most tokens are extremely close, but a relatively small number of tokens have **very large deviations**.

 That's why I wouldn't judge a quantization solely from the mean.

---

 # The most interesting part for comparing Q5\_1 vs Q4\_1

 For your original experiment, I'd run:

```
# 1. Generate reference once
./build/bin/llama-perplexity \
    -m Llama-3-8B-F16.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --kl-divergence-base llama3-8b-f16.kld
```

 Then:

```
# 2. Q5_1
./build/bin/llama-perplexity \
    -m Llama-3-8B-Q5_1.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --kl-divergence-base llama3-8b-f16.kld \
    --kl-divergence
```

 and:

```
# 3. Q4_1
./build/bin/llama-perplexity \
    -m Llama-3-8B-Q4_1.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --kl-divergence-base llama3-8b-f16.kld \
    --kl-divergence
```

 Then make a table like:

 | Metric | Q5\_1 | Q4\_1 |
| --- | --- | --- |
| PPL |  |  |
| ΔPPL |  |  |
| PPL ratio |  |  |
| Mean KLD |  |  |
| Median KLD |  |  |
| 99% KLD |  |  |
| Mean Δp |  |  |
| RMS Δp |  |  |
| Same top p |  |  |

This is **much more informative than just comparing PPL**.

 In fact, llama.cpp's own Llama 3 8B scoreboard sorts its quantizations by KLD relative to FP16 and reports PPL, KLD, mean Δp and RMS Δp together.

 ### One important caveat

 The `.kld` reference must correspond to the **same exact evaluation setup**: same model/reference, dataset, context/evaluation settings, etc. You're effectively pairing the reference logits token-by-token with the quantized model's logits. You shouldn't generate the reference with one test configuration and then change the relevant evaluation conditions for the quantized run.

 Also, the current llama.cpp README notes that its stored FP16 logits are actually converted to a compact 16-bit representation with scaling, so even the "FP16 vs FP16" KLD isn't mathematically zero; the documented Llama 3 8B scoreboard shows a small nonzero baseline KLD for `f16`.
