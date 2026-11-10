"""The single tool-free prompt per task (identical for both LLMs). Contains no image and no data statistics.

    python prompts.py uterusmnist      # print one prompt
"""
import sys
from medmnist import INFO
from prognet import shape


def source(flag):
    if flag == "uterusmnist":
        return ("SynthUterus (Mueller et al. 2026, Zenodo): synthetic, region-of-interest-cropped uterine MRI slices; "
                "only cases validated by two radiologists are used; images downsampled from 96 x 96 to 28 x 28")
    return f"{INFO[flag]['python_class']} from MedMNIST v2 (Yang et al. 2023), official split"


def build(flag):
    info = INFO[flag]
    k, c, no = shape(flag)
    task = info["task"]
    labels = "\n".join(f"  {i}: {n}" for i, n in info["label"].items())
    if task == "binary-class":
        out = (f"THE OUTPUT: one logit o_0 = log-odds that the label is 1 ('{info['label']['1']}'); "
               "the score is sigmoid(o_0).")
        scoring = "AUC of sigmoid(o_0), and ACC with threshold 0.5."
    elif task.startswith("multi-label"):
        out = f"THE OUTPUT: {no} logits, one per label; label i's score is sigmoid(o_i) (labels are independent)."
        scoring = "mean over labels of the per-label AUC, and mean per-label ACC with threshold 0.5."
    else:
        out = f"THE OUTPUT: {no} logits, one per class; class scores are softmax(o)."
        scoring = "mean over classes of the one-vs-rest AUC of the softmax scores, and ACC of argmax."
    chan = "1 channel (grey)" if c == 1 else "3 channels in the order R, G, B"
    n_params = k * c * 9 + k + no * k * 49 + no
    return f"""YOUR TASK: write, from scratch, the weights of a small convolutional network that solves this medical image classification task as well as possible. There is no training: no data, no loss, no gradients, no fine-tuning; you choose every number yourself. You have no tools: no code execution, no calculator, nothing to run, and you will not see any image from this dataset. This is a single response and you will get no feedback. First describe your design briefly (which image features each filter detects, and which evidence each output reads where), then write the edits block.

THE DATASET: {source(flag)}. Task type: {task}.
Official description: {info['description']}
Labels:
{labels}

THE INPUT: one image of 28 x 28 pixels with {chan}. Each pixel value p in 0..255 is given to the network as x = (p / 255 - 0.5) / 0.5, i.e. in [-1, 1] (-1 = black, +1 = white). Rows go from 0 (top) to 27 (bottom), columns from 0 (left) to 27 (right), exactly as stored in the dataset arrays.

{out}

THE NETWORK ({n_params:,} parameters; the same architecture as the gradient-trained baselines it is compared with):
  h   = ReLU(conv3x3(x; CW, CB))     CW: {k} x {c} x 3 x 3, CB: {k}   (stride 1, zero padding 1 -> {k} x 28 x 28)
  g   = AvgPool4x4(h)                -> {k} x 7 x 7 (cell (i, j) averages pixel rows 4i..4i+3, columns 4j..4j+3)
  o_n = sum over k, i, j of M[n, k, i, j] * g[k, i, j]  +  B[n]      M: {no} x {k} x 7 x 7, B: {no}
CW[k, c] is the 3 x 3 kernel of filter k on input channel c, applied as cross-correlation: kernel entry [a, b] multiplies the pixel at offset (a - 1, b - 1) (row, column). EVERY WEIGHT STARTS AT 0; you set the weights you need.

HOW YOUR NETWORK IS SCORED: on the official test split with MedMNIST's official metrics: {scoring} It is compared with networks of the same architecture trained by gradient descent on 256 labelled images and on the full training set.

HOW TO WRITE THE WEIGHTS (numbers only; nothing is run). Write a code block whose opening line is three backticks followed by the word edits, one statement per line ('#' starts a comment; a long list may continue over the next lines). Tensors: CW, CB, M, B.

```edits
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]   # filter 0, channel 0: identity kernel
CB[0] = -0.5                                    # one entry
M[2, 0, 1:6, 1:3] = 0.1                         # output 2 reads filter 0 in grid rows 1..5, columns 1..2
M[2, 0, 3] = [0, 0, 0.2, 0.2, 0.2, 0, 0]        # explicit values along the last axis
B[:] = -1                                       # fill a range (a:b is half-open; ':' alone = the whole axis)
M[:, 1] *= 2                                    # scale (also += and -=)
```
Ranges: a:b is half-open, a:b:s takes every s-th index. Statements apply in order; a later statement overwrites an earlier one. Only the LAST edits block of your reply is read; a statement that cannot be read is skipped (the others still apply). Values: plain decimal numbers (|v| <= 1e6); a list must have exactly the shape of the indexed block.
"""


if __name__ == "__main__":
    print(build(sys.argv[1]))
