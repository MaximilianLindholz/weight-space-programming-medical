# Hand-set CNN for OrganCMNIST: design and weights

## Design

I can't see the data, so I tuned every weight against my own estimates of how each organ crop looks. These estimates assume:
- Hounsfield units map to x ≈ (HU − 50)/200 with clipping. That puts air at −1, fat at about −0.75, urine at about −0.2, muscle at about 0, enhanced liver or spleen at about +0.3, enhanced kidney cortex or cardiac blood at about +0.6, and bone at +1.
- Each image is the organ's bounding box, so the organ sits in the centre and its surroundings sit at the border.

### Filters (3×3 kernels; m is the local 3×3 mean)

| Filter | Detects | Formula and thresholds |
|---|---|---|
| F0 | air | ReLU(−9m − 8): fires only when m < −0.89, i.e. lung or gas. Fat stays at 0. |
| F1 | dark: fat or air | ReLU(−3.6m − 1.8): fat ≈ 0.9, air = 1.8. The output layer reads "fat" as F1 − 1.8·F0, which is about 0.9 for fat and 0 for air. |
| F2 | any soft tissue | ReLU(m + 0.4): urine ≈ 0.2, muscle ≈ 0.4, liver ≈ 0.7, kidney ≈ 1.0. |
| F3 | enhanced parenchyma | ReLU(m + 0.05): zero for urine and fat, ≈ 0.35 for liver or spleen, ≈ 0.65 for kidney or heart. |
| F9 | strongly enhanced | ReLU(m − 0.4): kidney cortex, cardiac blood pool, bone. |
| F4 | bone | ReLU(5x − 4) on the centre pixel: cortical or trabecular bone (x > 0.8). |
| F5–F8 | edges | Sobel-type gradients in ±horizontal and ±vertical directions, minus 0.15. Their sum measures texture and boundary density. |

### What each output reads (on the 7×7 pooled grid)

- **Lung (7, 8):** air in the centre plus air over the whole image.
- **Femur (1, 2):** bone fraction over the whole image, plus strong enhancement in the centre.
- **Bladder (0):** "water band" in the centre, meaning tissue present (F2) but no enhancement (F3 = 0). It is penalised by central fat, edges and air, and rewarded by a fat surround.
- **Liver (6):** homogeneous enhanced centre (F3 but no F9). It is penalised by fat, edges and air.
- **Spleen (10):** like liver, but the fat surround counts in its favour and central fat counts against it.
- **Kidney (4, 5):** strong enhancement in the centre (F9), a fat surround and inner edges, with bone penalised.
- **Pancreas (9):** fat in the centre and overall, plus high central edge density. Strong enhancement counts against it.
- **Heart (3):** air at the image border but not the centre (flanking lungs), plus an enhanced centre.

### Left/right cues

All left/right cues rest on one assumption: images use the radiological convention, with the patient's left on the image's right. Under that convention, a left-sided organ has its bulk laterally, i.e. on the image right. I gave these cues only moderate weight because I can't verify the orientation. Each paired class gets the cue with opposite signs:

- **Lung:** air in the lower-right minus lower-left cells favours left lung. The medial side holds the heart or mediastinum.
- **Kidney:** enhanced tissue on the right minus the left favours left kidney. The hilum, with its sinus fat, is medial.
- **Femur:** bone on the right minus the left favours left femur. The shaft and trochanter are lateral.
- **Liver vs spleen:** enhanced tissue on the image left favours liver; on the image right it favours spleen.

## Weights

