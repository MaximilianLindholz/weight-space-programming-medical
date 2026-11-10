This is an **unvalidated anatomical heuristic**, not a substitute for learned weights. At 28×28, especially for nodules and fibrosis, reliable discrimination may be impossible from these features alone.

**Filters:** 0 measures brightness; 1 detects smoothed bright opacity; 2 detects smoothed darkness; 3 detects local bright curvature; 4–5 measure curvature anisotropy, allowing the readout to discount line-like responses when seeking blobs; 6–7 detect opposite horizontal brightness transitions; 8 detects horizontal bright bands; 9 detects downward brightening.

**Spatial evidence:** pooled columns 1–2 and 4–5 approximate the lungs. References in upper lung fields or central column 3 reduce exposure sensitivity.

| Outputs | Main evidence |
|---|---|
| Atelectasis | Basal opacity and horizontal bands |
| Cardiomegaly | Lower cardiac silhouette width and outward-shifted borders |
| Effusion | Smooth basal/lateral opacity, reduced basal darkness |
| Infiltration | Broad mid/lower-lung opacity and texture |
| Mass, nodule | Focal brightness and blob-like curvature; reduced cardiac-region weight |
| Pneumonia, consolidation | Mid/basal opacity relative to upper lungs and mediastinum |
| Pneumothorax | Peripheral upper-lung darkness, fewer markings, medial pleural-edge evidence |
| Edema | Perihilar opacity relative to peripheral lungs, plus basal opacity |
| Emphysema | Diffuse lucency, reduced markings, lower diaphragm evidence |
| Fibrosis | Predominantly basal texture and bands |
| Pleural | Apical/peripheral thickening and boundary contrast |
| Hernia | Lower-central/retrocardiac lucency, surrounding brightness, rounded edges |

Biases approximate label rarity. The final scaling preserves ranking—and therefore AUC—while keeping every logit negative. Thus thresholded ACC deliberately uses the all-negative baseline rather than unsupported positive decisions; the handcrafted features only attempt to improve ranking.

