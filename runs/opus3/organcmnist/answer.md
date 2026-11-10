# Hand-set CNN weights for OrganCMNIST (11-class organ classification)

## Design

**Assumptions about pixel values.** I assume an abdominal CT window of roughly [-150, 250] HU. Under that window, x ≈ (HU − 50)/200, which gives these tissue values:

| Tissue | x |
|---|---|
| Lung and air | -1 |
| Fat | about -0.75 |
| Urine (bladder) | about -0.2 |
| Muscle | about 0 |
| Liver and spleen (contrast-enhanced) | about 0.3 |
| Kidney and blood pool | 0.5 to 0.75 |
| Bone | +1 |

**Orientation.** I am not sure about the image orientation. The volume may be rotated by 90° or flipped. So every class template uses only rotation-invariant regions:

- **Center:** grid cells 2–4 × 2–4.
- **Ring:** the remaining 40 cells.
- **Interior:** cells 1–5 × 1–5, used only for the texture filters.

For the same reason, I make no left/right guess. The two classes in each pair (femur, kidney, lung) get identical scores. A wrong guess on chirality would cost as much as a right guess would gain.

**Filters.** Filters 0–6 use the center tap only. Filters 7–8 are 3×3 Laplacians.

| Filter | Formula | What it responds to |
|---|---|---|
| 0, AIR | ReLU(-8x-7) | 1 on lung/air, 0 above -0.875 |
| 1, DARK | ReLU(-2x-1) | fat and air; fat ≈ 2·(g1−g0) |
| 2 | ReLU(x+0.45) | intensity ramp |
| 3 | ReLU(x+0.2) | intensity ramp |
| 4 | ReLU(x−0.05) | intensity ramp |
| 5 | ReLU(x−0.45) | intensity ramp |
| 6, BONE | ReLU(8x−7) | saturated bone |
| 7 | positive Laplacian, threshold 0.4 | bright edges and spots |
| 8 | negative Laplacian, threshold 0.4 | dark edges and spots |
| 9 | unused | — |

**Derived per-pixel features.** These are linear combinations of the filters above:

- **FLUID** = 4·g2 − 8·g3 + 4·g4. This is a peak centered at x = -0.2.
- **TISSUE** = 4·g3 − 4·g4 − 2.5·g5. It responds to muscle and liver.
- **ENH** = 4·g5. It responds to kidney, contrast-filled vessels and bone.
- **TEX** = g7 + g8. It measures local texture.

**What each output reads.**

| Class | Positive evidence | Negative evidence |
|---|---|---|
| Lung (both sides) | air in the center (strongly), air in the ring | — |
| Heart | air in the ring, enhanced tissue in the center | air in the center |
| Liver | homogeneous tissue in both center and ring | fat, air, very bright pixels, texture |
| Spleen | tissue in the center; some fat and air in the ring | air in the center, enhancement in the center |
| Kidney (both sides) | bright enhanced tissue in the center, fat in the ring | air, bone |
| Pancreas | fat in the center, mixed tissue, high texture | fluid, enhancement, bone |
| Bladder | fluid in the center, fat in the ring | tissue in the center, air, bone |
| Femur (both sides) | bone anywhere, texture | — |

## Weights

```edits
# ---- filters ----
CW[0, 0] = [[0, 0, 0], [0, -8, 0], [0, 0, 0]]
CB[0] = -7
CW[1, 0] = [[0, 0, 0], [0, -2, 0], [0, 0, 0]]
CB[1] = -1
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[2] = 0.45
CW[3, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[3] = 0.2
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[4] = -0.05
CW[5, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[5] = -0.45
CW[6, 0] = [[0, 0, 0], [0, 8, 0], [0, 0, 0]]
CB[6] = -7
CW[7, 0] = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
CB[7] = -0.4
CW[8, 0] = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
CB[8] = -0.4

# ---- class 0 bladder ----
M[0, 0, :, :] = -0.175
M[0, 0, 2:5, 2:5] = -0.444
M[0, 1, :, :] = 0.1
M[0, 1, 2:5, 2:5] = 0
M[0, 2, 2:5, 2:5] = 2.667
M[0, 3, 2:5, 2:5] = -6.667
M[0, 4, 2:5, 2:5] = 4.0
M[0, 5, 2:5, 2:5] = 0.833
M[0, 6, :, :] = -0.041
B[0] = 0

# ---- classes 1,2 femur ----
M[1:3, 6, :, :] = 0.306
M[1:3, 7, 1:6, 1:6] = 0.04
M[1:3, 8, 1:6, 1:6] = 0.04
B[1:3] = -0.5

# ---- class 3 heart ----
M[3, 0, :, :] = 0.15
M[3, 0, 2:5, 2:5] = -0.889
M[3, 3, 2:5, 2:5] = 1.333
M[3, 4, 2:5, 2:5] = -1.333
M[3, 5, 2:5, 2:5] = 0.056
B[3] = -1

# ---- classes 4,5 kidney ----
M[4:6, 0, :, :] = -0.2
M[4:6, 0, 2:5, 2:5] = -0.444
M[4:6, 1, :, :] = 0.15
M[4:6, 1, 2:5, 2:5] = 0
M[4:6, 5, 2:5, 2:5] = 2.667
M[4:6, 6, :, :] = -0.163
B[4:6] = -1

# ---- class 6 liver ----
M[6, 0, :, :] = 0.125
M[6, 0, 2:5, 2:5] = 0.444
M[6, 1, :, :] = -0.2
M[6, 1, 2:5, 2:5] = -0.444
M[6, 3, :, :] = 0.3
M[6, 3, 2:5, 2:5] = 1.333
M[6, 4, :, :] = -0.3
M[6, 4, 2:5, 2:5] = -1.333
M[6, 5, :, :] = -0.1875
M[6, 5, 2:5, 2:5] = -2.167
M[6, 7, 1:6, 1:6] = -0.08
M[6, 8, 1:6, 1:6] = -0.08
B[6] = 0

# ---- classes 7,8 lung ----
M[7:9, 0, :, :] = 0.075
M[7:9, 0, 2:5, 2:5] = 0.889
B[7:9] = -2

# ---- class 9 pancreas ----
M[9, 0, :, :] = -0.1
M[9, 0, 2:5, 2:5] = -2.111
M[9, 1, :, :] = 0.1
M[9, 1, 2:5, 2:5] = 1.778
M[9, 2, 2:5, 2:5] = -1.333
M[9, 3, 2:5, 2:5] = 3.333
M[9, 4, 2:5, 2:5] = -2.0
M[9, 5, 2:5, 2:5] = -1.306
M[9, 6, :, :] = -0.082
M[9, 7, 1:6, 1:6] = 0.12
M[9, 8, 1:6, 1:6] = 0.12
B[9] = 0

# ---- class 10 spleen ----
M[10, 0, :, :] = -0.05
M[10, 0, 2:5, 2:5] = -0.222
M[10, 1, :, :] = 0.1
M[10, 1, 2:5, 2:5] = -0.444
M[10, 3, :, :] = 0.1
M[10, 3, 2:5, 2:5] = 1.333
M[10, 4, :, :] = -0.1
M[10, 4, 2:5, 2:5] = -1.333
M[10, 5, :, :] = -0.0625
M[10, 5, 2:5, 2:5] = -2.167
B[10] = 0
```