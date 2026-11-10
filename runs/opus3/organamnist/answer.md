# Hand-set CNN for OrganAMNIST

## Design

**Assumptions about the images.** Each image is a crop centred on the organ, taken from its axial bounding box. It is shown in an abdominal window, which maps CT density to grey level as follows:

| Tissue | Approx. x |
|---|---|
| Air / lung | −1 |
| Fat | about −0.75 |
| Water / urine | about −0.2 |
| Liver, spleen, muscle | 0 to 0.4 |
| Contrast-enhanced kidney cortex, heart blood | 0.45 to 0.85 |
| Bone | > 0.85 |

For the left/right pairs I assume radiological orientation: the patient's right appears on the image left (low columns). This is a guess. If the arrays are flipped, the within-pair decisions reverse; if they are transposed, those decisions become coin flips.

**Filters.** Filters 0–5 use identity kernels, so each pixel gets a piecewise-linear function of its own intensity. The readout combines them into six soft intensity bins, written below as linear combinations of the filter outputs (F0 to F5):

| Filter | Formula | Threshold |
|---|---|---|
| F0 | ReLU(−5x − 4.25) | x < −0.85 |
| F1 | ReLU(−2.5x − 1) | x < −0.4 |
| F2 | ReLU(2.5x + 0.25) | x > −0.1 |
| F3 | ReLU(4x − 0.6) | x > 0.15 |
| F4 | ReLU(2.5x − 1.125) | x > 0.45 |
| F5 | ReLU(6.67x − 5.67) | x > 0.85 |

| Bin | Readout combination |
|---|---|
| air | 1.33·F0 |
| fat | 0.89·F1 − 1.78·F0 |
| water | 0.44·F0 − 0.89·F1 − 1.6·F2 + F3, plus a constant absorbed in the biases |
| soft tissue | 1.6·F2 − F3 − F4 + 0.375·F5 |
| enhanced | 0.83·F3 − 1.33·F4 − F5 |
| bone | F5 |

Filters 7 and 8 are positive and negative Laplacians with a small threshold; their sum measures local texture. Texture is read only from the interior 5×5 cells, which keeps out padding artifacts. Filters 6 and 9 are unused.

**Readout regions.** The outputs read these bins over the whole image, the centre (3×3 cells), the periphery, and the left or right three columns:

| Class | Evidence for | Evidence against |
|---|---|---|
| Lungs | air everywhere, especially the centre | — |
| Lung-right vs lung-left | right: air in left columns, mediastinum on the right; left: the mirror | — |
| Heart | enhanced or soft tissue in the centre; air (lung) in the periphery | central air; peripheral fat |
| Kidneys | enhanced centre; fat periphery; texture | air |
| Kidney-right vs kidney-left | right: cortex in the left half, spine in the right half; left: the mirror | — |
| Liver | homogeneous soft tissue, centre and whole image; soft tissue in the left half | fat, air, peripheral bone, texture |
| Spleen | soft tissue; fat, air and ribs in the periphery; soft tissue in the right half | texture |
| Bladder | water in the centre and overall; fat rim | texture, air |
| Femurs | bone everywhere, especially the centre | — |
| Femur-right vs femur-left | right: bone in the left half (lateral shaft); left: the mirror | — |
| Pancreas | texture, fat in the centre and overall | water, enhanced centre, bone |

The biases were balanced against my estimated typical feature profiles for each class.

