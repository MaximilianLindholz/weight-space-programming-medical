# Hand-built CNN weights for OrganAMNIST

## Design

**Assumptions.** Each image is a tight crop of one organ's bounding box. Intensities follow an abdominal CT window, so roughly x ≈ (HU − 40)/200:

| Tissue | Approximate x |
|---|---|
| Air | −1 |
| Fat | −0.7 |
| Urine | −0.15 |
| Muscle | 0.05 |
| Enhanced liver / spleen | 0.35–0.4 |
| Kidney cortex / blood pool | 0.7 |
| Bone | 1 |

**Filters**

- **Filters 0–5 (intensity ramps).** Each uses an identity kernel and computes ReLU(x − t), with t = −0.95, −0.7, −0.2, 0.15, 0.4, 0.7.
  - Differences of neighbouring ramps give soft "triangle" bins after 4×4 pooling. Each bin is the fraction of a cell made of one tissue type: air, fat, fluid, soft tissue, parenchyma, enhanced tissue or bone.
  - Every class gets a weight per bin, set from my guessed tissue fractions. These weights are converted into ramp weights, and the constant part of the air bin goes into B.
- **Filters 6–9 (edges).** These are thresholded Sobel edges in four directions (+x, −x, +y, −y). Only the interior cells are read, to avoid zero-padding artifacts. Their sum measures texture.

**What each output reads**

| Class | Evidence |
|---|---|
| Lung | Air everywhere, extra weight on air in the centre. |
| Heart | Air in the outer ring of cells, no air in the centre, bright tissue in the centre, some edges. |
| Bladder | The fluid bin, boosted in the centre. Fat counts mildly in its favour. Homogeneous texture (edges count against it). |
| Femur | Bone and muscle; edges count slightly in its favour. |
| Kidney | Enhanced tissue plus fat. |
| Liver / spleen | Homogeneous parenchyma; edges count against them. |
| Pancreas | Fat, mixed tissue, many edges. |

**Left versus right.** The array orientation is uncertain: either standard radiological display or a transposed array. In both cases the patient's right side lands in the top-left of the image. So laterality is read as top-3-rows + left-3-columns minus bottom-3-rows + right-3-columns.

- **Lungs (filter 0, non-air tissue):** tissue on the medial side means it is the opposite lung.
- **Kidneys (filter 3, bright tissue):** cortex lies on the lateral side.
- **Femurs (filter 4, bone):** the shaft lies on the lateral side.
- **Liver vs spleen (filter 2, soft tissue):** the liver is on the patient's right, the spleen on the left.

**Biases** contain the constants from the bin conversion, half-strength log class priors, and small corrections for an expected front-to-back bias in the laterality readout.

## Weights

