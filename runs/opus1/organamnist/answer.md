# Hand-set weights for OrganAMNIST: intensity bands, coarse layout and diagonal left/right cues

## Assumptions

- **Input crops.** Each image is a crop of the organ's bounding box from an axial slice, not the whole body section. Under an abdominal window, the approximate grey values are:

  | Tissue | Approx. x |
  |---|---|
  | Air (lung) | -1 |
  | Fat | -0.7 |
  | Fluid (urine) | -0.15 |
  | Muscle | 0.1 |
  | Liver | 0.33 |
  | Spleen | 0.4 |
  | Enhanced blood | 0.55 |
  | Kidney cortex | 0.6 |
  | Bone | 1 |

- **Left/right is the riskiest guess.** I don't know whether the arrays are transposed or rotated. The left/right cues are therefore built only from diagonal corner contrasts. Main diagonal = top-left and bottom-right corners; anti-diagonal = the other two. These contrasts give the same answer whether the image is transposed or rotated 180°. They assume voxel order follows DICOM: x towards patient-left, y towards posterior.
  - Right organs then have their anterolateral and posteromedial corners on the main diagonal.
  - Left organs have them on the anti-diagonal.
  - If the arrays are mirrored along a single axis, these cues point the wrong way.

## Filters

Filters 0–5 read only the centre pixel. They are intensity ramps, so the linear readout can combine them into intensity bands.

| Filter | Formula | Fires on |
|---|---|---|
| 0 AIR | ReLU(-5x-4) | lung or air (1) |
| 1 DARK | ReLU(-2x-0.8) | fat (0.6), air (1.2); fat-only band = F1 - 1.2·F0 |
| 2 T0 | ReLU(x+0.45) | anything brighter than fat |
| 3 T1 | 2·ReLU(x-0.1) | parenchyma (liver, spleen) and brighter |
| 4 T2 | 3·ReLU(x-0.45) | enhanced kidney or blood |
| 5 BONE | 5·ReLU(x-0.85) | bone |
| 6, 7 | ± Laplacian, minus a 0.1 threshold | bright spots and dark spots (vessels, edges) |
| 8, 9 | ± horizontal Sobel gradient, minus a 0.1 threshold | edge density |

Filters 6–9 are read only in the inner 5×5 cells, which avoids artefacts from the zero padding.

## Readout

The readout is a hand-built linear discriminant. Its features are region means over parts of the 7×7 grid:

- air in the centre and air in the outer ring
- fat in the ring
- in the centre: a low-tissue band (fluid or muscle), an organ band (liver or spleen grey) and a bright band (kidney or blood)
- bone over the whole image
- texture over the inner cells
- organ-band tissue in the main-diagonal corners

Weights are each class's guessed feature mean divided by an assumed variance. Each bias combines the usual discriminant term with the log class prior.

What each class mainly reads:

- **Lung:** air everywhere.
- **Heart:** air in the ring, with organ-grey and bright tissue in the centre.
- **Kidney:** a bright centre surrounded by a ring of fat.
- **Bladder:** a fluid-grey centre with a ring of fat.
- **Femur:** bone plus strong texture.
- **Pancreas:** a mix of fat, tissue and vessels, with high texture.
- **Liver vs spleen:** both have a grey centre. Liver also has tissue in the main-diagonal corners. Spleen has its curved shape and more fat.

Left/right pairs share the same base logit, then get opposite-signed corner cues:

- **Kidney:** the bean's long axis runs anterolateral to posteromedial. So bright tissue on the main diagonal and fat (hilum) on the anti-diagonal means right.
- **Femur:** the head sits anteromedial and the trochanter posterolateral. So bone on the main diagonal means left.
- **Lung:** the spine sits in the posteromedial corner. So bone on the main diagonal means right.

