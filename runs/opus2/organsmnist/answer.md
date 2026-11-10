# Hand-set weights for OrganSMNIST: intensity bands plus a center-versus-border layout

## Design

None of these numbers have been run or tested. The class prototypes below are my estimates of what each organ crop looks like, not measurements.

**Assumptions.** Each image is the organ's bounding-box crop, resized to 28×28. It is contrast CT shown in an abdominal window, so x ≈ (HU − 50)/200 clipped to [−1, 1]. Expected intensities:

| Tissue | Approx. HU | Approx. x |
|---|---|---|
| Air | | −1 |
| Fat | ≈ −100 | ≈ −0.75 |
| Urine or water | ≈ 0 | ≈ −0.25 |
| Liver or spleen | | ≈ 0.3 |
| Kidney cortex or heart blood pool | | 0.5–0.7 |
| Bone | | saturated at +1 |

**Filters (centre-only kernels, so zero padding has no effect):**

| Filter | Formula | Role |
|---|---|---|
| k0 | ReLU(−6.67x − 5.67) | Air indicator: 1 at x = −1, 0 above −0.85 |
| k1 | ReLU(−2x − 1) | Dark ramp. Fat-only = 1.43·(k1 − k0) |
| k2, k3 | ReLU(−x − 0.25), ReLU(−x) | Water triangle W = 4k3 − 8k2 + 2k1, peaking at x = −0.25. This is the bladder signal. |
| k4, k5 | ReLU(2.5x − 0.125), ReLU(2.5x − 1.125) | Tissue step T = k4 − k5 (soft tissue or brighter). "High" step H = k5 − 0.375·k6 (enhanced kidney, heart blood, bone). |
| k6 | ReLU(6.67x − 5.67) | Bone indicator |
| k7, k8 | ±Laplacian (centre 4, neighbours −0.5, bias −0.4) | Bright and dark texture/edges. Used for pancreas heterogeneity. |
| k9 | unused | |

**Readout.** Because the readout is linear, these filter combinations are exact piecewise-linear intensity histograms. Each class reads them in two regions: the inner 5×5 pooled cells and the outer ring. The 25 inner cells are weighted ×0.04 and the 24 ring cells ×0.042, which turns them into fractions.

| Class | Evidence used |
|---|---|
| Lung (L and R) | Lots of air in the inner region (9) and the ring (3); a little less if the centre is bright |
| Heart | Air in the ring (lung around it), tissue in the centre, bright blood pool in the centre. Penalised by fat, water and bone. |
| Liver | Tissue in both the centre and the ring (the organ fills the box). Homogeneous, so texture counts against it. Little fat, air or bright signal. Prior bias +0.6. |
| Spleen | Tissue in the centre with a less-filled ring (fat, air, ribs) |
| Kidney (L and R) | Bright enhanced centre with perirenal fat in the ring. No bone or air. |
| Pancreas | Fat mixed into the centre, tissue, texture and some fluid |
| Bladder | Water in the centre (6) and the ring (2), fat around it, little tissue |
| Femur (L and R) | Bone fraction, centre (12) and ring (6) |

**Limitations.**
- The left and right twins (lungs, kidneys, femurs) get identical evidence. My network cannot tell them apart, apart from a small prior favouring the right lung. Expect roughly coin-flip accuracy within each pair.
- Liver versus spleen relies only on how well tissue fills the ring, so expect confusion there too.
- Scans without contrast would put liver and kidney intensities lower than assumed, which would weaken the tissue and "high" signals.