```edits
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 0.95
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[1] = 0.7
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[2] = 0.2
CW[3, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[3] = -0.15
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[4] = -0.4
CW[5, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[5] = -0.7
CW[6, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CB[6] = -0.15
CW[7, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[7] = -0.15
CW[8, 0] = [[-0.25, -0.5, -0.25], [0, 0, 0], [0.25, 0.5, 0.25]]
CB[8] = -0.15
CW[9, 0] = [[0.25, 0.5, 0.25], [0, 0, 0], [-0.25, -0.5, -0.25]]
CB[9] = -0.15
# ---- base intensity-bin readouts (uniform over cells) ----
M[0, 0] = 0.40
M[0, 1] = 0.02
M[0, 2] = -1.049
M[0, 3] = 0.309
M[0, 4] = 0.32
M[0, 5] = 0.067
M[1:3, 0] = 0.40
M[1:3, 1] = -0.46
M[1:3, 2] = 0.231
M[1:3, 3] = -0.651
M[1:3, 4] = 0.613
M[1:3, 5] = 0.534
M[3, 0] = -0.24
M[3, 1] = 0.24
M[3, 2] = 0.057
M[3, 3] = 0.063
M[3, 4] = -0.053
M[3, 5] = -0.267
M[4:6, 0] = 0.40
M[4:6, 1] = -0.52
M[4:6, 2] = 0.12
M[4:6, 3] = 0.12
M[4:6, 4] = 0.413
M[4:6, 5] = -1.133
M[6, 0] = 0
M[6, 1] = 0.06
M[6, 2] = -0.003
M[6, 3] = 0.583
M[6, 4] = -1.207
M[6, 5] = 0.533
M[7:9, 0] = -1.28
M[7:9, 1] = 1.30
M[7:9, 2] = 0.037
M[7:9, 3] = -0.137
M[7:9, 4] = 0.08
M[7:9, 5] = 0.10
M[9, 0] = 0.56
M[9, 1] = -0.72
M[9, 2] = 0.217
M[9, 3] = -0.137
M[9, 4] = 0.013
M[9, 5] = 0
M[10, 0] = 0.12
M[10, 1] = -0.12
M[10, 2] = 0.057
M[10, 3] = 0.503
M[10, 4] = -1.06
M[10, 5] = 0.467
# ---- heart: air in outer ring, no air in centre, tissue in centre ----
M[3, 0] -= 0.48
M[3, 1] += 0.48
M[3, 0, 1:6, 1:6] += 0.48
M[3, 1, 1:6, 1:6] -= 0.48
M[3, 0, 2:5, 2:5] += 0.8
M[3, 1, 2:5, 2:5] -= 0.8
M[3, 3, 2:5, 2:5] += 0.15
# ---- lungs: air in centre ----
M[7:9, 0, 2:5, 2:5] -= 0.2
M[7:9, 1, 2:5, 2:5] += 0.2
# ---- bladder: fluid in centre ----
M[0, 1, 2:5, 2:5] += 0.2
M[0, 2, 2:5, 2:5] -= 0.486
M[0, 3, 2:5, 2:5] += 0.286
# ---- laterality (patient-right = top rows + left cols) ----
M[7, 0, 0:3] += 0.12
M[7, 0, :, 0:3] += 0.12
M[7, 0, 4:7] -= 0.12
M[7, 0, :, 4:7] -= 0.12
M[8, 0, 0:3] -= 0.12
M[8, 0, :, 0:3] -= 0.12
M[8, 0, 4:7] += 0.12
M[8, 0, :, 4:7] += 0.12
M[5, 3, 0:3] += 0.12
M[5, 3, :, 0:3] += 0.12
M[5, 3, 4:7] -= 0.12
M[5, 3, :, 4:7] -= 0.12
M[4, 3, 0:3] -= 0.12
M[4, 3, :, 0:3] -= 0.12
M[4, 3, 4:7] += 0.12
M[4, 3, :, 4:7] += 0.12
M[2, 4, 0:3] += 0.3
M[2, 4, :, 0:3] += 0.3
M[2, 4, 4:7] -= 0.3
M[2, 4, :, 4:7] -= 0.3
M[1, 4, 0:3] -= 0.3
M[1, 4, :, 0:3] -= 0.3
M[1, 4, 4:7] += 0.3
M[1, 4, :, 4:7] += 0.3
M[6, 2, 0:3] += 0.15
M[6, 2, :, 0:3] += 0.15
M[6, 2, 4:7] -= 0.15
M[6, 2, :, 4:7] -= 0.15
M[10, 2, 0:3] -= 0.15
M[10, 2, :, 0:3] -= 0.15
M[10, 2, 4:7] += 0.15
M[10, 2, :, 4:7] += 0.15
# ---- texture (edge energy, interior cells only) ----
M[0, 6:10, 1:6, 1:6] = -0.08
M[1:3, 6:10, 1:6, 1:6] = 0.04
M[3, 6:10, 1:6, 1:6] = 0.04
M[6, 6:10, 1:6, 1:6] = -0.1
M[9, 6:10, 1:6, 1:6] = 0.12
M[10, 6:10, 1:6, 1:6] = -0.1
# ---- biases ----
B[:] = [-3.63, -4.03, -3.53, 2.20, -3.45, -3.15, -2.59, 12.92, 13.72, -2.94, -2.86]
```