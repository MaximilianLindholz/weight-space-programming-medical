## Design

**Prior.** About 73% of BreastMNIST images are label 1 (normal or benign). The bias therefore starts positive, and the network predicts "benign" unless there is clear malignant evidence.

**What the filters detect.** All kernels act on the 3×3 local mean or on a vertical gradient, which smooths out speckle.
- **Filter 0, darkness:** all weights −1/9, bias −0.3. It fires where the local mean is below about −0.3, i.e. on hypoechoic tissue such as a lesion.
- **Filter 1, strong darkness:** all weights −1/9, bias −0.7. It marks near-anechoic regions. It is computed but not read by the output, so it is neutral.
- **Filter 2, brightness:** all weights +1/9, bias −0.1. It fires on bright, echogenic tissue.
- **Filter 3, bright-below edge:** dark above and bright below, kernel rows (−1, 0, +1)/3, bias −0.3. This is the signature of posterior acoustic enhancement under a lesion, which is typical of benign cysts and fibroadenomas.

**How the output reads the evidence.**
- **Lesion burden (malignant evidence):** filter 0 is read with negative weight over the central grid. The weight is −0.15 on cells 1–5 and −0.3 on the inner 3×3 (rows and columns 2–4). Malignant masses in this dataset tend to be large, dark and central. Normal images have little darkness, and benign lesions are usually smaller.
- **Posterior shadowing (malignant evidence):** darkness directly below the centre adds −0.15 per cell on grid rows 5–6, columns 2–4.
- **Echogenic tissue (benign/normal evidence):** brightness is read with +0.15 in the centre, where it means no lesion. It is read with +0.2 below the centre, where it means posterior enhancement rather than shadow.
- **Bright-below edges (benign evidence):** filter 3 is read with +0.2 per cell on grid rows 3–5, columns 2–4.
- **Bias:** B = 1.2. A typical benign or normal image stays above 0. A large, dark, shadowing mass pushes the logit below 0.

```edits
# Filter 0: darkness (local mean below ~-0.3)
CW[0, 0] = [[-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111]]
CB[0] = -0.3
# Filter 1: strong darkness / anechoic (not read by the output)
CW[1, 0] = [[-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111]]
CB[1] = -0.7
# Filter 2: brightness (echogenic tissue)
CW[2, 0] = [[0.111, 0.111, 0.111], [0.111, 0.111, 0.111], [0.111, 0.111, 0.111]]
CB[2] = -0.1
# Filter 3: dark above / bright below edge (posterior enhancement)
CW[3, 0] = [[-0.333, -0.333, -0.333], [0, 0, 0], [0.333, 0.333, 0.333]]
CB[3] = -0.3

# Lesion burden: central darkness -> malignant
M[0, 0, 1:6, 1:6] = -0.15
M[0, 0, 2:5, 2:5] = -0.3
# Posterior shadowing: darkness below centre -> malignant
M[0, 0, 5:7, 2:5] -= 0.15
# Echogenic tissue centrally, and enhancement below -> benign/normal
M[0, 2, 2:5, 2:5] = 0.15
M[0, 2, 5:7, 2:5] = 0.2
# Bright-below edges in lower centre -> benign
M[0, 3, 3:6, 2:5] = 0.2

# Prior toward benign/normal
B[0] = 1.2
```