```edits
CW[0, 0] = [[0, 0, 0], [0, -5, 0], [0, 0, 0]]
CB[0] = -4
CW[1, 0] = [[0, 0, 0], [0, -2, 0], [0, 0, 0]]
CB[1] = -0.8
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[2] = 0.45
CW[3, 0] = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
CB[3] = -0.2
CW[4, 0] = [[0, 0, 0], [0, 3, 0], [0, 0, 0]]
CB[4] = -1.35
CW[5, 0] = [[0, 0, 0], [0, 5, 0], [0, 0, 0]]
CB[5] = -4.25
CW[6, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[6] = -0.1
CW[7, 0] = [[0.125, 0.125, 0.125], [0.125, -1, 0.125], [0.125, 0.125, 0.125]]
CB[7] = -0.1
CW[8, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CB[8] = -0.1
CW[9, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[9] = -0.1
# ---- bladder (0)
M[0, 0, :, :] = -0.295
M[0, 0, 1:6, 1:6] = 0
M[0, 1, :, :] = 0.254
M[0, 1, 1:6, 1:6] = 0
M[0, 2, 2:5, 2:5] = 0.173
M[0, 3, 2:5, 2:5] = -0.409
M[0, 4, 2:5, 2:5] = 0.302
M[0, 5, :, :] = 0.04
M[0, 5, 2:5, 2:5] -= 0.249
M[0, 6:10, 1:6, 1:6] = 0.044
B[0] = -4.23
# ---- femur (1 left, 2 right)
M[1:3, 0, :, :] = -0.2175
M[1:3, 0, 1:6, 1:6] = 0
M[1:3, 1, :, :] = 0.181
M[1:3, 1, 1:6, 1:6] = 0
M[1:3, 2, 2:5, 2:5] = -0.139
M[1:3, 3, :, :] = -0.0071
M[1:3, 3, 2:5, 2:5] += 0.216
M[1:3, 4, :, :] = 0.0214
M[1:3, 4, 2:5, 2:5] += 0.287
M[1:3, 5, :, :] = 0.1465
M[1:3, 5, 2:5, 2:5] -= 0.674
M[1:3, 6:10, 1:6, 1:6] = 0.311
B[1:3] = -7.54
M[1, 5, 0:2, 0:2] += 0.625
M[1, 5, 5:7, 5:7] += 0.625
M[1, 5, 0:2, 5:7] -= 0.625
M[1, 5, 5:7, 0:2] -= 0.625
M[2, 5, 0:2, 0:2] -= 0.625
M[2, 5, 5:7, 5:7] -= 0.625
M[2, 5, 0:2, 5:7] += 0.625
M[2, 5, 5:7, 0:2] += 0.625
# ---- heart (3)
M[3, 0, :, :] = 0.14
M[3, 0, 1:6, 1:6] = 0
M[3, 0, 2:5, 2:5] = 0.037
M[3, 1, :, :] = 0.087
M[3, 1, 1:6, 1:6] = 0
M[3, 2, 2:5, 2:5] = -0.278
M[3, 3, :, :] = 0.0533
M[3, 3, 2:5, 2:5] += 0.802
M[3, 3, 0:2, 0:2] += 0.07
M[3, 3, 5:7, 5:7] += 0.07
M[3, 4, :, :] = -0.16
M[3, 4, 2:5, 2:5] -= 0.539
M[3, 4, 0:2, 0:2] -= 0.21
M[3, 4, 5:7, 5:7] -= 0.21
M[3, 5, :, :] = 0.229
M[3, 5, 2:5, 2:5] += 0.136
M[3, 5, 0:2, 0:2] += 0.28
M[3, 5, 5:7, 5:7] += 0.28
M[3, 6:10, 1:6, 1:6] = 0.133
B[3] = -5.5
# ---- kidney (4 left, 5 right)
M[4:6, 0, :, :] = -0.295
M[4:6, 0, 1:6, 1:6] = 0
M[4:6, 1, :, :] = 0.254
M[4:6, 1, 1:6, 1:6] = 0
M[4:6, 2, 2:5, 2:5] = -0.382
M[4:6, 3, 2:5, 2:5] = 0.332
M[4:6, 3, 0:2, 0:2] -= 0.07
M[4:6, 3, 5:7, 5:7] -= 0.07
M[4:6, 4, 2:5, 2:5] = 1.815
M[4:6, 4, 0:2, 0:2] += 0.21
M[4:6, 4, 5:7, 5:7] += 0.21
M[4:6, 5, :, :] = 0.008
M[4:6, 5, 2:5, 2:5] -= 3.43
M[4:6, 5, 0:2, 0:2] -= 0.28
M[4:6, 5, 5:7, 5:7] -= 0.28
M[4:6, 6:10, 1:6, 1:6] = 0.156
B[4:6] = -6.98
M[5, 4, 0:2, 0:2] += 0.375
M[5, 4, 5:7, 5:7] += 0.375
M[5, 4, 0:2, 5:7] -= 0.375
M[5, 4, 5:7, 0:2] -= 0.375
M[5, 5, 0:2, 0:2] -= 0.825
M[5, 5, 5:7, 5:7] -= 0.825
M[5, 5, 0:2, 5:7] += 0.825
M[5, 5, 5:7, 0:2] += 0.825
M[5, 1, 0:2, 0:2] -= 0.375
M[5, 1, 5:7, 5:7] -= 0.375
M[5, 1, 0:2, 5:7] += 0.375
M[5, 1, 5:7, 0:2] += 0.375
M[4, 4, 0:2, 0:2] -= 0.375
M[4, 4, 5:7, 5:7] -= 0.375
M[4, 4, 0:2, 5:7] += 0.375
M[4, 4, 5:7, 0:2] += 0.375
M[4, 5, 0:2, 0:2] += 0.825
M[4, 5, 5:7, 5:7] += 0.825
M[4, 5, 0:2, 5:7] -= 0.825
M[4, 5, 5:7, 0:2] -= 0.825
M[4, 1, 0:2, 0:2] += 0.375
M[4, 1, 5:7, 5:7] += 0.375
M[4, 1, 0:2, 5:7] -= 0.375
M[4, 1, 5:7, 0:2] -= 0.375
# ---- liver (6)
M[6, 0, :, :] = -0.058
M[6, 0, 1:6, 1:6] = 0
M[6, 0, 2:5, 2:5] = 0.024
M[6, 1, :, :] = 0.087
M[6, 1, 1:6, 1:6] = 0
M[6, 2, 2:5, 2:5] = -0.104
M[6, 3, :, :] = 0.1065
M[6, 3, 2:5, 2:5] += 0.702
M[6, 3, 0:2, 0:2] += 0.3475
M[6, 3, 5:7, 5:7] += 0.3475
M[6, 4, :, :] = -0.32
M[6, 4, 2:5, 2:5] -= 1.492
M[6, 4, 0:2, 0:2] -= 1.0425
M[6, 4, 5:7, 5:7] -= 1.0425
M[6, 5, :, :] = 0.442
M[6, 5, 2:5, 2:5] += 1.847
M[6, 5, 0:2, 0:2] += 1.39
M[6, 5, 5:7, 5:7] += 1.39
M[6, 6:10, 1:6, 1:6] = 0.0756
B[6] = -4.15
# ---- lung (7 left, 8 right)
M[7:9, 0, :, :] = 0.2025
M[7:9, 0, 1:6, 1:6] = 0
M[7:9, 0, 2:5, 2:5] = 0.802
M[7:9, 1, :, :] = 0.043
M[7:9, 1, 1:6, 1:6] = 0
M[7:9, 3, :, :] = 0.0178
M[7:9, 3, 2:5, 2:5] += 0.037
M[7:9, 3, 0:2, 0:2] += 0.07
M[7:9, 3, 5:7, 5:7] += 0.07
M[7:9, 4, :, :] = -0.0533
M[7:9, 4, 2:5, 2:5] -= 0.071
M[7:9, 4, 0:2, 0:2] -= 0.21
M[7:9, 4, 5:7, 5:7] -= 0.21
M[7:9, 5, :, :] = 0.095
M[7:9, 5, 2:5, 2:5] += 0.061
M[7:9, 5, 0:2, 0:2] += 0.28
M[7:9, 5, 5:7, 5:7] += 0.28
M[7:9, 6:10, 1:6, 1:6] = 0.156
B[7:9] = -7.1
M[8, 5, 0:2, 0:2] += 1.0
M[8, 5, 5:7, 5:7] += 1.0
M[8, 5, 0:2, 5:7] -= 1.0
M[8, 5, 5:7, 0:2] -= 1.0
M[7, 5, 0:2, 0:2] -= 1.0
M[7, 5, 5:7, 5:7] -= 1.0
M[7, 5, 0:2, 5:7] += 1.0
M[7, 5, 5:7, 0:2] += 1.0
# ---- pancreas (9)
M[9, 0, :, :] = -0.2375
M[9, 0, 1:6, 1:6] = 0
M[9, 0, 2:5, 2:5] = 0.037
M[9, 1, :, :] = 0.2175
M[9, 1, 1:6, 1:6] = 0
M[9, 2, 2:5, 2:5] = -0.069
M[9, 3, :, :] = 0.0427
M[9, 3, 2:5, 2:5] += 0.324
M[9, 3, 0:2, 0:2] += 0.166
M[9, 3, 5:7, 5:7] += 0.166
M[9, 4, :, :] = -0.128
M[9, 4, 2:5, 2:5] -= 0.371
M[9, 4, 0:2, 0:2] -= 0.499
M[9, 4, 5:7, 5:7] -= 0.499
M[9, 5, :, :] = 0.1865
M[9, 5, 2:5, 2:5] += 0.231
M[9, 5, 0:2, 0:2] += 0.665
M[9, 5, 5:7, 5:7] += 0.665
M[9, 6:10, 1:6, 1:6] = 0.244
B[9] = -5.38
# ---- spleen (10)
M[10, 0, :, :] = -0.156
M[10, 0, 1:6, 1:6] = 0
M[10, 0, 2:5, 2:5] = 0.024
M[10, 1, :, :] = 0.145
M[10, 1, 1:6, 1:6] = 0
M[10, 2, 2:5, 2:5] = -0.173
M[10, 3, :, :] = 0.1065
M[10, 3, 2:5, 2:5] += 0.902
M[10, 3, 0:2, 0:2] += 0.111
M[10, 3, 5:7, 5:7] += 0.111
M[10, 4, :, :] = -0.32
M[10, 4, 2:5, 2:5] -= 1.686
M[10, 4, 0:2, 0:2] -= 0.334
M[10, 4, 5:7, 5:7] -= 0.334
M[10, 5, :, :] = 0.442
M[10, 5, 2:5, 2:5] += 2.01
M[10, 5, 0:2, 0:2] += 0.445
M[10, 5, 5:7, 5:7] += 0.445
M[10, 6:10, 1:6, 1:6] = 0.0576
B[10] = -4.88
```