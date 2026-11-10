This is an unvalidated, hand-built CT heuristic; its accuracy cannot be established without images.

Filters 0 and 4 jointly give a clipped soft-tissue occupancy signal. Filter 1 detects dark fat/fluid, 2 detects near-white bone, and 3 detects very dark air. Filter 5 detects bright local detail; filters 6–9 detect rightward, leftward, downward, and upward intensity increases.

The outputs combine density evidence with coarse spatial templates: smooth central fluid for bladder; bright cortex and a head-to-shaft offset for femurs; central tissue surrounded by air for heart; peripheral tissue and a medial dark hilum for kidneys; a broad asymmetric homogeneous region for liver; air-filled interiors with medial tissue for lungs; a textured diagonal band for pancreas; and a smooth, filled oval for spleen. Paired-organ templates assume radiological orientation—patient left on image right. That convention is an assumption, not verified from these arrays.

```edits
# Intensity features.
CW[0, 0] = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
CW[1, 0] = [[0, 0, 0], [0, -1.25, 0], [0, 0, 0]]
CW[2, 0] = [[0, 0, 0], [0, 2.5, 0], [0, 0, 0]]
CW[3, 0] = [[0, 0, 0], [0, -4, 0], [0, 0, 0]]
CW[4, 0] = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]

# Bright detail and signed, smoothed derivatives.
CW[5, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[:] = [1, -0.25, -1.5, -3, 0, -0.04, -0.025, -0.025, -0.025, -0.025]

# Global density and texture preferences.
B[:] = [1.10, -2.52, -2.52, -0.58, -0.23, -0.23, -1.12, -2.28, -2.28, 0.31, -0.59]

M[0, 0] = -0.008
M[0, 4] = 0.008
M[0, 1] = -0.014
M[0, 2] = -0.08
M[0, 3] = -0.01
M[0, 5] = -0.07

M[1:3, 0] = 0.028
M[1:3, 4] = -0.028
M[1:3, 1] = -0.014
M[1:3, 2] = 0.272
M[1:3, 3] = -0.01
M[1:3, 5] = 0.08

M[3, 0] = 0.028
M[3, 4] = -0.028
M[3, 1] = 0.002
M[3, 2] = -0.08
M[3, 3] = 0.038
M[3, 5] = -0.05

M[4:6, 0] = 0.016
M[4:6, 4] = -0.016
M[4:6, 1] = 0.002
M[4:6, 2] = -0.064
M[4:6, 3] = -0.0052
M[4:6, 5] = 0.03

M[6, 0] = 0.052
M[6, 4] = -0.052
M[6, 1] = -0.014
M[6, 2] = -0.08
M[6, 3] = -0.0004
M[6, 5] = -0.07

M[7:9, 0] = -0.0872
M[7:9, 4] = 0.0872
M[7:9, 1] = 0.074
M[7:9, 2] = -0.08
M[7:9, 3] = 0.23
M[7:9, 5] = -0.01

M[9, 0] = -0.008
M[9, 4] = 0.008
M[9, 1] = 0.01
M[9, 2] = -0.048
M[9, 3] = -0.0004
M[9, 5] = 0.06

M[10, 0] = 0.0352
M[10, 4] = -0.0352
M[10, 1] = -0.0076
M[10, 2] = -0.08
M[10, 3] = -0.0052
M[10, 5] = -0.05

# Bladder: non-bright, non-fatty, smooth interior; rounded boundary.
M[0, 4, 1:6, 1:6] -= 0.04
M[0, 1, 1:6, 1:6] -= 0.05
M[0, 5, 1:6, 1:6] -= 0.10
M[0, 6, 1:6, 0:2] += 0.06
M[0, 7, 1:6, 5:7] += 0.06
M[0, 8, 0:2, 1:6] += 0.04
M[0, 9, 5:7, 2:5] += 0.06

# Femurs: central bone rather than isolated bright peripheral structures.
M[1:3, 2, :, 2:5] += 0.035
M[1:3, 2, :, 0] -= 0.0525
M[1:3, 2, :, 6] -= 0.0525

# Left femur: proximal head toward image left, distal shaft toward right.
M[1, 2, 0:3, 0:3] += 0.10
M[1, 2, 0:3, 4:7] -= 0.10
M[1, 2, 3:7, 0:3] -= 0.08
M[1, 2, 3:7, 4:7] += 0.08
M[1, 6, 3:7, 2:4] += 0.045
M[1, 7, 3:7, 5:7] += 0.045

# Right femur: mirrored head and shaft.
M[2, 2, 0:3, 0:3] -= 0.10
M[2, 2, 0:3, 4:7] += 0.10
M[2, 2, 3:7, 0:3] += 0.08
M[2, 2, 3:7, 4:7] -= 0.08
M[2, 6, 3:7, 0:2] += 0.045
M[2, 7, 3:7, 3:5] += 0.045

# Heart: filled center, dark upper lateral surroundings.
M[3, 0] -= 0.03
M[3, 4] += 0.03
M[3, 0, 1:6, 1:6] += 0.06
M[3, 4, 1:6, 1:6] -= 0.06
M[3, 3, 0:3, 0:2] += 0.045
M[3, 3, 0:3, 5:7] += 0.045
M[3, 3, 2:5, 2:5] -= 0.06

# Cardiac apex toward the lower image-right portion.
M[3, 0, 4:6, 3:6] += 0.04
M[3, 4, 4:6, 3:6] -= 0.04
M[3, 0, 4:6, 0:3] -= 0.04
M[3, 4, 4:6, 0:3] += 0.04
M[3, 6, 1:5, 0:2] += 0.05
M[3, 7, 2:6, 5:7] += 0.05
M[3, 8, 0:2, 2:5] += 0.05
M[3, 9, 5:7, 2:6] += 0.05

# Kidneys: compact parenchyma, internal detail, rounded outer borders.
M[4:6, 0] -= 0.02
M[4:6, 4] += 0.02
M[4:6, 0, 1:6, 1:6] += 0.04
M[4:6, 4, 1:6, 1:6] -= 0.04
M[4:6, 5, 2:5, 2:5] += 0.10
M[4:6, 6, 1:6, 0:2] += 0.035
M[4:6, 7, 1:6, 5:7] += 0.035
M[4:6, 8, 0:2, 2:5] += 0.035
M[4:6, 9, 5:7, 2:5] += 0.035

# Left kidney: darker medial image-left notch.
M[4, 0, 2:5, 4:6] += 0.06
M[4, 4, 2:5, 4:6] -= 0.06
M[4, 0, 2:5, 1:3] -= 0.06
M[4, 4, 2:5, 1:3] += 0.06
M[4, 1, 2:5, 1:3] += 0.10
M[4, 1, 2:5, 4:6] -= 0.10
M[4, 6, 2:5, 2:4] += 0.07
M[4, 7, 2:5, 2:4] -= 0.025

# Right kidney: darker medial image-right notch.
M[5, 0, 2:5, 1:3] += 0.06
M[5, 4, 2:5, 1:3] -= 0.06
M[5, 0, 2:5, 4:6] -= 0.06
M[5, 4, 2:5, 4:6] += 0.06
M[5, 1, 2:5, 4:6] += 0.10
M[5, 1, 2:5, 1:3] -= 0.10
M[5, 7, 2:5, 3:5] += 0.07
M[5, 6, 2:5, 3:5] -= 0.025

# Liver: broad filled region, with the larger lobe on image left.
M[6, 0] -= 0.01
M[6, 4] += 0.01
M[6, 0, 1:6, 1:6] += 0.02
M[6, 4, 1:6, 1:6] -= 0.02
M[6, 0, 2:7, 0:3] += 0.045
M[6, 4, 2:7, 0:3] -= 0.045
M[6, 0, 2:7, 4:7] -= 0.045
M[6, 4, 2:7, 4:7] += 0.045
M[6, 5, 1:5, 1:4] -= 0.07
M[6, 8, 0:2, 1:6] += 0.06
M[6, 7, 3:5, 3:5] += 0.07
M[6, 7, 5:7, 1:3] += 0.07
M[6, 9, 5:7, 0:3] += 0.04

# Lungs: central air and a bright inferior diaphragmatic boundary.
M[7:9, 3] -= 0.025
M[7:9, 3, 1:6, 1:6] += 0.05
M[7:9, 8, 5:7, 1:6] += 0.07
M[7:9, 9, 0:2, 2:5] += 0.03
M[7:9, 7, 1:6, 0:2] += 0.035
M[7:9, 6, 1:6, 5:7] += 0.035

# Left lung: medial tissue on image left, lateral air on image right.
M[7, 0, 2:6, 0:3] += 0.055
M[7, 4, 2:6, 0:3] -= 0.055
M[7, 0, 2:6, 4:7] -= 0.055
M[7, 4, 2:6, 4:7] += 0.055
M[7, 3, 2:6, 4:7] += 0.045
M[7, 3, 2:6, 0:3] -= 0.045
M[7, 7, 2:6, 2:4] += 0.04

# Right lung: mirrored medial tissue and lateral air.
M[8, 0, 2:6, 4:7] += 0.055
M[8, 4, 2:6, 4:7] -= 0.055
M[8, 0, 2:6, 0:3] -= 0.055
M[8, 4, 2:6, 0:3] += 0.055
M[8, 3, 2:6, 0:3] += 0.045
M[8, 3, 2:6, 4:7] -= 0.045
M[8, 6, 2:6, 3:5] += 0.04

# Pancreas: lower-left head, central body, upper-right tail.
M[9, 0] -= 0.018
M[9, 4] += 0.018
M[9, 0, 4:7, 0:2] += 0.042
M[9, 4, 4:7, 0:2] -= 0.042
M[9, 0, 2:5, 2:4] += 0.042
M[9, 4, 2:5, 2:4] -= 0.042
M[9, 0, 0:3, 4:7] += 0.042
M[9, 4, 0:3, 4:7] -= 0.042
M[9, 6:10] += 0.012
M[9, 6, 2:4, 1:3] += 0.04
M[9, 8, 0:2, 3:6] += 0.04
M[9, 7, 3:5, 4:6] += 0.04
M[9, 9, 5:7, 0:3] += 0.04

# Spleen: smooth filled oval, without a pronounced internal fatty hilum.
M[10, 0] -= 0.028
M[10, 4] += 0.028
M[10, 0, 1:6, 1:6] += 0.056
M[10, 4, 1:6, 1:6] -= 0.056
M[10, 1, 2:5, 2:5] -= 0.07
M[10, 5, 2:5, 2:5] -= 0.08
M[10, 0, 1:6, 4:6] += 0.012
M[10, 4, 1:6, 4:6] -= 0.012
M[10, 0, 1:6, 1:3] -= 0.012
M[10, 4, 1:6, 1:3] += 0.012
M[10, 6, 1:6, 0:2] += 0.06
M[10, 7, 1:6, 5:7] += 0.06
M[10, 8, 0:2, 2:5] += 0.05
M[10, 9, 5:7, 2:5] += 0.05
```