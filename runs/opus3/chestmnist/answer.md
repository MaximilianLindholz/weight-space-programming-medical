# Hand-set CNN weights for ChestMNIST (14 labels)

## Design

**Accuracy strategy.** Every label is rare. Prevalence runs from about 18% (infiltration) down to about 0.2% (hernia). The best fixed answer at threshold 0.5 is therefore "absent" for all labels. Each bias B[n] is set near logit(prevalence) minus a small margin. The features are kept small enough that no logit reaches 0, even on very washed-out images. So ACC should match the all-negative baseline, and AUC comes only from how images are ranked.

**Filters (3×3, applied to x in [-1, 1]):**

| Filter | Kernel and bias | Output | Detects |
|---|---|---|---|
| k0 | identity, bias +1 | x+1 (always ≥ 0, linear) | brightness |
| k1 | identity, bias -0.4 | ReLU(x-0.4) | dense, very white opacity |
| k2 | -identity, bias -0.4 | ReLU(-x-0.4) | very dark, hyperlucent areas |
| k3 / k4 | Sobel, ± signs | vertical edges | tubes, pleural lines, texture |
| k5 / k6 | Sobel, ± signs | horizontal edges | k5: diaphragm edge (dark above, bright below) |
| k7 | centre 1, neighbours -1/8, bias -0.1 | bright spot | nodules, masses, devices |
| k8 | negative of k7 | dark spot | gas pockets |
| k9 | unused | — | — |

**Regions on the 7×7 grid:**
- Lungs: columns 1–2 and 4–5, rows 1–5. Column 4 is only used in rows 1–2, because the heart occupies rows 3–5 of that column.
- Mediastinum and spine: column 3.
- Heart: rows 3–5, columns 3–4.

**What each output reads:**

| Label | Evidence it reads |
|---|---|
| Atelectasis, consolidation | Lower and mid lung brightness plus very-white area. Minus upper mediastinum brightness, to normalise for exposure. |
| Effusion | Brightness and white area at the lung bases and costophrenic cells (rows 4–5). Minus the sharpness of the diaphragm edge. Minus mediastinum. |
| Infiltration, pneumonia | Brightness and white area over the whole lung, exposure-normalised. |
| Edema | Perihilar (central lung) brightness plus bilateral white area. |
| Cardiomegaly | Brightness and white area in the cells just lateral to the heart (rows 3–5, columns 2 and 5). Minus upper-lung brightness. |
| Mass, nodule | Bright-spot energy inside the lungs. |
| Pneumothorax | Dark area in the upper lungs, plus edges and spots (chest tubes, pleural line). |
| Emphysema | Dark area over all lungs, extra darkness at the bases. |
| Fibrosis | Edge and spot texture, weighted toward the upper lungs. |
| Pleural thickening | Brightness at the apices and lateral lung margins. |
| Hernia | Dark spot and brightness in the cells behind the heart. |

