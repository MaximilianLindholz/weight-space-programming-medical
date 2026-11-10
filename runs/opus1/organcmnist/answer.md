# Hand-set CNN for OrganCMNIST (11 organs, coronal CT)

## Assumptions
- **Image content.** Each image is the coronal CT slice through the centre of the organ's bounding box, cropped to that box.
- **Orientation.** Head is at the top, in radiological convention: the patient's right appears on the image left.
  - For right-side organs, the medial side is the right side of the crop. For left-side organs it is the left side.
  - All left/right decisions depend on this convention. If the dataset is mirrored, the left/right pairs swap.
- **Intensity scale.** I assume a portal-venous abdominal window, so x ≈ (HU − 50)/200:
  - air −1, fat −0.75, urine −0.25, muscle 0
  - liver/spleen ≈ 0.25, renal cortex ≈ 0.6–0.8, bone 1

## Filters
| # | Kernel | Detects |
|---|---|---|
| 0 | Air: ReLU(−5x − 4.5) | Lung only (0.5 for air, 0 for fat) |
| 1 | Fat-or-air: ReLU(−x − 0.4) | Fat and air |
| 2 | ReLU(x + 0.45) | Anything at or above water density |
| 3 | ReLU(x + 0.15) | Soft tissue and brighter (urine gives 0) |
| 4 | ReLU(x − 0.4) | Bright: enhanced kidney, blood pool, bone |
| 5 | ReLU(5x − 4.5) | Bone only |
| 6, 7 | ± Laplacian, 2·(x − mean of 8 neighbours) − 0.08 | Texture and edges; read only in interior cells to avoid padding artefacts |
| 8, 9 | — | Unused |

Two filter combinations are used in the readout:
- **Water tent = f2 − 3·f3.** This peaks at urine density and is strongly negative for parenchyma and bone.
- **Parenchyma = f3 − 3·f4.** This responds to liver/spleen-like tissue but not to kidney or bone.

## Readouts
- **Bladder:** water tent over the interior, fat on the border, penalty on air.
- **Femurs:** bone (f5) and bright (f4) evidence globally. Left vs right uses a diagonal pattern: head and acetabulum at the top-medial corner, shaft at the bottom-lateral corner, soft tissue at the bottom-medial corner.
- **Kidneys:** bright (f4), with penalties on bone and air.
  - Left vs right uses the same diagonal idea: the upper pole is medial and the lower pole lateral.
  - The fat in the renal hilum sits at the medial-middle.
- **Heart:** air at the top-left and top-right (flanking lungs), tissue and blood in the centre. Air in the centre, and bone, are penalised.
- **Lungs:** air everywhere, with a penalty on tissue. Left vs right uses where the mediastinum/heart sits: soft tissue at the lower-medial side.
- **Liver / spleen:** homogeneous parenchyma with penalties on texture and air.
  - The liver crop is filled on its left (lateral) side, and the spleen's on its right.
  - Each gets a negative weight where the other organ's contents would be (bottom-medial).
- **Pancreas:** heterogeneous texture plus fat, with penalties on bright tissue, bone and air.