```edits
# Convolutional features
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[1, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]
CW[2, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CW[3, 0] = [[0, -0.25, 0], [-0.25, 1, -0.25], [0, -0.25, 0]]
CW[4, 0] = [[0, -0.25, 0], [0.25, 0, 0.25], [0, -0.25, 0]]
CW[5, 0] = [[0, 0.25, 0], [-0.25, 0, -0.25], [0, 0.25, 0]]
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[8, 0] = [[-0.125, -0.25, -0.125], [0.25, 0.5, 0.25], [-0.125, -0.25, -0.125]]
CW[9, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CB[:] = [1, -0.05, -0.3, 0, 0, 0, 0, 0, 0, 0]

# 0: Atelectasis
M[0, 0, 4:6, 1:3] = 0.18
M[0, 0, 4:6, 5] = 0.18
M[0, 0, 3, 1:3] = 0.08
M[0, 0, 3, 4:6] = 0.06
M[0, 0, 4, 4] = 0.08
M[0, 0, 1:3, 1:3] = -0.18
M[0, 0, 1:3, 4:6] = -0.18
M[0, 1, 4:6, 1:3] = 0.12
M[0, 1, 4:6, 5] = 0.12
M[0, 1, 3:5, 4] = 0.06
M[0, 1, 1:3, 1:3] = -0.105
M[0, 1, 1:3, 4:6] = -0.105
M[0, 8, 3:5, 1:3] = 0.18
M[0, 8, 3:5, 4:6] = 0.12
M[0, 8, 1:3, 1:3] = -0.06
M[0, 8, 1:3, 4:6] = -0.06

# 1: Cardiomegaly
M[1, 0, 3] = [0, -0.1, 0.2, 0, 0.2, 0.05, 0]
M[1, 0, 4] = [0, -0.1, 0.25, 0, 0.3, 0.15, 0]
M[1, 0, 5] = [0, 0, 0.1, 0, 0.1, 0.05, 0]
M[1, 0, 1:3, 1:3] = -0.15
M[1, 0, 1:3, 4:6] = -0.15
M[1, 1, 3:5, 2] = 0.14
M[1, 1, 3:5, 4] = 0.16
M[1, 1, 3:5, 5] = 0.1
M[1, 1, 1:3, 1:3] = -0.1
M[1, 1, 1:3, 4:6] = -0.1
M[1, 6, 3:5, 2] = 0.1
M[1, 6, 3:5, 3] = -0.1
M[1, 7, 3:5, 5] = 0.16
M[1, 7, 3:5, 4] = -0.08
M[1, 7, 3:5, 3] = -0.08

# 2: Effusion
M[2, 0, 3] = [0, 0.06, 0.06, 0, 0, 0.06, 0]
M[2, 0, 4] = [0, 0.18, 0.18, 0, 0.06, 0.18, 0]
M[2, 0, 5] = [0, 0.2, 0.2, 0, 0.06, 0.2, 0]
M[2, 0, 1:3, 1:3] = -0.18
M[2, 0, 1:3, 4:6] = -0.18
M[2, 1, 4:6, 1:3] = 0.18
M[2, 1, 4:6, 5] = 0.18
M[2, 1, 4:6, 4] = 0.06
M[2, 1, 1:3, 1:3] = -0.15
M[2, 1, 1:3, 4:6] = -0.15
M[2, 2, 4:6, 1:3] = -0.08
M[2, 2, 4:6, 5] = -0.08
M[2, 2, 1:3, 1:3] = 0.06
M[2, 2, 1:3, 4:6] = 0.06
M[2, 3, 4:6, 1:3] = -0.04
M[2, 3, 4:6, 5] = -0.04
M[2, 3, 1:3, 1:3] = 0.03
M[2, 3, 1:3, 4:6] = 0.03

# 3: Infiltration
M[3, 0, 2:5, 1:6] = 0.1
M[3, 0, 5, 1:3] = 0.1
M[3, 0, 5, 5] = 0.1
M[3, 0, 1:6, 3] = -0.3
M[3, 1, 2:5, 1:6] = 0.08
M[3, 1, 5, 1:3] = 0.08
M[3, 1, 5, 5] = 0.08
M[3, 1, 1:6, 3] = -0.24
M[3, 3, 2:5, 1:6] = 0.06
M[3, 3, 2:5, 3] = 0
M[3, 8, 2:5, 1:6] = 0.03
M[3, 8, 2:5, 3] = 0
M[3, 2, 2:5, 1:6] = -0.04
M[3, 2, 2:5, 3] = 0

# 4: Mass
M[4, 0, 1:5, 1:6] = -0.03
M[4, 0, 1:5, 3] = 0.12
M[4, 1, 1:5, 1:6] = 0.12
M[4, 1, 1:5, 3] = -0.48
M[4, 3:6, 1:5, 1:6] = -0.14
M[4, 3, 1:5, 1:6] = 0.35
M[4, 3:6, 1:5, 3] = 0
M[4, :, 4, 4] *= 0.4

# 5: Nodule
M[5, 0, 1:5, 1:6] = -0.01
M[5, 0, 1:5, 3] = 0.04
M[5, 1, 1:5, 1:6] = 0.04
M[5, 1, 1:5, 3] = -0.16
M[5, 3:6, 1:5, 1:6] = -0.23
M[5, 3, 1:5, 1:6] = 0.5
M[5, 3:6, 1:5, 3] = 0
M[5, 3:6, 5, 1:3] = -0.092
M[5, 3, 5, 1:3] = 0.2
M[5, 3:6, 5, 5] = -0.092
M[5, 3, 5, 5] = 0.2
M[5, :, 4, 4] *= 0.25

# 6: Pneumonia
M[6, 0, 2:5, 1:6] = 0.05
M[6, 0, 2:5, 3] = 0
M[6, 0, 5, 1:3] = 0.1
M[6, 0, 5, 5] = 0.1
M[6, 0, 1, 1:3] = -0.075
M[6, 0, 1, 4:6] = -0.075
M[6, 0, 1:4, 3] = -0.2
M[6, 1, 2:5, 1:6] = 0.1
M[6, 1, 2:5, 3] = 0
M[6, 1, 5, 1:3] = 0.2
M[6, 1, 5, 5] = 0.2
M[6, 1, 1, 1:3] = -0.15
M[6, 1, 1, 4:6] = -0.15
M[6, 1, 1:4, 3] = -0.4
M[6, 3, 2:5, 1:6] = 0.04
M[6, 3, 2:5, 3] = 0
M[6, 8, 3:5, 1:3] = 0.02
M[6, 8, 3:5, 4:6] = 0.02

# 7: Pneumothorax
M[7, 0, 1:4, 1:6:4] = -0.2
M[7, 0, 1:4, 2:5:2] = 0.2
M[7, 2, 1:4, 1:6:4] = 0.3
M[7, 2, 1:4, 2:5:2] = -0.12
M[7, 3, 1:4, 1:6:4] = -0.16
M[7, 3, 1:4, 2:5:2] = 0.04
M[7, 6, 1:4, 2] = 0.12
M[7, 6, 1:4, 1] = 0.05
M[7, 7, 1:4, 4] = 0.12
M[7, 7, 1:4, 5] = 0.05

# 8: Consolidation
M[8, 0, 2:5, 1:6] = 0.06
M[8, 0, 2:5, 3] = 0
M[8, 0, 5, 1:3] = 0.12
M[8, 0, 5, 5] = 0.12
M[8, 0, 1, 1:3] = -0.09
M[8, 0, 1, 4:6] = -0.09
M[8, 0, 1:4, 3] = -0.24
M[8, 1, 2:5, 1:6] = 0.16
M[8, 1, 2:5, 3] = 0
M[8, 1, 5, 1:3] = 0.24
M[8, 1, 5, 5] = 0.24
M[8, 1, 1, 1:3] = -0.18
M[8, 1, 1, 4:6] = -0.18
M[8, 1, 1:4, 3] = -0.64
M[8, 3, 2:5, 1:6] = -0.02
M[8, 3, 2:5, 3] = 0
M[8, 2, 2:5, 1:6] = -0.06
M[8, 2, 2:5, 3] = 0
M[8, 2, 5, 1:3] = -0.1
M[8, 2, 5, 5] = -0.1
M[8, 2, 1, 1:3] = 0.09
M[8, 2, 1, 4:6] = 0.09

# 9: Edema
M[9, 0, 2:4, 2:5:2] = 0.22
M[9, 0, 2:4, 1:6:4] = -0.18
M[9, 0, 4, 2:5:2] = 0.2
M[9, 0, 4, 1:6:4] = 0.08
M[9, 0, 5, 1:3] = 0.1
M[9, 0, 5, 5] = 0.1
M[9, 0, 1, 1:3] = -0.18
M[9, 0, 1, 4:6] = -0.18
M[9, 0, 1:4, 3] = -0.1
M[9, 1, 2:5, 2:5:2] = 0.2
M[9, 1, 2:4, 1:6:4] = -0.15
M[9, 1, 4:6, 1:6:4] = 0.1
M[9, 1, 5, 2] = 0.1
M[9, 1, 1, 1:3] = -0.2
M[9, 1, 1, 4:6] = -0.2
M[9, 1, 1:4, 3] = -0.1
M[9, 8, 3:5, 1:6:4] = 0.06

# 10: Emphysema
M[10, 0, 1:5, 1:6] = -0.1
M[10, 0, 1:5, 3] = 0.52
M[10, 0, 5, 1:3] = -0.16
M[10, 0, 5, 5] = -0.16
M[10, 2, 1:5, 1:6] = 0.15
M[10, 2, 1:5, 3] = -0.12
M[10, 2, 5, 1:3] = 0.2
M[10, 2, 5, 5] = 0.2
M[10, 3, 1:5, 1:6] = -0.08
M[10, 3, 1:5, 3] = 0
M[10, 8, 1:5, 1:6] = -0.025
M[10, 8, 1:5, 3] = 0
M[10, 9, 4, 1:3] = -0.08
M[10, 9, 4, 4:6] = -0.08
M[10, 9, 5, 1:3] = 0.08
M[10, 9, 5, 5] = 0.08
M[10, 9, 6, 1:3] = 0.04
M[10, 9, 6, 5] = 0.04

# 11: Fibrosis
M[11, 3, 2:6, 1:3] = 0.18
M[11, 3, 2:6, 4:6] = 0.14
M[11, 3, 1, 1:3] = -0.05
M[11, 3, 1, 4:6] = -0.05
M[11, 4:6, 2:6, 1:3] = 0.04
M[11, 4:6, 2:6, 4:6] = 0.04
M[11, 8, 3:6, 1:3] = 0.12
M[11, 8, 3:6, 4:6] = 0.1
M[11, 0, 3:5, 1:3] = 0.04
M[11, 0, 3:5, 5] = 0.04
M[11, 0, 5, 1:3] = 0.08
M[11, 0, 5, 5] = 0.08
M[11, 0, 1:3, 1:3] = -0.06
M[11, 0, 1:3, 4:6] = -0.06
M[11, 3:9, 3:6, 4] *= 0.5

# 12: Pleural thickening
M[12, 0, 1:5, 1:6:4] = 0.16
M[12, 0, 1:5, 2:5:2] = -0.16
M[12, 1, 1:5, 1:6:4] = 0.14
M[12, 1, 1:5, 2:5:2] = -0.14
M[12, 3, 1:5, 1:6:4] = 0.14
M[12, 3, 1:5, 2:5:2] = -0.04
M[12, 8, 1, 1:3] = 0.12
M[12, 8, 1, 4:6] = 0.12
M[12, 7, 1:5, 1] = 0.06
M[12, 6, 1:5, 5] = 0.06

# 13: Hernia
M[13, 2, 4:6, 3] = 0.45
M[13, 2, 4:6, 4] = 0.3
M[13, 2, 3, 3:5] = -0.2
M[13, 2, 6, 3:5] = -0.2
M[13, 0, 4:6, 3] = -0.16
M[13, 0, 4:6, 4] = -0.1
M[13, 0, 3, 3:5] = 0.08
M[13, 0, 6, 3:5] = 0.08
M[13, 0, 4:6, 2] = 0.05
M[13, 0, 4:6, 5] = 0.05
M[13, 3:6, 4:6, 3:5] = -0.075
M[13, 3, 4:6, 3:5] = 0.2
M[13, 1, 3, 3:5] = 0.06
M[13, 1, 6, 3:5] = 0.06
M[13, 9, 5, 3:5] = 0.08

# Preserve rankings while retaining negative threshold decisions
M[:] *= 0.1
B[:] = [-2.16, -3.67, -2.0, -1.53, -2.91, -2.81, -4.35, -3.0, -3.14, -3.87, -3.77, -4.18, -3.47, -6.2]
```