```edits
# ---- filters ----
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[1] = -0.4
CW[2, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[2] = -0.4
CW[3, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CW[4, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CW[5, 0] = [[-0.25, -0.5, -0.25], [0, 0, 0], [0.25, 0.5, 0.25]]
CW[6, 0] = [[0.25, 0.5, 0.25], [0, 0, 0], [-0.25, -0.5, -0.25]]
CW[7, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[7] = -0.1
CW[8, 0] = [[0.125, 0.125, 0.125], [0.125, -1, 0.125], [0.125, 0.125, 0.125]]
CB[8] = -0.1

# ---- 0 atelectasis: lower/mid lung opacity ----
M[0, 0, 3:6, 1:3] = 0.06
M[0, 0, 3:6, 5] = 0.06
M[0, 1, 3:6, 1:3] = 0.2
M[0, 1, 3:6, 5] = 0.2
M[0, 0, 1:3, 3] = -0.08
B[0] = -2.5

# ---- 1 cardiomegaly: brightness lateral to heart ----
M[1, 0, 4:6, 5] = 0.15
M[1, 0, 4:6, 2] = 0.1
M[1, 1, 3:6, 5] = 0.3
M[1, 1, 4:6, 2] = 0.2
M[1, 0, 1:3, 1:3] = -0.04
M[1, 0, 1:3, 4:6] = -0.04
B[1] = -4.0

# ---- 2 effusion: basal opacity, blunted diaphragm ----
M[2, 0, 4:6, 1:3] = 0.08
M[2, 0, 4:6, 5] = 0.1
M[2, 1, 4:6, 1:3] = 0.25
M[2, 1, 4:6, 5] = 0.3
M[2, 5, 4:6, 1:3] = -0.3
M[2, 5, 4:6, 5] = -0.3
M[2, 0, 1:3, 3] = -0.08
B[2] = -2.4

# ---- 3 infiltration: diffuse lung opacity ----
M[3, 0, 1:6, 1:3] = 0.03
M[3, 0, 1:3, 4:6] = 0.03
M[3, 0, 3:6, 5] = 0.03
M[3, 1, 1:6, 1:3] = 0.1
M[3, 1, 1:3, 4:6] = 0.1
M[3, 1, 3:6, 5] = 0.1
M[3, 0, 1:3, 3] = -0.08
B[3] = -1.8

# ---- 4 mass: bright spots + dense areas in lungs ----
M[4, 7, 1:6, 1:3] = 0.5
M[4, 7, 1:3, 4:6] = 0.5
M[4, 7, 3:6, 5] = 0.5
M[4, 1, 1:6, 1:3] = 0.1
M[4, 1, 1:3, 4:6] = 0.1
M[4, 1, 3:6, 5] = 0.1
B[4] = -3.2

# ---- 5 nodule: bright spots in lungs ----
M[5, 7, 1:6, 1:3] = 0.6
M[5, 7, 1:3, 4:6] = 0.6
M[5, 7, 3:6, 5] = 0.6
B[5] = -3.0

# ---- 6 pneumonia: lung opacity ----
M[6, 0, 1:6, 1:3] = 0.03
M[6, 0, 1:3, 4:6] = 0.03
M[6, 0, 3:6, 5] = 0.03
M[6, 1, 2:6, 1:3] = 0.15
M[6, 1, 3:6, 5] = 0.15
M[6, 0, 1:3, 3] = -0.06
B[6] = -4.6

# ---- 7 pneumothorax: dark upper lungs, tubes/edges ----
M[7, 2, 1:4, 1:3] = 0.3
M[7, 2, 1:3, 4:6] = 0.3
M[7, 2, 3, 5] = 0.3
M[7, 3, 1:4, 1:3] = 0.1
M[7, 4, 1:4, 1:3] = 0.1
M[7, 3, 1:4, 4:6] = 0.1
M[7, 4, 1:4, 4:6] = 0.1
M[7, 7, 1:4, 1:3] = 0.3
M[7, 7, 1:4, 4:6] = 0.3
M[7, 0, 1:3, 1] = -0.05
M[7, 0, 1:3, 5] = -0.05
B[7] = -3.2

# ---- 8 consolidation: mid/lower opacity ----
M[8, 0, 2:6, 1:3] = 0.04
M[8, 0, 2:6, 5] = 0.04
M[8, 1, 2:6, 1:3] = 0.2
M[8, 1, 2:6, 5] = 0.2
M[8, 0, 1:3, 3] = -0.08
B[8] = -3.5

# ---- 9 edema: perihilar + bilateral opacity ----
M[9, 0, 2:5, 2] = 0.08
M[9, 0, 2, 4] = 0.08
M[9, 1, 1:6, 1:3] = 0.2
M[9, 1, 1:3, 4:6] = 0.2
M[9, 1, 3:6, 5] = 0.2
M[9, 0, 1:3, 3] = -0.06
B[9] = -4.3

# ---- 10 emphysema: hyperlucent lungs, dark bases ----
M[10, 2, 1:6, 1:3] = 0.25
M[10, 2, 1:3, 4:6] = 0.25
M[10, 2, 3:6, 5] = 0.25
M[10, 0, 4:6, 1:3] = -0.04
M[10, 0, 4:6, 5] = -0.04
B[10] = -4.0

# ---- 11 fibrosis: texture, upper-lobe weighted ----
M[11, 3, 1:6, 1:3] = 0.1
M[11, 4, 1:6, 1:3] = 0.1
M[11, 5, 1:6, 1:3] = 0.1
M[11, 6, 1:6, 1:3] = 0.1
M[11, 3, 1:3, 4:6] = 0.15
M[11, 4, 1:3, 4:6] = 0.15
M[11, 5, 1:3, 4:6] = 0.15
M[11, 6, 1:3, 4:6] = 0.15
M[11, 7, 1:4, 1:3] = 0.2
M[11, 7, 1:3, 4:6] = 0.2
M[11, 8, 1:4, 1:3] = 0.2
M[11, 8, 1:3, 4:6] = 0.2
B[11] = -4.5

# ---- 12 pleural thickening: apical caps, lateral margins ----
M[12, 0, 1, 1:3] = 0.06
M[12, 0, 1, 4:6] = 0.06
M[12, 0, 1:5, 1] = 0.06
M[12, 0, 1:4, 5] = 0.06
M[12, 1, 1, 1:3] = 0.15
M[12, 1, 1, 4:6] = 0.15
M[12, 0, 1:3, 3] = -0.05
B[12] = -3.8

# ---- 13 hernia: retrocardiac gas / density ----
M[13, 8, 4:6, 3:5] = 0.3
M[13, 0, 4:6, 3:5] = 0.05
B[13] = -6.5
```