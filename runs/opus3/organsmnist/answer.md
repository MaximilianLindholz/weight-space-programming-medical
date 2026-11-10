## Design

**Assumption.** Each image is a sagittal crop of the bounding box around one organ. The organ fills the middle of the crop, and its surroundings (air, fat, bone) fill the border. I don't trust the image orientation, so the classifier uses only **center vs. periphery** statistics and does not rely on top/bottom or anterior/posterior. Under the abdominal window, x ≈ (HU − 40)/200. That puts air at −1, fat at about −0.7, fluid at about −0.1, liver/spleen at about +0.35, kidney cortex and contrast blood at about +0.7, and bone near +1.

**Filters.** Filters 0–5 are 1×1 "intensity ramps", so the readout can build piecewise-linear intensity bands. Filters 6–9 detect edges.

| k | response | detects |
|---|---|---|
| 0 | ReLU(−x−0.5) | dark: fat and air |
| 1 | ReLU(−4x−3.4) | air only (lung, gas) |
| 2 | ReLU(x+0.4) | soft tissue or fluid and brighter |
| 3 | ReLU(x) | organ-level brightness |
| 4 | ReLU(x−0.45) | bright: enhancing cortex, blood, bone |
| 5 | ReLU(3x−2.4) | bone |
| 6–9 | ReLU(±Sobel x/y − 0.05) | edge and texture density |

**Derived features.** The readout combines the filters into these features:
- air fraction in the center (C = grid 2..4 × 2..4) and in the periphery (P);
- fat (k0 − 0.83·k1) in C and in P;
- fluid band (k2 − 2k3 + k4) in C;
- organ band (k3 − 2k4) in C and in P;
- bright tissue (k4) in C;
- global bone (k5);
- edge density in the inner 5×5 cells, which avoids the zero-padding border artifacts.

**Outputs.** Each output is a nearest-centroid linear score, T·(μ·z − |μ|²/2), plus a small class-frequency prior. The hand-estimated centroids μ are:
- **Lung:** air in C and P.
- **Heart:** organ/bright tissue in C, air in P.
- **Bladder:** fluid band in C, fat in P.
- **Femur:** bone and bright in C, many edges.
- **Kidney:** bright cortex in C, fat around it.
- **Liver:** organ band everywhere, few edges.
- **Spleen:** organ band in C, more fat and air in P.
- **Pancreas:** fat and fluid mixed in C, many edges.

**Left/right pairs.** The two sides of each pair share weights, so they are mostly indistinguishable. There is one small cue: right kidney gets extra credit for liver-like tissue in the periphery, and left kidney for gas in the periphery.

