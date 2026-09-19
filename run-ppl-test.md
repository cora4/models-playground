[GitHub](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md) describes **perplexity testing of quantized GGUF models**, normally against the Wikitext-2 test set. Lower perplexity means better next-token prediction, and the llama.cpp convention is to use Wikitext-2 for these comparisons.

 If your goal is specifically:

 > **Compare the same model quantized as `Q5_1` vs `Q4_1`**

 here is the concrete procedure.

 ## 1\. Build llama.cpp

 From the llama.cpp directory:

```
cmake -B build
cmake --build build --config Release -j
```

 You should then have the perplexity executable at approximately:

```
build/bin/llama-perplexity
```

 Check:

```
build/bin/llama-perplexity --help
```

 ## 2\. Download Wikitext-2

 From the llama.cpp root:

```
./scripts/get-wikitext-2.sh
```

 This downloads/prepares the Wikitext-2 test corpus that llama.cpp uses for its standard perplexity measurements.

 The resulting test file is normally:

```
./data/wikitext-2-raw/wiki.test.raw
```

 You can verify with:

```
ls -lh data/wikitext-2-raw/wiki.test.raw
```

 ## 3\. Get your two GGUF models

 For example, suppose you have:

```
models/MyModel-Q4_1.gguf
models/MyModel-Q5_1.gguf
```

 **Important:** these must be quantizations of the **same underlying model**, with the same tokenizer/model architecture. Otherwise the comparison isn't meaningful as a quantization-quality comparison.

 ## 4\. Run Q4\_1

```
./build/bin/llama-perplexity \
    --model ./models/MyModel-Q4_1.gguf \
    --file ./data/wikitext-2-raw/wiki.test.raw
```

 Or, if your build uses the executable from `bin` directly:

```
./bin/llama-perplexity \
    --model ./models/MyModel-Q4_1.gguf \
    --file ./data/wikitext-2-raw/wiki.test.raw
```

 The current llama.cpp CI also demonstrates the basic pattern:

```
llama-perplexity --model MODEL --file WIKI_TEST
```

 with additional options for its CI configuration.  [GitHub](https://github.com/ggml-org/llama.cpp/blob/master/ci/run.sh)

 ## 5\. Run Q5\_1

 Exactly the same test, changing only the model:

```
./build/bin/llama-perplexity \
    --model ./models/MyModel-Q5_1.gguf \
    --file ./data/wikitext-2-raw/wiki.test.raw
```

 **Keep everything else identical.** That's important for a fair comparison.

 You'll get output containing a value along the lines of:

```
perplexity = 6.xxxx +/- 0.xxxx
```

 Record those numbers.

 ## 6\. Run both automatically

 I'd actually use this little shell script so you don't accidentally change parameters between tests:

```
#!/bin/bash

PPL=./build/bin/llama-perplexity
WIKI=./data/wikitext-2-raw/wiki.test.raw

echo "===== Q4_1 ====="
$PPL \
    --model ./models/MyModel-Q4_1.gguf \
    --file "$WIKI"

echo
echo "===== Q5_1 ====="
$PPL \
    --model ./models/MyModel-Q5_1.gguf \
    --file "$WIKI"
```

 Save as:

```
compare.sh
```

 then:

```
chmod +x compare.sh
./compare.sh
```

 That gives you an apples-to-apples comparison.

 ## If you want to reproduce llama.cpp's more controlled test

 The llama.cpp CI currently runs the perplexity test with:

```
./bin/llama-perplexity \
    --model MODEL \
    --file WIKI_TEST \
    -ngl 99 \
    -c 1024 \
    -b 512 \
    --chunks 2
```

 and does this separately for `q4_1` and `q5_1`.  [GitHub](https://github.com/ggml-org/llama.cpp/blob/master/ci/run.sh)

 So you could do:

```
./build/bin/llama-perplexity \
    --model ./models/MyModel-Q4_1.gguf \
    --file ./data/wikitext-2-raw/wiki.test.raw \
    -ngl 99 \
    -c 1024 \
    -b 512 \
    --chunks 2
```

 and:

```
./build/bin/llama-perplexity \
    --model ./models/MyModel-Q5_1.gguf \
    --file ./data/wikitext-2-raw/wiki.test.raw \
    -ngl 99 \
    -c 1024 \
    -b 512 \
    --chunks 2
```

 `-ngl 99` essentially means "offload as many layers as possible" on a GPU-capable build. If you're CPU-only, you can omit it.

 ### What you should compare

 Suppose you get:

```
Q4_1:  6.6827
Q5_1:  6.3379
```

 Then the raw difference is:

```
6.6827 - 6.3379 = 0.3448
```

 and the relative increase of Q4\_1 over Q5\_1 is:

```
0.3448 / 6.3379 × 100 = 5.44%
```

 For reference, the current llama.cpp README's **Llama 3 8B** scoreboard reports `Q5_1` at **6.337857** and `Q4_1` at **6.682737** under its documented test conditions.

 One important distinction: **perplexity tells you about prediction loss; it doesn't directly tell you how much you'll notice the difference in chat/use.** llama.cpp also supports a more detailed comparison against FP16 using `--kl-divergence-base` and `--kl-divergence`, which measures differences in the output logit distributions. 
