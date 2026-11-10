This design uses intensity, texture, and coarse anatomical shape rather than learned features.

- **Filters 0–4:** grayscale level, near-white dense material, dark fat/background, nearly black air, and positive-intensity enhancement.
- **Filters 5–8:** rightward, leftward, downward, and upward intensity rises. **Filter 9:** small bright peaks, emphasizing cortex, vessels, and fine texture.
- **Bladder:** smooth, relatively dark-gray center with surrounding fat. **Femurs:** dense material and longitudinal boundaries, with mirrored head/shaft placement.
- **Heart:** central and lower-right soft tissue, with air at the upper corners. **Kidneys:** enhanced peripheral tissue surrounding a less enhanced, medially indented center.
- **Liver:** broad, comparatively uniform upper/left tissue with an inferior-right taper. **Lungs:** dark central fields, reversed-polarity boundaries, and medial soft-tissue encroachment.
- **Pancreas:** a textured transverse tissue band amid mixed dark surroundings. **Spleen:** smooth, moderately enhanced central tissue with an approximately oval boundary.

Paired templates assume anatomical left appears on image right. These are unvalidated heuristics; their performance and that orientation assumption cannot be checked here.

```edits
# Intensity features.
CW[0, 0] = [[0, 0, 0], [0, 0.5, 0], [0, 0, 0]]
CW[1, 0] = [[0, 0, 0], [0, 3, 0], [0, 0, 0]]
CW[2, 0] = [[0, 0, 0], [0, -2, 0], [0, 0, 0]]
CW[3, 0] = [[0, 0, 0], [0, -10, 0], [0, 0, 0]]
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]

# Directional edges.
CW[5, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[6, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[7, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[8, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

# Thresholded local bright peaks.
CW[9, 0] = [[0, -0.25, 0], [-0.25, 1, -0.25], [0, -0.25, 0]]
CB[:] = [0.5, -2, -1, -9, 0, 0, 0, 0, 0, -0.04]

B[:] = [1, -0.65, -0.65, -1.3, -0.95, -0.95, -1.2, -0.45, -0.45, -0.95, -1]

# 0: Bladder -- low-enhancement, smooth central contents.
M[0, 0, 2:5, 2:5] = -0.111111
M[0, 1] = -0.016327
M[0, 2, 2:5, 2:5] = -0.177778
M[0, 3] = -0.014286
M[0, 4, 2:5, 2:5] = -0.355556
M[0, 5:9, 2:5, 2:5] = -0.088889
M[0, 9, 2:5, 2:5] = -0.166667

# Fat outside the central contents.
M[0, 2, 0:2, 0:2] = 0.01875
M[0, 2, 0:2, 5:7] = 0.01875
M[0, 2, 5:7, 0:2] = 0.01875
M[0, 2, 5:7, 5:7] = 0.01875

# Enclosing bright-organ boundary.
M[0, 5, 1:6, 0:2] += 0.00625
M[0, 6, 1:6, 5:7] += 0.00625
M[0, 7, 0:2, 2:5] += 0.010417
M[0, 8, 5:7, 2:5] += 0.010417

# 1,2: Femurs -- dense material, enhancement, and longitudinal edges.
M[1:3, 1] = 0.030612
M[1:3, 1, 1:6, 1:6] += 0.24
M[1:3, 2, 1:6, 1:6] = -0.024
M[1:3, 3] = -0.010204
M[1:3, 4, 1:6, 1:6] = 0.016
M[1:3, 5:7, 1:6, 1:6] = 0.024
M[1:3, 7:9, 1:6, 1:6] = -0.01
M[1:3, 9, 1:6, 1:6] = 0.012

# Left femur: upper-medial head, lower-lateral shaft.
M[1, 1, 0:3, 0:3] += 0.05
M[1, 1, 0:3, 4:7] -= 0.05
M[1, 1, 4:7, 0:3] -= 0.05
M[1, 1, 4:7, 4:7] += 0.05
M[1, 4, 0:3, 0:3] += 0.016667
M[1, 4, 0:3, 4:7] -= 0.016667
M[1, 4, 4:7, 0:3] -= 0.016667
M[1, 4, 4:7, 4:7] += 0.016667

# Right femur: mirrored head and shaft evidence.
M[2, 1, 0:3, 0:3] -= 0.05
M[2, 1, 0:3, 4:7] += 0.05
M[2, 1, 4:7, 0:3] += 0.05
M[2, 1, 4:7, 4:7] -= 0.05
M[2, 4, 0:3, 0:3] -= 0.016667
M[2, 4, 0:3, 4:7] += 0.016667
M[2, 4, 4:7, 0:3] += 0.016667
M[2, 4, 4:7, 4:7] -= 0.016667

# 3: Heart -- central soft tissue.
M[3, 0, 1:6, 1:6] = 0.128
M[3, 1] = -0.02449
M[3, 1, 1:6, 1:6] -= 0.064
M[3, 4, 1:6, 1:6] = -0.064

# Central enhancement and lower-right tissue.
M[3, 4, 2:5, 2:5] += 0.088889
M[3, 0, 4:6, 2:6] += 0.075
M[3, 1, 4:6, 2:6] -= 0.0375
M[3, 4, 4:6, 2:6] -= 0.0375

# Upper-corner lung air, but not a globally air-filled crop.
M[3, 3] = -0.006122
M[3, 3, 0:2, 0:2] += 0.1
M[3, 3, 0:2, 5:7] += 0.1
M[3, 5:9, 2:5, 2:5] = -0.035556
M[3, 9, 2:5, 2:5] = -0.055556

# 4,5: Kidneys -- central tissue, limited bone and air.
M[4:6, 0, 1:6, 1:6] = 0.096
M[4:6, 1] = -0.020408
M[4:6, 1, 1:6, 1:6] -= 0.048
M[4:6, 3] = -0.02449
M[4:6, 4, 1:6, 1:6] = -0.048

# Enhanced annulus relative to the hilar center.
M[4:6, 4, 1:6, 1:6] += 0.1125
M[4:6, 4, 2:5, 2:5] -= 0.1125
M[4:6, 4, 2:5, 2:5] -= 0.111111

# Surrounding fat.
M[4:6, 2, 0:2, 0:2] = 0.01875
M[4:6, 2, 0:2, 5:7] = 0.01875
M[4:6, 2, 5:7, 0:2] = 0.01875
M[4:6, 2, 5:7, 5:7] = 0.01875

# Internal hilar structure and enclosing boundaries.
M[4:6, 5:9, 2:5, 2:5] = 0.033333
M[4:6, 9, 2:5, 2:5] = 0.022222
M[4:6, 5, 1:6, 0:2] += 0.0075
M[4:6, 6, 1:6, 5:7] += 0.0075
M[4:6, 7, 0:2, 2:5] += 0.0125
M[4:6, 8, 5:7, 2:5] += 0.0125

# Left kidney: medial indentation on image left.
M[4, 2, 2:5, 1:3] += 0.058333
M[4, 2, 2:5, 4:6] -= 0.058333
M[4, 0, 2:5, 4:6] += 0.083333
M[4, 0, 2:5, 1:3] -= 0.083333
M[4, 1, 2:5, 4:6] -= 0.041667
M[4, 1, 2:5, 1:3] += 0.041667
M[4, 4, 2:5, 4:6] -= 0.041667
M[4, 4, 2:5, 1:3] += 0.041667

# Right kidney: mirrored medial indentation.
M[5, 2, 2:5, 4:6] += 0.058333
M[5, 2, 2:5, 1:3] -= 0.058333
M[5, 0, 2:5, 1:3] += 0.083333
M[5, 0, 2:5, 4:6] -= 0.083333
M[5, 1, 2:5, 1:3] -= 0.041667
M[5, 1, 2:5, 4:6] += 0.041667
M[5, 4, 2:5, 1:3] -= 0.041667
M[5, 4, 2:5, 4:6] += 0.041667

# 6: Liver -- broad central parenchyma.
M[6, 0, 1:6, 1:6] = 0.136
M[6, 1] = -0.012245
M[6, 1, 1:6, 1:6] -= 0.068
M[6, 4, 1:6, 1:6] = -0.068

# Broad upper-left extent.
M[6, 0, 0:4, 0:3] += 0.058334
M[6, 1, 0:4, 0:3] -= 0.029167
M[6, 4, 0:4, 0:3] -= 0.029167
M[6, 0, 0:2, 1:6] += 0.05
M[6, 1, 0:2, 1:6] -= 0.025
M[6, 4, 0:2, 1:6] -= 0.025

# Inferior-right taper.
M[6, 0, 4:7, 4:7] -= 0.044444
M[6, 1, 4:7, 4:7] += 0.022222
M[6, 4, 4:7, 4:7] += 0.022222
M[6, 2, 4:7, 4:7] = 0.027778

# Relatively homogeneous, non-aerated tissue.
M[6, 3] = -0.018367
M[6, 5:9, 1:6, 1:6] = -0.012
M[6, 9, 1:6, 1:6] = -0.028

# 7,8: Lungs -- central air and low attenuation.
M[7:9, 1] = -0.030612
M[7:9, 2, 1:6, 1:6] = 0.036
M[7:9, 3, 1:6, 1:6] = 0.096
M[7:9, 4, 1:6, 1:6] = -0.016

# Boundaries of a dark field inside brighter tissue.
M[7:9, 6, 1:6, 0:2] = 0.00625
M[7:9, 5, 1:6, 5:7] = 0.00625
M[7:9, 8, 0:2, 2:5] = 0.010417
M[7:9, 7, 5:7, 2:5] = 0.010417

# Left lung: lateral air on image right, medial tissue on image left.
M[7, 3, 1:6, 4:6] += 0.04
M[7, 3, 1:6, 1:3] -= 0.04
M[7, 2, 1:6, 4:6] += 0.02
M[7, 2, 1:6, 1:3] -= 0.02
M[7, 0, 1:6, 4:6] = -0.02
M[7, 0, 1:6, 1:3] = 0.02

# Right lung: mirrored lateral air and medial tissue.
M[8, 3, 1:6, 1:3] += 0.04
M[8, 3, 1:6, 4:6] -= 0.04
M[8, 2, 1:6, 1:3] += 0.02
M[8, 2, 1:6, 4:6] -= 0.02
M[8, 0, 1:6, 1:3] = -0.02
M[8, 0, 1:6, 4:6] = 0.02

# 9: Pancreas -- transverse tissue band.
M[9, 0, 2:5, :] = 0.12381
M[9, 1] = -0.018367
M[9, 1, 2:5, :] -= 0.061905
M[9, 4, 2:5, :] = -0.061905

# Mixed fatty surroundings, without predominantly air or bone.
M[9, 2] = 0.012245
M[9, 3] = -0.018367

# Tissue concentrated in middle rows rather than top and bottom.
M[9, 0, 2:5, :] += 0.038096
M[9, 1, 2:5, :] -= 0.019048
M[9, 4, 2:5, :] -= 0.019048
M[9, 0, 0:2, :] = -0.028572
M[9, 0, 5:7, :] = -0.028572
M[9, 1, 0:2, :] += 0.014286
M[9, 1, 5:7, :] += 0.014286
M[9, 4, 0:2, :] = 0.014286
M[9, 4, 5:7, :] = 0.014286

# Moderate enhancement and appreciable internal texture.
M[9, 4, 2:5, :] -= 0.014286
M[9, 5:9, 2:5, 1:6] = 0.093333
M[9, 9, 2:5, 1:6] = 0.073333

# 10: Spleen -- smooth, centrally concentrated parenchyma.
M[10, 0, 1:6, 1:6] = 0.136
M[10, 1] = -0.016327
M[10, 1, 1:6, 1:6] -= 0.068
M[10, 4, 1:6, 1:6] = -0.068
M[10, 0, 2:5, 2:5] += 0.044444
M[10, 1, 2:5, 2:5] -= 0.022222
M[10, 4, 2:5, 2:5] -= 0.022222

# Less pronounced cortical enhancement than a kidney.
M[10, 4, 1:6, 1:6] -= 0.0375
M[10, 4, 2:5, 2:5] += 0.0375

# Fat around the approximately oval organ.
M[10, 2, 0:2, 0:2] = 0.015625
M[10, 2, 0:2, 5:7] = 0.015625
M[10, 2, 5:7, 0:2] = 0.015625
M[10, 2, 5:7, 5:7] = 0.015625

# Penalize air and central heterogeneity.
M[10, 3] = -0.026531
M[10, 5:9, 2:5, 2:5] = -0.066667
M[10, 9, 2:5, 2:5] = -0.088889

# Smooth enclosing boundary.
M[10, 5, 1:6, 0:2] += 0.00375
M[10, 6, 1:6, 5:7] += 0.00375
M[10, 7, 0:2, 2:5] += 0.00625
M[10, 8, 5:7, 2:5] += 0.00625
```