```edits
CW[0, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[0] = -0.5
CW[1, 0] = [[0, 0, 0], [0, -4, 0], [0, 0, 0]]
CB[1] = -3.4
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[2] = 0.4
CW[3, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[3] = 0
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[4] = -0.45
CW[5, 0] = [[0, 0, 0], [0, 3, 0], [0, 0, 0]]
CB[5] = -2.4
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CB[6] = -0.05
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CB[7] = -0.05
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CB[8] = -0.05
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[9] = -0.05
# bladder
M[0, 0, :, :] = 1.2
M[0, 0, 2:5, 2:5] = 1.333
M[0, 1, :, :] = -0.996
M[0, 1, 2:5, 2:5] = -1.107
M[0, 2, 2:5, 2:5] = 1.433
M[0, 3, :, :] = 0.0213
M[0, 3, 2:5, 2:5] = -2.85
M[0, 4, :, :] = -0.0425
M[0, 4, 2:5, 2:5] = 1.4
M[0, 5, :, :] = 0.122
M[0, 6:10, 1:6, 1:6] = 0.094
# femurs
M[1:3, 0, :, :] = 0.9
M[1:3, 0, 2:5, 2:5] = 2.667
M[1:3, 1, :, :] = -0.747
M[1:3, 1, 2:5, 2:5] = -2.214
M[1:3, 2, 2:5, 2:5] = 0.521
M[1:3, 3, 2:5, 2:5] = -1.142
M[1:3, 4, 2:5, 2:5] = 2.128
M[1:3, 5, :, :] = 0.392
M[1:3, 6:10, 1:6, 1:6] = 0.375
# heart
M[3, 0, :, :] = 0.6
M[3, 0, 2:5, 2:5] = 1.333
M[3, 1, :, :] = -0.276
M[3, 1, 2:5, 2:5] = -1.076
M[3, 2, 2:5, 2:5] = 0.26
M[3, 3, :, :] = 0.25
M[3, 3, 2:5, 2:5] = 0.313
M[3, 4, :, :] = -0.5
M[3, 4, 2:5, 2:5] = -0.938
M[3, 6:10, 1:6, 1:6] = 0.188
# kidneys
M[4:6, 0, :, :] = 1.2
M[4:6, 0, 2:5, 2:5] = 2.667
M[4:6, 1, :, :] = -0.969
M[4:6, 1, 2:5, 2:5] = -2.214
M[4:6, 2, 2:5, 2:5] = 0.157
M[4:6, 3, :, :] = 0.209
M[4:6, 3, 2:5, 2:5] = 0.353
M[4:6, 4, :, :] = -0.4175
M[4:6, 4, 2:5, 2:5] = -0.527
M[4:6, 5, :, :] = 0.0245
M[4:6, 6:10, 1:6, 1:6] = 0.188
M[4, 1, :, :] += 0.042
M[4, 1, 2:5, 2:5] -= 0.042
M[5, 3, :, :] += 0.05
M[5, 3, 2:5, 2:5] -= 0.05
M[5, 4, :, :] -= 0.1
M[5, 4, 2:5, 2:5] += 0.1
# liver
M[6, 0, :, :] = 0.3
M[6, 0, 2:5, 2:5] = 0
M[6, 1, :, :] = -0.193
M[6, 1, 2:5, 2:5] = 0
M[6, 2, 2:5, 2:5] = 0.364
M[6, 3, :, :] = 0.479
M[6, 3, 2:5, 2:5] = 0.304
M[6, 4, :, :] = -0.9575
M[6, 4, 2:5, 2:5] = -1.598
M[6, 5, :, :] = 0.0245
M[6, 6:10, 1:6, 1:6] = 0.0564
# lungs
M[7:9, 0, :, :] = 0.3
M[7:9, 0, 2:5, 2:5] = 0
M[7:9, 1, :, :] = 0.0285
M[7:9, 1, 2:5, 2:5] = 0.524
M[7:9, 2, 2:5, 2:5] = 0.104
M[7:9, 3, :, :] = 0.209
M[7:9, 3, 2:5, 2:5] = -0.042
M[7:9, 4, :, :] = -0.4175
M[7:9, 4, 2:5, 2:5] = -0.124
M[7:9, 5, :, :] = 0.049
M[7:9, 6:10, 1:6, 1:6] = 0.225
# pancreas
M[9, 0, :, :] = 0.9
M[9, 0, 2:5, 2:5] = 4.0
M[9, 1, :, :] = -0.691
M[9, 1, 2:5, 2:5] = -3.29
M[9, 2, 2:5, 2:5] = 0.626
M[9, 3, :, :] = 0.271
M[9, 3, 2:5, 2:5] = -0.784
M[9, 4, :, :] = -0.5425
M[9, 4, 2:5, 2:5] = -0.151
M[9, 6:10, 1:6, 1:6] = 0.281
# spleen
M[10, 0, :, :] = 0.6
M[10, 0, 2:5, 2:5] = 0.667
M[10, 1, :, :] = -0.415
M[10, 1, 2:5, 2:5] = -0.554
M[10, 3, :, :] = 0.334
M[10, 3, 2:5, 2:5] = 1.2
M[10, 4, :, :] = -0.6675
M[10, 4, 2:5, 2:5] = -2.296
M[10, 5, :, :] = 0.049
M[10, 6:10, 1:6, 1:6] = 0.094
# biases
B[:] = [-4.54, -6.58, -6.58, -4.05, -4.61, -4.76, -3.71, -3.75, -3.75, -4.66, -3.89]
```