```edits
CW[0, 0] = [[0, 0, 0], [0, -5, 0], [0, 0, 0]]
CB[0] = -4.25
CW[1, 0] = [[0, 0, 0], [0, -2.5, 0], [0, 0, 0]]
CB[1] = -1
CW[2, 0] = [[0, 0, 0], [0, 2.5, 0], [0, 0, 0]]
CB[2] = 0.25
CW[3, 0] = [[0, 0, 0], [0, 4, 0], [0, 0, 0]]
CB[3] = -0.6
CW[4, 0] = [[0, 0, 0], [0, 2.5, 0], [0, 0, 0]]
CB[4] = -1.125
CW[5, 0] = [[0, 0, 0], [0, 6.67, 0], [0, 0, 0]]
CB[5] = -5.67
CW[7, 0] = [[-0.25, -0.25, -0.25], [-0.25, 2, -0.25], [-0.25, -0.25, -0.25]]
CB[7] = -0.3
CW[8, 0] = [[0.25, 0.25, 0.25], [0.25, -2, 0.25], [0.25, 0.25, 0.25]]
CB[8] = -0.3
# bladder
M[0, 0] = -0.1525
M[0, 0, 2:5, 2:5] += 0.3357
M[0, 1] = 0.0082
M[0, 1, 2:5, 2:5] += -0.5383
M[0, 2] = -0.0653
M[0, 2, 2:5, 2:5] += -1.0667
M[0, 3] = 0.0408
M[0, 3, 2:5, 2:5] += 0.4815
M[0, 4, 2:5, 2:5] = 0.4074
M[0, 5, 2:5, 2:5] = 0.1806
M[0, 7, 1:6, 1:6] = -0.12
M[0, 8, 1:6, 1:6] = -0.12
# femurs (shared)
M[1:3, 0] = -0.0544
M[1:3, 0, 2:5, 2:5] += -0.0494
M[1:3, 1, 2:5, 2:5] = 0.0988
M[1:3, 2] = 0.0327
M[1:3, 2, 2:5, 2:5] += 0.1778
M[1:3, 3] = -0.0204
M[1:3, 3, 2:5, 2:5] += -0.1111
M[1:3, 4] = -0.0204
M[1:3, 5] = 0.2117
M[1:3, 5, 2:5, 2:5] += 0.4444
M[2, 5, :, 0:3] += 0.1429
M[2, 5, :, 4:7] -= 0.1429
M[1, 5, :, 0:3] -= 0.1429
M[1, 5, :, 4:7] += 0.1429
# heart
M[3, 0] = 0.4
M[3, 0, 2:5, 2:5] += -1.98
M[3, 1] = -0.0667
M[3, 1, 2:5, 2:5] += 0.2642
M[3, 2, 2:5, 2:5] = 0.7111
M[3, 3] = 0.034
M[3, 3, 2:5, 2:5] += -0.1667
M[3, 4] = -0.0544
M[3, 4, 2:5, 2:5] += -0.6667
M[3, 5] = -0.102
M[3, 5, 2:5, 2:5] += -0.25
# kidneys (shared)
M[4:6, 0] = -0.2151
M[4:6, 0, 2:5, 2:5] += 0.1335
M[4:6, 1] = 0.0667
M[4:6, 1, 2:5, 2:5] += -0.0667
M[4:6, 2, 2:5, 2:5] = -0.1778
M[4:6, 3] = 0.034
M[4:6, 3, 2:5, 2:5] += 0.4815
M[4:6, 4] = -0.0544
M[4:6, 4, 2:5, 2:5] += -0.4815
M[4:6, 5] = -0.0816
M[4:6, 5, 2:5, 2:5] += -0.4861
M[4:6, 7, 1:6, 1:6] = 0.08
M[4:6, 8, 1:6, 1:6] = 0.08
M[5, 3, :, 0:3] += 0.119
M[5, 4, :, 0:3] -= 0.1905
M[5, 5, :, 0:3] -= 0.2381
M[5, 3, :, 4:7] -= 0.119
M[5, 4, :, 4:7] += 0.1905
M[5, 5, :, 4:7] += 0.2381
M[4, 3, :, 0:3] -= 0.119
M[4, 4, :, 0:3] += 0.1905
M[4, 5, :, 0:3] += 0.2381
M[4, 3, :, 4:7] += 0.119
M[4, 4, :, 4:7] -= 0.1905
M[4, 5, :, 4:7] -= 0.2381
# liver
M[6, 0] = -0.0027
M[6, 0, 2:5, 2:5] += -0.0335
M[6, 1] = -0.103
M[6, 1, 2:5, 2:5] += 0.0667
M[6, 2] = 0.098
M[6, 2, 2:5, 2:5] += 0.7111
M[6, 3] = -0.0612
M[6, 3, 2:5, 2:5] += -0.6296
M[6, 4] = -0.0612
M[6, 4, 2:5, 2:5] += -0.1481
M[6, 5] = -0.077
M[6, 5, 2:5, 2:5] += 0.4889
M[6, 7, 1:6, 1:6] = -0.12
M[6, 8, 1:6, 1:6] = -0.12
M[6, 2, :, 0:3] += 0.1143
M[6, 3, :, 0:3] -= 0.0714
M[6, 4, :, 0:3] -= 0.0714
M[6, 5, :, 0:3] += 0.0268
M[6, 2, :, 4:7] -= 0.1143
M[6, 3, :, 4:7] += 0.0714
M[6, 4, :, 4:7] += 0.0714
M[6, 5, :, 4:7] -= 0.0268
# lungs (shared)
M[7:9, 0] = 0.1361
M[7:9, 0, 2:5, 2:5] += 0.4444
M[7:9, 3, 2:5, 2:5] = -0.1852
M[7:9, 4, 2:5, 2:5] = 0.2963
M[7:9, 5] = -0.0408
M[7:9, 5, 2:5, 2:5] += 0.2222
M[8, 0, :, 0:3] += 0.254
M[8, 0, :, 4:7] -= 0.254
M[7, 0, :, 0:3] -= 0.254
M[7, 0, :, 4:7] += 0.254
# pancreas
M[9, 0] = -0.0999
M[9, 0, 2:5, 2:5] += -0.7414
M[9, 1] = 0.0363
M[9, 1, 2:5, 2:5] += 0.5926
M[9, 2] = 0.0327
M[9, 2, 2:5, 2:5] += 0.3556
M[9, 3] = -0.0034
M[9, 3, 2:5, 2:5] += -0.4074
M[9, 4] = -0.0476
M[9, 4, 2:5, 2:5] += 0.4074
M[9, 5] = -0.074
M[9, 5, 2:5, 2:5] += 0.1806
M[9, 7, 1:6, 1:6] = 0.12
M[9, 8, 1:6, 1:6] = 0.12
# spleen
M[10, 0] = -0.0447
M[10, 0, 2:5, 2:5] += -0.4491
M[10, 1] = 0.0889
M[10, 1, 2:5, 2:5] += 0.0099
M[10, 2] = 0.0816
M[10, 2, 2:5, 2:5] += 0.7111
M[10, 3] = -0.051
M[10, 3, 2:5, 2:5] += -0.6296
M[10, 4] = -0.051
M[10, 4, 2:5, 2:5] += -0.037
M[10, 5] = 0.1691
M[10, 5, 2:5, 2:5] += 0.1972
M[10, 7, 1:6, 1:6] = -0.08
M[10, 8, 1:6, 1:6] = -0.08
M[10, 2, :, 0:3] -= 0.1143
M[10, 3, :, 0:3] += 0.0714
M[10, 4, :, 0:3] += 0.0714
M[10, 5, :, 0:3] -= 0.0268
M[10, 2, :, 4:7] += 0.1143
M[10, 3, :, 4:7] -= 0.0714
M[10, 4, :, 4:7] -= 0.0714
M[10, 5, :, 4:7] += 0.0268
# biases
B[0] = 4.5
B[1] = -1.5
B[2] = -1.5
B[3] = -3.3
B[4] = -1.0
B[5] = -1.0
B[6] = -3.5
B[7] = -2.0
B[8] = -2.0
B[9] = -3.0
B[10] = -4.2
```