```edits
# ---------- filters ----------
CW[0, 0] = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]
CB[0] = -8
CW[1, 0] = [[-0.4, -0.4, -0.4], [-0.4, -0.4, -0.4], [-0.4, -0.4, -0.4]]
CB[1] = -1.8
CW[2, 0] = [[0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111]]
CB[2] = 0.4
CW[3, 0] = [[0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111]]
CB[3] = 0.05
CW[4, 0] = [[0, 0, 0], [0, 5, 0], [0, 0, 0]]
CB[4] = -4
CW[5, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CB[5] = -0.15
CW[6, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[6] = -0.15
CW[7, 0] = [[-0.25, -0.5, -0.25], [0, 0, 0], [0.25, 0.5, 0.25]]
CB[7] = -0.15
CW[8, 0] = [[0.25, 0.5, 0.25], [0, 0, 0], [-0.25, -0.5, -0.25]]
CB[8] = -0.15
CW[9, 0] = [[0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111], [0.1111, 0.1111, 0.1111]]
CB[9] = -0.4

# ---------- bladder (0) ----------
M[0, 2, 2:5, 2:5] = 0.667
M[0, 3, 2:5, 2:5] = -1.556
M[0, 1, :, :] = 0.0306
M[0, 1, 2:5, 2:5] = -0.303
M[0, 0, :, :] = -0.0551
M[0, 0, 2:5, 2:5] = -0.122
M[0, 5:9, 2:5, 2:5] = -0.333
B[0] = 0

# ---------- femur left (1) / right (2) ----------
M[1, 4, :, :] = 0.408
M[1, 9, 2:5, 2:5] = 0.222
M[2, 4, :, :] = 0.408
M[2, 9, 2:5, 2:5] = 0.222
B[1] = -3
B[2] = -3
M[1, 4, :, 4:7] += 0.381
M[1, 4, :, 0:3] -= 0.381
M[2, 4, :, 0:3] += 0.381
M[2, 4, :, 4:7] -= 0.381

# ---------- heart (3) ----------
M[3, 0, :, :] = 0.351
M[3, 0, 2:5, 2:5] = -0.982
M[3, 1, :, :] = -0.0816
M[3, 3, 2:5, 2:5] = 0.556
M[3, 9, 2:5, 2:5] = 0.556
M[3, 4, :, :] = -0.204
B[3] = -1.5

# ---------- kidney left (4) / right (5) ----------
M[4, 9, 2:5, 2:5] = 1.111
M[4, 3, 2:5, 2:5] = 0.333
M[4, 1, :, :] = 0.1224
M[4, 0, :, :] = -0.343
M[4, 5:9, 1:6, 1:6] = 0.08
M[4, 4, :, :] = -0.510
B[4] = -3
M[5, 9, 2:5, 2:5] = 1.111
M[5, 3, 2:5, 2:5] = 0.333
M[5, 1, :, :] = 0.1224
M[5, 0, :, :] = -0.343
M[5, 5:9, 1:6, 1:6] = 0.08
M[5, 4, :, :] = -0.510
B[5] = -3
M[4, 3, 1:6, 4:7] += 0.667
M[4, 3, 1:6, 0:3] -= 0.667
M[5, 3, 1:6, 0:3] += 0.667
M[5, 3, 1:6, 4:7] -= 0.667

# ---------- liver (6) ----------
M[6, 3, 2:5, 2:5] = 0.889
M[6, 9, 2:5, 2:5] = -1.556
M[6, 1, :, :] = -0.1224
M[6, 0, :, :] = 0.2204
M[6, 0, 2:5, 2:5] = -0.4466
M[6, 5:9, 2:5, 2:5] = -0.444
M[6, 3, :, 0:3] += 0.286
M[6, 3, :, 4:7] -= 0.286
B[6] = 0

# ---------- lung left (7) / right (8) ----------
M[7, 0, :, :] = 0.0816
M[7, 0, 2:5, 2:5] = 0.970
M[8, 0, :, :] = 0.0816
M[8, 0, 2:5, 2:5] = 0.970
B[7] = -4
B[8] = -4
M[7, 0, 2:7, 4:7] += 0.533
M[7, 0, 2:7, 0:3] -= 0.533
M[8, 0, 2:7, 0:3] += 0.533
M[8, 0, 2:7, 4:7] -= 0.533

# ---------- pancreas (9) ----------
M[9, 1, :, :] = 0.0612
M[9, 1, 2:5, 2:5] = 0.617
M[9, 0, :, :] = -0.110
M[9, 0, 2:5, 2:5] = -1.554
M[9, 5:9, 2:5, 2:5] = 0.444
M[9, 9, 2:5, 2:5] = -0.889
B[9] = -2

# ---------- spleen (10) ----------
M[10, 3, 2:5, 2:5] = 0.889
M[10, 9, 2:5, 2:5] = -1.556
M[10, 1, :, :] = 0.0816
M[10, 1, 2:5, 2:5] = -0.807
M[10, 0, :, :] = -0.147
M[10, 0, 2:5, 2:5] = 0.786
M[10, 5:9, 2:5, 2:5] = -0.444
M[10, 3, :, 0:3] -= 0.286
M[10, 3, :, 4:7] += 0.286
B[10] = -1.3
```