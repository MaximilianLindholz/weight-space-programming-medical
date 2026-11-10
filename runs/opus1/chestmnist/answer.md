## Design

**Approach.** All 14 labels are rare (about 0.2–19 % positives). So every bias is strongly negative, which keeps every sigmoid below 0.5 on all images. Accuracy then equals 1 − prevalence, the best a weak model can expect at threshold 0.5. The features are kept small and bounded so they can never push a logit above 0. Ranking (AUC) comes from radiologic cues built as differences between regions. Differences cancel the constant offsets and partly normalise exposure.

**Grid geometry (7×7 cells, standard PA orientation, patient-right on image-left).**
- Lungs: rows 1–4, columns 1, 2 (right lung) and 4, 5 (left lung).
- Spine and mediastinum: column 3.
- Heart: rows 3–4, columns 2–4.
- Costophrenic angles: around (4–5, 1) and (4–5, 5).
- Apices: rows 0–1.

**Filters.**
- **k0, brightness:** identity kernel with bias +1, so h = x + 1 (linear).
- **k1, aerated or dark:** ReLU(−mean₃ₓ₃ − 0.1), which responds to dark, air-filled lung.
- **k2, very bright:** ReLU(mean₃ₓ₃ − 0.5), which responds to dense opacity, tubes and wires.
- **k5, "bright-left" edge:** negative Sobel-x. It fires on the image-right heart border, where the bright heart meets dark lung.
- **k6, bright blob:** centre minus the mean of its 8 neighbours, minus 0.1. It is aimed at masses and nodules.
- **k3, k4, k7–k9:** unused (all zero).

**Evidence features (read from the pooled map g).**
- **OP, opacity:** mean k0 over the 16 lung cells minus mean k0 over the spine column (rows 1–4). It rises with opacified lungs and with low-contrast AP "sick-patient" films.
- **DARK:** mean k1 over the lung cells.
- **LOWER:** brightness of the lower-lateral cells (4–5, 1/5) minus the upper-lateral cells (1–2, 1/5). This captures blunted angles and basal effusion or collapse.
- **CARD:** brightness at the cardiac-border cells (3,5), (4,5), (4,2) minus upper-lung cells. A k5 edge shift from column 4 to column 5 is added, since a wider heart moves its border outward.
- **BLOB:** mean k6 over the lungs.
- **BRIGHT:** mean k2 over the lungs.
- **Label-specific extras:**
  - apical darkness, for pneumothorax;
  - upper-zone opacity, for fibrosis;
  - lateral-minus-inner lung brightness, for pleural thickening.

**How each label reads the features.**

| Label | Features used |
|---|---|
| Infiltration, pneumonia | OP up, DARK down |
| Consolidation | OP up, DARK down, plus LOWER |
| Atelectasis | OP up, LOWER up, BRIGHT up |
| Effusion | LOWER (strongest), OP, CARD a little, BRIGHT |
| Cardiomegaly | CARD plus the border-edge shift, a little OP and LOWER |
| Edema | OP plus CARD |
| Mass, nodule | BLOB plus a little OP |
| Pneumothorax | OP down, DARK up, dark apices |
| Emphysema | OP down, DARK up, darker bases (low, flat diaphragm) |
| Fibrosis | upper-zone opacity plus BLOB |
| Pleural thickening | peripheral brightness plus LOWER |
| Hernia | CARD plus a little OP, with a very low bias |

