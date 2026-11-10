## Design

**Assumptions.** Each image is a tight crop around one organ, so the organ fills the centre of the frame and its surroundings fill the border. I don't know which way the sagittal axes are oriented after cropping, so I rely on orientation-free cues: how bright the centre is, what tissue surrounds it, and how much texture there is. I assume the abdominal window maps HU to x ≈ (HU − 40)/200, which gives:

| Tissue | x |
|---|---|
| Air | −1 |
| Fat | −0.7 |
| Urine | −0.2 |
| Muscle | 0.1 |
| Enhanced liver / spleen | 0.3–0.4 |
| Heart blood / kidney cortex | 0.5–0.8 |
| Bone | 1 (saturated) |

**Filters**
- **f0–f6: intensity histogram.** Each uses an identity kernel and computes ReLU(x − t) for t = −0.9, −0.6, −0.3, 0, 0.3, 0.6, 0.85. Averaged over a region, any linear combination of these gives the region mean of a piecewise-linear "intensity score" f(x). So each class gets a soft histogram template over air, fat, water, soft tissue, enhanced tissue and bone.
- **f7 / f8: texture.** ReLU(+Laplacian) and ReLU(−Laplacian) (centre 1, four neighbours −0.25). Their sum is |Laplacian|, a texture and edge measure. They are read only in the interior cells 1..5 to avoid zero-padding artefacts at the border.
- **f9: saturated white.** ReLU(x − 0.92), i.e. cortical bone.

**Outputs.** For each class I specified f(x) at the breakpoints, separately for two regions:
- **Centre:** cells 2..4 × 2..4, the organ itself.
- **Periphery:** the other 40 cells, the surroundings, weighted 0.7.

Slope changes become the M weights, divided by the number of cells in the region so each region contributes a mean. The constant term of each template goes into B.

What each class reads:
- **Lung:** air in the centre.
- **Femur:** bright or saturated bone in the centre, plus texture.
- **Bladder:** water-grey, smooth centre surrounded by fat.
- **Kidney:** bright cortex with sinus fat in the centre, perirenal fat around it, and no saturated bone.
- **Heart:** enhanced grey centre with lung air and fat around it.
- **Liver:** uniform grey (about 0.3) almost everywhere, little texture, a little air at the border.
- **Spleen:** like liver but slightly brighter, with more mixed surroundings.
- **Pancreas:** mixed fat and grey, high texture, vessels and fat around it.

**Known limits.** I can't separate left from right organs in a sagittal view, so each left/right pair gets identical weights.