```edits
# ---- conv filters ----
CW[0, 0] = [[0, 0, 0], [0, -5, 0], [0, 0, 0]]
CB[0] = -4.5
CW[1, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[1] = -0.4
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[2] = 0.45
CW[3, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[3] = 0.15
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[4] = -0.4
CW[5, 0] = [[0, 0, 0], [0, 5, 0], [0, 0, 0]]
CB[5] = -4.5
CW[6, 0] = [[-0.25, -0.25, -0.25], [-0.25, 2, -0.25], [-0.25, -0.25, -0.25]]
CB[6] = -0.08
CW[7, 0] = [[0.25, 0.25, 0.25], [0.25, -2, 0.25], [0.25, 0.25, 0.25]]
CB[7] = -0.08

# ---- 0 bladder ----
M[0, 0] = -0.5
M[0, 1] = 0.2
M[0, 1, 1:6, 1:6] = 0
M[0, 2, 1:6, 1:6] = 1.0
M[0, 3, 1:6, 1:6] = -3.0

# ---- 1 femur-left (medial = crop left) ----
M[1, 5] = 0.6
M[1, 4] = 0.2
M[1, 0] = -0.3
M[1, 4, 0:3, 0:3] += 0.6
M[1, 4, 4:7, 4:7] += 0.6
M[1, 4, 0:3, 4:7] -= 0.6
M[1, 4, 4:7, 0:3] -= 0.6

# ---- 2 femur-right (medial = crop right) ----
M[2, 5] = 0.6
M[2, 4] = 0.2
M[2, 0] = -0.3
M[2, 4, 0:3, 4:7] += 0.6
M[2, 4, 4:7, 0:3] += 0.6
M[2, 4, 0:3, 0:3] -= 0.6
M[2, 4, 4:7, 4:7] -= 0.6

# ---- 3 heart ----
M[3, 0, 0:4, 0:2] = 0.8
M[3, 0, 0:4, 5:7] = 0.8
M[3, 0, 2:5, 2:5] = -0.5
M[3, 3, 1:6, 1:6] = 0.15
M[3, 4, 1:6, 1:6] = 0.2
M[3, 5] = -0.5
B[3] = -1

# ---- 4 kidney-left (medial = crop left) ----
M[4, 4] = 0.5
M[4, 5] = -1.0
M[4, 0] = -0.3
M[4, 4, 0:3, 0:3] += 0.6
M[4, 4, 4:7, 4:7] += 0.6
M[4, 4, 0:3, 4:7] -= 0.6
M[4, 4, 4:7, 0:3] -= 0.6
M[4, 1, 2:5, 0:2] = 1.0
M[4, 1, 2:5, 5:7] = -1.0

# ---- 5 kidney-right (medial = crop right) ----
M[5, 4] = 0.5
M[5, 5] = -1.0
M[5, 0] = -0.3
M[5, 4, 0:3, 4:7] += 0.6
M[5, 4, 4:7, 0:3] += 0.6
M[5, 4, 0:3, 0:3] -= 0.6
M[5, 4, 4:7, 4:7] -= 0.6
M[5, 1, 2:5, 5:7] = 1.0
M[5, 1, 2:5, 0:2] = -1.0

# ---- 6 liver (fills crop left / lateral) ----
M[6, 3, :, 0:3] = 0.5
M[6, 3, :, 3] = 0.2
M[6, 3, 0:3, 4:7] = 0.2
M[6, 3, 3:7, 4:7] = -0.3
M[6, 4, :, 0:3] = -1.5
M[6, 4, :, 3] = -0.6
M[6, 4, 0:3, 4:7] = -0.6
M[6, 0] = -0.3
M[6, 1] = -0.1
M[6, 6, 1:6, 1:6] = -0.8
M[6, 7, 1:6, 1:6] = -0.8

# ---- 7 lung-left (mediastinum at crop lower-left) ----
M[7, 0] = 0.3
M[7, 2] = -0.1
M[7, 3, 3:7, 0:3] = 0.7
M[7, 3, 3:7, 4:7] = -0.7
M[7, 0, 3:7, 4:7] += 0.3
M[7, 0, 3:7, 0:3] -= 0.3

# ---- 8 lung-right (mediastinum at crop lower-right) ----
M[8, 0] = 0.3
M[8, 2] = -0.1
M[8, 3, 3:7, 4:7] = 0.7
M[8, 3, 3:7, 0:3] = -0.7
M[8, 0, 3:7, 0:3] += 0.3
M[8, 0, 3:7, 4:7] -= 0.3

# ---- 9 pancreas ----
M[9, 1] = 0.2
M[9, 0] = -0.3
M[9, 6, 1:6, 1:6] = 1.0
M[9, 7, 1:6, 1:6] = 1.0
M[9, 3] = 0.05
M[9, 4] = -0.3
M[9, 5] = -1.0
B[9] = -0.5

# ---- 10 spleen (fills crop right / lateral) ----
M[10, 3, :, 4:7] = 0.5
M[10, 3, :, 3] = 0.2
M[10, 3, 0:3, 0:3] = 0.2
M[10, 3, 3:7, 0:3] = -0.3
M[10, 4, :, 4:7] = -1.5
M[10, 4, :, 3] = -0.6
M[10, 4, 0:3, 0:3] = -0.6
M[10, 0] = -0.15
M[10, 1] = -0.1
M[10, 6, 1:6, 1:6] = -0.8
M[10, 7, 1:6, 1:6] = -0.8
```