```edits
# ---- conv filters (centre-only intensity bands) ----
CW[0, 0] = [[0, 0, 0], [0, -6.667, 0], [0, 0, 0]]
CB[0] = -5.667
CW[1, 0] = [[0, 0, 0], [0, -2, 0], [0, 0, 0]]
CB[1] = -1
CW[2, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[2] = -0.25
CW[3, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[3] = 0
CW[4, 0] = [[0, 0, 0], [0, 2.5, 0], [0, 0, 0]]
CB[4] = -0.125
CW[5, 0] = [[0, 0, 0], [0, 2.5, 0], [0, 0, 0]]
CB[5] = -1.125
CW[6, 0] = [[0, 0, 0], [0, 6.667, 0], [0, 0, 0]]
CB[6] = -5.667
# texture: +/- Laplacian
CW[7, 0] = [[-0.5, -0.5, -0.5], [-0.5, 4, -0.5], [-0.5, -0.5, -0.5]]
CB[7] = -0.4
CW[8, 0] = [[0.5, 0.5, 0.5], [0.5, -4, 0.5], [0.5, 0.5, 0.5]]
CB[8] = -0.4

# ---- lungs (7, 8) ----
M[7:9, 0] = 0.125
M[7:9, 0, 1:6, 1:6] = 0.36
M[7:9, 5, 1:6, 1:6] = -0.08
M[7:9, 6, 1:6, 1:6] = 0.03

# ---- heart (3) ----
M[3, 0] = 0.1667
M[3, 0, 1:6, 1:6] = 0.1543
M[3, 1, 1:6, 1:6] = -0.2743
M[3, 2, 1:6, 1:6] = 0.64
M[3, 3, 1:6, 1:6] = -0.32
M[3, 4, 1:6, 1:6] = 0.08
M[3, 5, 1:6, 1:6] = 0.08
M[3, 6, 1:6, 1:6] = -0.18

# ---- liver (6) ----
M[6, 0] = 0.0893
M[6, 1] = -0.0893
M[6, 4] = 0.125
M[6, 5] = -0.125
M[6, 0, 1:6, 1:6] = 0.0343
M[6, 1, 1:6, 1:6] = -0.2743
M[6, 2, 1:6, 1:6] = 0.64
M[6, 3, 1:6, 1:6] = -0.32
M[6, 4, 1:6, 1:6] = 0.12
M[6, 5, 1:6, 1:6] = -0.18
M[6, 6, 1:6, 1:6] = -0.0975
M[6, 7, 1:6, 1:6] = -0.04
M[6, 8, 1:6, 1:6] = -0.04

# ---- spleen (10) ----
M[10, 0] = -0.0179
M[10, 1] = 0.0595
M[10, 4] = 0.0417
M[10, 5] = -0.0417
M[10, 6] = 0.0417
M[10, 0, 1:6, 1:6] = 0.0343
M[10, 1, 1:6, 1:6] = -0.2743
M[10, 2, 1:6, 1:6] = 0.64
M[10, 3, 1:6, 1:6] = -0.32
M[10, 4, 1:6, 1:6] = 0.12
M[10, 5, 1:6, 1:6] = -0.12
M[10, 6, 1:6, 1:6] = -0.12
M[10, 7, 1:6, 1:6] = -0.02
M[10, 8, 1:6, 1:6] = -0.02

# ---- kidneys (4, 5) ----
M[4:6, 0] = -0.2202
M[4:6, 1] = 0.1786
M[4:6, 0, 1:6, 1:6] = 0.0343
M[4:6, 1, 1:6, 1:6] = -0.2743
M[4:6, 2, 1:6, 1:6] = 0.64
M[4:6, 3, 1:6, 1:6] = -0.32
M[4:6, 4, 1:6, 1:6] = 0.08
M[4:6, 5, 1:6, 1:6] = 0.08
M[4:6, 6, 1:6, 1:6] = -0.22

# ---- pancreas (9) ----
M[9, 0] = -0.1012
M[9, 1] = 0.0595
M[9, 0, 1:6, 1:6] = -0.3086
M[9, 1, 1:6, 1:6] = 0.3086
M[9, 2, 1:6, 1:6] = -0.32
M[9, 3, 1:6, 1:6] = 0.16
M[9, 4, 1:6, 1:6] = 0.08
M[9, 5, 1:6, 1:6] = -0.12
M[9, 6, 1:6, 1:6] = 0.015
M[9, 7, 1:6, 1:6] = 0.06
M[9, 8, 1:6, 1:6] = 0.06

# ---- bladder (0) ----
M[0, 0] = -0.0595
M[0, 1] = 0.2262
M[0, 2] = -0.6667
M[0, 3] = 0.3333
M[0, 0, 1:6, 1:6] = -0.08
M[0, 1, 1:6, 1:6] = 0.48
M[0, 2, 1:6, 1:6] = -1.92
M[0, 3, 1:6, 1:6] = 0.96
M[0, 4, 1:6, 1:6] = -0.08
M[0, 5, 1:6, 1:6] = 0.08

# ---- femurs (1, 2) ----
M[1:3, 0] = -0.0595
M[1:3, 1] = 0.0595
M[1:3, 6] = 0.25
M[1:3, 0, 1:6, 1:6] = -0.08
M[1:3, 6, 1:6, 1:6] = 0.48

# ---- biases (rough priors) ----
B[6] = 0.6
B[9] = 0.5
B[3] = -0.3
B[8] = 0.2
B[7] = -0.2
```