```edits
# ---------- conv filters ----------
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
CW[1, 0] = [[-0.1111, -0.1111, -0.1111], [-0.1111, -0.1111, -0.1111], [-0.1111, -0.1111, -0.1111]]
CB[1] = -0.1
CW[2, 0] = [[0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111]]
CB[2] = -0.5
CW[5, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[5] = -0.05
CW[6, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[6] = -0.1

# ---------- biases ----------
B[0] = -1.8
B[1] = -3.5
B[2] = -2.3
B[3] = -1.0
B[4] = -2.5
B[5] = -2.5
B[6] = -3.5
B[7] = -3.8
B[8] = -2.8
B[9] = -3.0
B[10] = -4.0
B[11] = -3.5
B[12] = -3.0
B[13] = -5.5

# ---------- 0 atelectasis: OP a=1.0, DARK -0.5, LOWER 0.8, BRIGHT 1 ----------
M[0, 0, 1:5, 1:3] += 0.0625
M[0, 0, 1:5, 4:6] += 0.0625
M[0, 0, 1:5, 3] -= 0.25
M[0, 1, 1:5, 1:3] += -0.03125
M[0, 1, 1:5, 4:6] += -0.03125
M[0, 0, 4:6, 1] += 0.2
M[0, 0, 4:6, 5] += 0.2
M[0, 0, 1:3, 1] -= 0.2
M[0, 0, 1:3, 5] -= 0.2
M[0, 2, 1:5, 1:3] += 0.0625
M[0, 2, 1:5, 4:6] += 0.0625

# ---------- 1 cardiomegaly: CARD 1.5, edge shift, OP 0.5, LOWER 0.3 ----------
M[1, 0, 3:5, 5] += 0.5
M[1, 0, 4, 2] += 0.5
M[1, 0, 1, 2] -= 0.5
M[1, 0, 1:3, 5] -= 0.5
M[1, 5, 3:5, 5] += 0.5
M[1, 5, 3:5, 4] -= 0.5
M[1, 0, 1:5, 1:3] += 0.03125
M[1, 0, 1:5, 4:6] += 0.03125
M[1, 0, 1:5, 3] -= 0.125
M[1, 0, 4:6, 1] += 0.075
M[1, 0, 4:6, 5] += 0.075
M[1, 0, 1:3, 1] -= 0.075
M[1, 0, 1:3, 5] -= 0.075

# ---------- 2 effusion: OP 1.0, DARK -0.5, LOWER 1.2, CARD 0.3, BRIGHT 1 ----------
M[2, 0, 1:5, 1:3] += 0.0625
M[2, 0, 1:5, 4:6] += 0.0625
M[2, 0, 1:5, 3] -= 0.25
M[2, 1, 1:5, 1:3] += -0.03125
M[2, 1, 1:5, 4:6] += -0.03125
M[2, 0, 4:6, 1] += 0.3
M[2, 0, 4:6, 5] += 0.3
M[2, 0, 1:3, 1] -= 0.3
M[2, 0, 1:3, 5] -= 0.3
M[2, 0, 3:5, 5] += 0.1
M[2, 0, 4, 2] += 0.1
M[2, 0, 1, 2] -= 0.1
M[2, 0, 1:3, 5] -= 0.1
M[2, 2, 1:5, 1:3] += 0.0625
M[2, 2, 1:5, 4:6] += 0.0625

# ---------- 3 infiltration: OP 1.2, DARK -0.5 ----------
M[3, 0, 1:5, 1:3] += 0.075
M[3, 0, 1:5, 4:6] += 0.075
M[3, 0, 1:5, 3] -= 0.3
M[3, 1, 1:5, 1:3] += -0.03125
M[3, 1, 1:5, 4:6] += -0.03125

# ---------- 4 mass: OP 0.6, DARK -0.3, BLOB 5 ----------
M[4, 0, 1:5, 1:3] += 0.0375
M[4, 0, 1:5, 4:6] += 0.0375
M[4, 0, 1:5, 3] -= 0.15
M[4, 1, 1:5, 1:3] += -0.01875
M[4, 1, 1:5, 4:6] += -0.01875
M[4, 6, 1:5, 1:3] += 0.3125
M[4, 6, 1:5, 4:6] += 0.3125

# ---------- 5 nodule: OP 0.3, DARK -0.2, BLOB 6 ----------
M[5, 0, 1:5, 1:3] += 0.01875
M[5, 0, 1:5, 4:6] += 0.01875
M[5, 0, 1:5, 3] -= 0.075
M[5, 1, 1:5, 1:3] += -0.0125
M[5, 1, 1:5, 4:6] += -0.0125
M[5, 6, 1:5, 1:3] += 0.375
M[5, 6, 1:5, 4:6] += 0.375

# ---------- 6 pneumonia: OP 1.2, DARK -0.5, LOWER 0.3 ----------
M[6, 0, 1:5, 1:3] += 0.075
M[6, 0, 1:5, 4:6] += 0.075
M[6, 0, 1:5, 3] -= 0.3
M[6, 1, 1:5, 1:3] += -0.03125
M[6, 1, 1:5, 4:6] += -0.03125
M[6, 0, 4:6, 1] += 0.075
M[6, 0, 4:6, 5] += 0.075
M[6, 0, 1:3, 1] -= 0.075
M[6, 0, 1:3, 5] -= 0.075

# ---------- 7 pneumothorax: OP -0.8, DARK +1, apical dark, BRIGHT (tubes) 1 ----------
M[7, 0, 1:5, 1:3] += -0.05
M[7, 0, 1:5, 4:6] += -0.05
M[7, 0, 1:5, 3] += 0.2
M[7, 1, 1:5, 1:3] += 0.0625
M[7, 1, 1:5, 4:6] += 0.0625
M[7, 1, 0:2, 1] += 0.15
M[7, 1, 0:2, 5] += 0.15
M[7, 2, 1:5, 1:3] += 0.0625
M[7, 2, 1:5, 4:6] += 0.0625

# ---------- 8 consolidation: OP 1.2, DARK -0.5, LOWER 0.6, BRIGHT 1 ----------
M[8, 0, 1:5, 1:3] += 0.075
M[8, 0, 1:5, 4:6] += 0.075
M[8, 0, 1:5, 3] -= 0.3
M[8, 1, 1:5, 1:3] += -0.03125
M[8, 1, 1:5, 4:6] += -0.03125
M[8, 0, 4:6, 1] += 0.15
M[8, 0, 4:6, 5] += 0.15
M[8, 0, 1:3, 1] -= 0.15
M[8, 0, 1:3, 5] -= 0.15
M[8, 2, 1:5, 1:3] += 0.0625
M[8, 2, 1:5, 4:6] += 0.0625

# ---------- 9 edema: OP 1.2, DARK -0.5, CARD 0.6, BRIGHT 1 ----------
M[9, 0, 1:5, 1:3] += 0.075
M[9, 0, 1:5, 4:6] += 0.075
M[9, 0, 1:5, 3] -= 0.3
M[9, 1, 1:5, 1:3] += -0.03125
M[9, 1, 1:5, 4:6] += -0.03125
M[9, 0, 3:5, 5] += 0.2
M[9, 0, 4, 2] += 0.2
M[9, 0, 1, 2] -= 0.2
M[9, 0, 1:3, 5] -= 0.2
M[9, 2, 1:5, 1:3] += 0.0625
M[9, 2, 1:5, 4:6] += 0.0625

# ---------- 10 emphysema: OP -1.0, DARK +1, LOWER -0.8 ----------
M[10, 0, 1:5, 1:3] += -0.0625
M[10, 0, 1:5, 4:6] += -0.0625
M[10, 0, 1:5, 3] += 0.25
M[10, 1, 1:5, 1:3] += 0.0625
M[10, 1, 1:5, 4:6] += 0.0625
M[10, 0, 4:6, 1] -= 0.2
M[10, 0, 4:6, 5] -= 0.2
M[10, 0, 1:3, 1] += 0.2
M[10, 0, 1:3, 5] += 0.2

# ---------- 11 fibrosis: OP 0.3, upper-zone OP 0.6, BLOB 2 ----------
M[11, 0, 1:5, 1:3] += 0.01875
M[11, 0, 1:5, 4:6] += 0.01875
M[11, 0, 1:5, 3] -= 0.075
M[11, 0, 1:3, 1:3] += 0.075
M[11, 0, 1:3, 4:6] += 0.075
M[11, 0, 1:3, 3] -= 0.3
M[11, 6, 1:5, 1:3] += 0.125
M[11, 6, 1:5, 4:6] += 0.125

# ---------- 12 pleural thickening: OP 0.5, peripheral-minus-inner 0.6, LOWER 0.4, BLOB 1 ----------
M[12, 0, 1:5, 1:3] += 0.03125
M[12, 0, 1:5, 4:6] += 0.03125
M[12, 0, 1:5, 3] -= 0.125
M[12, 0, 1:4, 1] += 0.1
M[12, 0, 1:4, 5] += 0.1
M[12, 0, 1:4, 2] -= 0.1
M[12, 0, 1:4, 4] -= 0.1
M[12, 0, 4:6, 1] += 0.1
M[12, 0, 4:6, 5] += 0.1
M[12, 0, 1:3, 1] -= 0.1
M[12, 0, 1:3, 5] -= 0.1
M[12, 6, 1:5, 1:3] += 0.0625
M[12, 6, 1:5, 4:6] += 0.0625

# ---------- 13 hernia: CARD 0.8, OP 0.4 ----------
M[13, 0, 3:5, 5] += 0.2667
M[13, 0, 4, 2] += 0.2667
M[13, 0, 1, 2] -= 0.2667
M[13, 0, 1:3, 5] -= 0.2667
M[13, 0, 1:5, 1:3] += 0.025
M[13, 0, 1:5, 4:6] += 0.025
M[13, 0, 1:5, 3] -= 0.1
```