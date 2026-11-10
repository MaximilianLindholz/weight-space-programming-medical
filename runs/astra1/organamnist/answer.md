This is an **unvalidated anatomical-prior design**; I cannot establish its accuracy without images or evaluation.

Filters 0–4 measure soft-tissue occupancy, brighter tissue, near-white density, near-black air, and dark fat/fluid. The difference between filters 0 and 1 gives a capped tissue-occupancy signal. Filter 5 detects bright local detail; filters 6–9 detect the two horizontal and two vertical edge directions.

The readouts favor:
- **Bladder:** a relatively uniform, moderately dark center with a brighter surrounding wall.
- **Femurs:** central dense bone, cortical detail, and potentially darker marrow.
- **Heart:** a broad tissue-filled center with air near the crop perimeter.
- **Kidneys:** an enhancing central body, surrounding fat, and a medial hilar indentation.
- **Liver:** extensive, relatively smooth tissue, with greater support toward the image’s left.
- **Lungs:** extensive near-black regions, especially centrally.
- **Pancreas:** a textured transverse tissue band.
- **Spleen:** a smooth, enhancing oblique body without a central dark hilum.

Weak opposing medial/lateral terms distinguish paired organs. These assume conventional radiological axial orientation, which I cannot verify for the stored arrays.

```edits
# Intensity and local-detail filters
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[2, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[3, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CW[4, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CW[5, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]

# Positive-right, positive-left, positive-down, positive-up edges
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[:] = [0.45, -0.15, -0.75, -0.80, -0.20, -0.06, -0.04, -0.04, -0.04, -0.04]

B[:] = [1.65, -0.55, -0.55, -1.15, -1.10, -1.10, -1.65, -0.45, -0.45, -0.65, -0.85]

# 0: Bladder -- moderate-density center, wall, little air or bone
M[0, 0] = 0.03
M[0, 1] = -0.03
M[0, 0, 2:5, 2:5] -= 0.43
M[0, 1, 2:5, 2:5] += 0.13
M[0, 4, 2:5, 2:5] = -0.60
M[0, 2] = -0.20
M[0, 3] = -0.08
M[0, 5, 1:6, 1:6] = -0.02
M[0, 6, 2:5, 4:6] = 0.07
M[0, 7, 2:5, 1:3] = 0.07
M[0, 8, 4:6, 2:5] = 0.07
M[0, 9, 1:3, 2:5] = 0.07

# 1, 2: Femurs -- concentrated dense bone and cortical detail
M[1:3, 2] = 0.28
M[1:3, 2, 1:6, 1:6] += 0.64
M[1:3, 1, 1:6, 1:6] = 0.12
M[1:3, 5, 1:6, 1:6] = 0.12
M[1:3, 4] = -0.04
M[1:3, 4, 1:6, 1:6] = 0
M[1:3, 4, 2:5, 2:5] = 0.20
M[1:3, 3] = -0.08
M[1:3, 6:10, 1:6, 1:6] = 0.04

# Femur-left: medial soft tissue and weak proximal-bone orientation
M[1, 0, 1:6, 0:2] = 0.05
M[1, 1, 1:6, 0:2] -= 0.05
M[1, 0, 1:6, 5:7] = -0.05
M[1, 1, 1:6, 5:7] += 0.05
M[1, 4, 1:6, 0:2] -= 0.03
M[1, 4, 1:6, 5:7] += 0.03
M[1, 2, 0:3, 1:3] += 0.05
M[1, 2, 0:3, 4:6] -= 0.05
M[1, 2, 4:7, 1:3] -= 0.05
M[1, 2, 4:7, 4:6] += 0.05

# Femur-right: mirrored weak laterality terms
M[2, 0, 1:6, 0:2] = -0.05
M[2, 1, 1:6, 0:2] += 0.05
M[2, 0, 1:6, 5:7] = 0.05
M[2, 1, 1:6, 5:7] -= 0.05
M[2, 4, 1:6, 0:2] += 0.03
M[2, 4, 1:6, 5:7] -= 0.03
M[2, 2, 0:3, 1:3] -= 0.05
M[2, 2, 0:3, 4:6] += 0.05
M[2, 2, 4:7, 1:3] += 0.05
M[2, 2, 4:7, 4:6] -= 0.05

# 3: Heart -- broad filled center, peripheral air, convex boundaries
M[3, 0, 1:6, 1:6] = 0.12
M[3, 1, 1:6, 1:6] = -0.12
M[3, 0, 2:5, 2:5] += 0.11
M[3, 1, 2:5, 2:5] -= 0.11
M[3, 1, 1:6, 1:6] += 0.032
M[3, 3] = 0.25
M[3, 3, 1:6, 1:6] = 0
M[3, 3, 2:5, 2:5] = -0.67
M[3, 2] = -0.08
M[3, 4, 2:5, 2:5] = -0.11
M[3, 5, 1:6, 1:6] = 0.02
M[3, 6, 1:6, 0:2] = 0.06
M[3, 7, 1:6, 5:7] = 0.06
M[3, 8, 0:2, 1:6] = 0.06
M[3, 9, 5:7, 1:6] = 0.06

# 4, 5: Kidneys -- central enhancement, fatty surroundings, limited air
M[4:6, 0] = -0.04
M[4:6, 1] = 0.04
M[4:6, 0, 1:6, 1:6] += 0.20
M[4:6, 1, 1:6, 1:6] -= 0.20
M[4:6, 0, 2:5, 2:5] += 0.11
M[4:6, 1, 2:5, 2:5] -= 0.11
M[4:6, 1, 1:6, 1:6] += 0.06
M[4:6, 4] = 0.08
M[4:6, 4, 1:6, 1:6] = 0
M[4:6, 4, 2:5, 2:5] = -0.33
M[4:6, 3] = -0.10
M[4:6, 2] = -0.14
M[4:6, 5, 1:6, 1:6] = 0.12
M[4:6, 6, 1:6, 0:2] = 0.06
M[4:6, 7, 1:6, 5:7] = 0.06
M[4:6, 8, 0:2, 1:6] = 0.06
M[4:6, 9, 5:7, 1:6] = 0.06

# Kidney-left: medial indentation on image left
M[4, 0, 2:5, 1:3] -= 0.10
M[4, 1, 2:5, 1:3] += 0.10
M[4, 0, 2:5, 4:6] += 0.10
M[4, 1, 2:5, 4:6] -= 0.10
M[4, 4, 2:5, 1:3] += 0.10
M[4, 4, 2:5, 4:6] -= 0.10
M[4, 6, 2:5, 2:4] += 0.08

# Kidney-right: mirrored indentation
M[5, 0, 2:5, 1:3] += 0.10
M[5, 1, 2:5, 1:3] -= 0.10
M[5, 0, 2:5, 4:6] -= 0.10
M[5, 1, 2:5, 4:6] += 0.10
M[5, 4, 2:5, 1:3] -= 0.10
M[5, 4, 2:5, 4:6] += 0.10
M[5, 7, 2:5, 3:5] += 0.08

# 6: Liver -- extensive smooth tissue, modest asymmetric shape prior
M[6, 0] = 0.14
M[6, 1] = -0.16
M[6, 0, 2:5, 2:5] += 0.11
M[6, 1, 2:5, 2:5] -= 0.11
M[6, 0, 1:5, 0:3] += 0.06
M[6, 1, 1:5, 0:3] -= 0.06
M[6, 0, 4:7, 4:7] -= 0.04
M[6, 1, 4:7, 4:7] += 0.04
M[6, 3] = -0.06
M[6, 2] = -0.08
M[6, 4, 2:5, 2:5] = -0.055
M[6, 5, 1:6, 1:6] = -0.08

# 7, 8: Lungs -- extensive air, particularly in the center
M[7:9, 3] = 0.20
M[7:9, 3, 2:5, 2:5] += 0.44
M[7:9, 0, 2:5, 2:5] = -0.22
M[7:9, 1, 2:5, 2:5] = 0.22
M[7:9, 1] -= 0.02
M[7:9, 2] = -0.10

# Lung-left: medial tissue on image left, lateral air on image right
M[7, 0, 2:6, 0:3] += 0.045
M[7, 1, 2:6, 0:3] -= 0.045
M[7, 0, 2:6, 4:7] -= 0.045
M[7, 1, 2:6, 4:7] += 0.045
M[7, 3, 2:6, 0:3] -= 0.06
M[7, 3, 2:6, 4:7] += 0.06
M[7, 7, 2:6, 1:3] = 0.06

# Lung-right: mirrored medial and lateral evidence
M[8, 0, 2:6, 0:3] -= 0.045
M[8, 1, 2:6, 0:3] += 0.045
M[8, 0, 2:6, 4:7] += 0.045
M[8, 1, 2:6, 4:7] -= 0.045
M[8, 3, 2:6, 0:3] += 0.06
M[8, 3, 2:6, 4:7] -= 0.06
M[8, 6, 2:6, 4:6] = 0.06

# 9: Pancreas -- transverse tissue band and local detail
M[9, 0, 2:5, :] = 0.24
M[9, 1, 2:5, :] = -0.19
M[9, 0, 0:2, :] = -0.07
M[9, 1, 0:2, :] = 0.07
M[9, 0, 5:7, :] = -0.07
M[9, 1, 5:7, :] = 0.07
M[9, 0, 2:5, 0:2] += 0.07
M[9, 1, 2:5, 0:2] -= 0.07
M[9, 0, 2:5, 5:7] += 0.07
M[9, 1, 2:5, 5:7] -= 0.07
M[9, 4] = 0.06
M[9, 4, 1:6, 1:6] = 0
M[9, 4, 2:5, 2:5] = -0.11
M[9, 3] = -0.08
M[9, 2] = -0.12
M[9, 5, 2:5, :] = 0.19
M[9, 8, 1:3, 1:6] = 0.10
M[9, 9, 4:6, 1:6] = 0.10

# 10: Spleen -- smooth oblique enhancing body
M[10, 0] = -0.02
M[10, 1] = 0.02
M[10, 0, 1, 3:6] += 0.24
M[10, 1, 1, 3:6] -= 0.24
M[10, 0, 2, 2:6] += 0.24
M[10, 1, 2, 2:6] -= 0.24
M[10, 0, 3, 1:6] += 0.24
M[10, 1, 3, 1:6] -= 0.24
M[10, 0, 4, 1:5] += 0.24
M[10, 1, 4, 1:5] -= 0.24
M[10, 0, 5, 1:4] += 0.24
M[10, 1, 5, 1:4] -= 0.24
M[10, 0, 2:5, 2:5] += 0.055
M[10, 1, 2:5, 2:5] -= 0.055
M[10, 1, 1:6, 1:6] += 0.08

# Weak oblique-shape contrast
M[10, 0, 1:3, 1:3] -= 0.10
M[10, 1, 1:3, 1:3] += 0.10
M[10, 0, 4:6, 4:6] -= 0.10
M[10, 1, 4:6, 4:6] += 0.10
M[10, 0, 1:3, 4:6] += 0.05
M[10, 1, 1:3, 4:6] -= 0.05
M[10, 0, 4:6, 1:3] += 0.05
M[10, 1, 4:6, 1:3] -= 0.05

M[10, 4] = 0.06
M[10, 4, 1:6, 1:6] = 0
M[10, 4, 2:5, 2:5] = -0.44
M[10, 3] = -0.10
M[10, 2] = -0.16
M[10, 5, 1:6, 1:6] = -0.12
M[10, 6, 3:6, 1:3] = 0.07
M[10, 7, 1:4, 4:6] = 0.07
M[10, 8, 1:3, 3:6] = 0.07
M[10, 9, 4:6, 1:4] = 0.07

# Restore useful amplitude for the narrow bone and air thresholds
M[:, 2] *= 1.6
M[:, 3] *= 2
```