```edits
# ---- filters ----
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 0.9
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[1] = 0.6
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[2] = 0.3
CW[3, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[3] = 0
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[4] = -0.3
CW[5, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[5] = -0.6
CW[6, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[6] = -0.85
CW[7, 0] = [[0, -0.25, 0], [-0.25, 1, -0.25], [0, -0.25, 0]]
CB[7] = 0
CW[8, 0] = [[0, 0.25, 0], [0.25, -1, 0.25], [0, 0.25, 0]]
CB[8] = 0
CW[9, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[9] = -0.92

# ---- bladder (0) ----
M[0, 0] = 0.1167
M[0, 1] = -0.1458
M[0, 5] = 0.0642
M[0, 6] = -0.035
M[0, 1, 2:5, 2:5] = 1.111
M[0, 2, 2:5, 2:5] = -1.111
M[0, 3, 2:5, 2:5] = -1.111
M[0, 4, 2:5, 2:5] = 0.741
M[0, 5, 2:5, 2:5] = 0.370
M[0, 6, 2:5, 2:5] = 0
M[0, 0, 2:5, 2:5] = 0

# ---- femur left/right (1,2) ----
M[1:3, 0] = 0.0875
M[1:3, 1] = -0.1458
M[1:3, 2] = 0.0875
M[1:3, 3] = -0.0292
M[1:3, 5] = 0.07
M[1:3, 6] = -0.07
M[1:3, 0, 2:5, 2:5] = 0
M[1:3, 1, 2:5, 2:5] = 0
M[1:3, 2, 2:5, 2:5] = 0
M[1:3, 3, 2:5, 2:5] = 0
M[1:3, 4, 2:5, 2:5] = 0.556
M[1:3, 5, 2:5, 2:5] = 0.111
M[1:3, 6, 2:5, 2:5] = 0.074

# ---- heart (3) ----
M[3, 0] = -0.0583
M[3, 2] = 0.0583
M[3, 3] = 0.0292
M[3, 4] = -0.0292
M[3, 5] = -0.07
M[3, 6] = 0.07
M[3, 0, 2:5, 2:5] = 0
M[3, 2, 2:5, 2:5] = 0.370
M[3, 3, 2:5, 2:5] = 0.185
M[3, 4, 2:5, 2:5] = -0.370
M[3, 5, 2:5, 2:5] = -1.074
M[3, 6, 2:5, 2:5] = 0.148

# ---- kidney left/right (4,5) ----
M[4:6, 0] = 0.1458
M[4:6, 1] = -0.2333
M[4:6, 2] = 0.0875
M[4:6, 5] = -0.035
M[4:6, 6] = -0.0233
M[4:6, 0, 2:5, 2:5] = 0.741
M[4:6, 1, 2:5, 2:5] = -1.111
M[4:6, 2, 2:5, 2:5] = 0.370
M[4:6, 3, 2:5, 2:5] = 0.370
M[4:6, 4, 2:5, 2:5] = 0.370
M[4:6, 5, 2:5, 2:5] = -0.741
M[4:6, 6, 2:5, 2:5] = -2.222

# ---- liver (6) ----
M[6, 0] = -0.0583
M[6, 1] = 0.0583
M[6, 2] = 0.0583
M[6, 3] = 0.0292
M[6, 4] = -0.175
M[6, 5] = 0.0175
M[6, 6] = 0.07
M[6, 0, 2:5, 2:5] = 0
M[6, 1, 2:5, 2:5] = 0.370
M[6, 2, 2:5, 2:5] = 0.185
M[6, 3, 2:5, 2:5] = 0
M[6, 4, 2:5, 2:5] = -1.111
M[6, 5, 2:5, 2:5] = -0.111
M[6, 6, 2:5, 2:5] = -0.074

# ---- lung left/right (7,8) ----
M[7:9, 0] = -0.0875
M[7:9, 1] = 0.0583
M[7:9, 2] = 0.0292
M[7:9, 4] = -0.0292
M[7:9, 5] = 0.0292
M[7:9, 0, 2:5, 2:5] = -1.111
M[7:9, 1, 2:5, 2:5] = 0.741
M[7:9, 2, 2:5, 2:5] = 0.370
M[7:9, 4, 2:5, 2:5] = 0
M[7:9, 5, 2:5, 2:5] = 0

# ---- pancreas (9) ----
M[9, 0] = 0.0583
M[9, 1] = -0.1167
M[9, 2] = 0.0583
M[9, 3] = 0.0292
M[9, 4] = -0.0292
M[9, 5] = -0.07
M[9, 6] = 0.0117
M[9, 0, 2:5, 2:5] = 0.556
M[9, 1, 2:5, 2:5] = -0.556
M[9, 2, 2:5, 2:5] = 0.185
M[9, 3, 2:5, 2:5] = -0.185
M[9, 4, 2:5, 2:5] = -0.370
M[9, 5, 2:5, 2:5] = 0.148
M[9, 6, 2:5, 2:5] = -0.148

# ---- spleen (10) ----
M[10, 1] = -0.0583
M[10, 2] = 0.0875
M[10, 3] = 0.0292
M[10, 4] = -0.0875
M[10, 5] = -0.0758
M[10, 6] = 0.105
M[10, 1, 2:5, 2:5] = 0.370
M[10, 2, 2:5, 2:5] = 0
M[10, 3, 2:5, 2:5] = 0.370
M[10, 4, 2:5, 2:5] = -0.926
M[10, 5, 2:5, 2:5] = -0.926
M[10, 6, 2:5, 2:5] = 0.370

# ---- saturated bone (f9) ----
M[1:3, 9] = 0.33
M[1:3, 9, 2:5, 2:5] = 2.78
M[4:6, 9, 2:5, 2:5] = -2.08
M[3, 9, 2:5, 2:5] = -1.39
M[6, 9, 2:5, 2:5] = -1.39
M[10, 9, 2:5, 2:5] = -1.39

# ---- texture |Laplacian| (f7 + f8), interior cells ----
M[9, 7:9, 1:6, 1:6] = 0.4
M[1:3, 7:9, 1:6, 1:6] = 0.24
M[4:6, 7:9, 1:6, 1:6] = 0.16
M[7:9, 7:9, 1:6, 1:6] = 0.12
M[6, 7:9, 1:6, 1:6] = -0.24
M[10, 7:9, 1:6, 1:6] = -0.12
M[0, 7:9, 1:6, 1:6] = -0.24

# ---- biases (template constants + small prior) ----
B[:] = [0, 0, 0, 1.75, -1, -1, 0, 5.75, 5.75, 0.7, 0.05]
```