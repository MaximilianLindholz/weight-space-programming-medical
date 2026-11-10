This is an unvalidated, hand-set CT heuristic; I cannot establish its test performance without images or evaluation.

**Filters.** Channels 0–3 are intensity hinges at −0.65, −0.25, 0.15, and 0.55. Their differences provide tissue occupancy, fluid-like intensity, ordinary soft tissue, and enhancement cues. Channel 4 detects near-white saturation; channel 5 detects very dark air-like pixels. Channels 6–7 detect bright and dark local irregularities. Channels 8–9 detect opposite horizontal edge directions.

**Readout.** Most evidence comes from the central 5×5 pooling cells, with additional central 3×3 and outer-ring evidence:
- **Bladder:** smooth fluid-like center, without substantial air or saturation.
- **Femurs:** saturated cortical ring, less-saturated marrow, and strong edges.
- **Heart:** solid, smooth, enhancing center with darker surroundings.
- **Kidneys:** enhancement, internal texture, and a relatively darker medial hilum.
- **Liver:** broad, smooth tissue occupancy, especially toward image-left and anteriorly.
- **Lungs:** extensive very dark interior, with mirrored medial soft-tissue indentations.
- **Pancreas:** mixed intensities, internal edges, and a central tissue band.
- **Spleen:** smooth soft tissue, lateral fullness, and a medial indentation.

The weak laterality templates assume patient-left appears on image-right; I cannot verify that convention for the stored arrays.

```edits
# Intensity hinges.
CW[0:4, 0, 1, 1] = 2.5
CW[4, 0, 1, 1] = 5
CW[5, 0, 1, 1] = -3

# Positive and negative local contrast.
CW[6, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CW[7, 0] = [[0.125, 0.125, 0.125], [0.125, -1, 0.125], [0.125, 0.125, 0.125]]

# Horizontal increase and decrease.
CW[8, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[9, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

CB[:] = [1.625, 0.625, -0.375, -1.375, -4.25, -2.1, -0.06, -0.06, -0.04, -0.04]
B[:] = [-0.5, -0.7, -0.7, -0.8, -1, -1, -0.9, -0.6, -0.6, -0.8, -0.5]

# 0: Bladder. Fluid-like interior and smooth central core.
M[0, 0] = -0.012
M[0, 1] = 0.012
M[0, 0, 1:6, 1:6] = 0.144
M[0, 1, 1:6, 1:6] = -0.26
M[0, 2, 1:6, 1:6] = 0.052
M[0, 3, 1:6, 1:6] = 0.064
M[0, 4, 1:6, 1:6] = -0.08
M[0, 5, 1:6, 1:6] = -0.06
M[0, 6:8, 1:6, 1:6] = -0.16
M[0, 0, 2:5, 2:5] += 0.08
M[0, 1, 2:5, 2:5] -= 0.16
M[0, 2, 2:5, 2:5] += 0.03
M[0, 3, 2:5, 2:5] += 0.05
M[0, 8:10, 2:5, 2:5] = -0.08

# 1 and 2: Femurs. Saturation, cortical edges, and less-white marrow.
M[1:3, 4] = 0.04
M[1:3, 0, 1:6, 1:6] = -0.016
M[1:3, 1, 1:6, 1:6] = 0.008
M[1:3, 2, 1:6, 1:6] = 0.08
M[1:3, 3, 1:6, 1:6] = -0.072
M[1:3, 4, 1:6, 1:6] = 0.32
M[1:3, 5, 1:6, 1:6] = -0.028
M[1:3, 6:8, 1:6, 1:6] = 0.08
M[1:3, 8:10, 1:6, 1:6] = 0.04
M[1:3, 0, 2:5, 2:5] += 0.06
M[1:3, 1, 2:5, 2:5] -= 0.12
M[1:3, 2, 2:5, 2:5] += 0.06
M[1:3, 4, 2:5, 2:5] -= 0.3

# Weak mirrored proximal-femur asymmetry.
M[1, 4, 1:4, 1:3] += 0.08
M[1, 4, 1:4, 4:6] -= 0.08
M[2, 4, 1:4, 1:3] -= 0.08
M[2, 4, 1:4, 4:6] += 0.08

# 3: Heart. Smooth enhancing core and darker outer context.
M[3, 0] = -0.012
M[3, 1] = 0.012
M[3, 5] = 0.02
M[3, 0, 1:6, 1:6] = 0.016
M[3, 1, 1:6, 1:6] = 0.068
M[3, 2, 1:6, 1:6] = -0.092
M[3, 3, 1:6, 1:6] = 0.008
M[3, 4, 1:6, 1:6] = -0.08
M[3, 5, 1:6, 1:6] = -0.04
M[3, 6:8, 1:6, 1:6] = -0.1
M[3, 0, 2:5, 2:5] -= 0.07
M[3, 1, 2:5, 2:5] += 0.21
M[3, 2, 2:5, 2:5] -= 0.16
M[3, 3, 2:5, 2:5] += 0.02
M[3, 8:10, 2:5, 2:5] = -0.06

# 4 and 5: Kidneys. Enhancement and moderate internal texture.
M[4:6, 0] = -0.016
M[4:6, 1] = 0.016
M[4:6, 0, 1:6, 1:6] = 0.024
M[4:6, 1, 1:6, 1:6] = 0.036
M[4:6, 2, 1:6, 1:6] = -0.024
M[4:6, 3, 1:6, 1:6] = -0.036
M[4:6, 4, 1:6, 1:6] = -0.1
M[4:6, 5, 1:6, 1:6] = -0.028
M[4:6, 6:8, 1:6, 1:6] = 0.12
M[4:6, 0, 2:5, 2:5] += 0.04
M[4:6, 1, 2:5, 2:5] -= 0.08
M[4:6, 2, 2:5, 2:5] += 0.04
M[4:6, 4, 2:5, 2:5] -= 0.1

# Left kidney: relatively darker medial-left hilum.
M[4, 1, 2:5, 1:3] -= 0.06
M[4, 2, 2:5, 1:3] += 0.06
M[4, 1, 2:5, 4:6] += 0.06
M[4, 2, 2:5, 4:6] -= 0.06
M[4, 5, 2:5, 1:3] += 0.032
M[4, 5, 2:5, 4:6] -= 0.032
M[4, 8, 2:5, 2:4] += 0.08
M[4, 9, 2:5, 2:4] -= 0.04

# Right kidney: mirrored hilar evidence.
M[5, 1, 2:5, 1:3] += 0.06
M[5, 2, 2:5, 1:3] -= 0.06
M[5, 1, 2:5, 4:6] -= 0.06
M[5, 2, 2:5, 4:6] += 0.06
M[5, 5, 2:5, 1:3] -= 0.032
M[5, 5, 2:5, 4:6] += 0.032
M[5, 9, 2:5, 3:5] += 0.08
M[5, 8, 2:5, 3:5] -= 0.04

# 6: Liver. Broad smooth tissue and substantial peripheral occupancy.
M[6, 0] = 0.036
M[6, 1] = -0.036
M[6, 0, 1:6, 1:6] = 0.044
M[6, 1, 1:6, 1:6] = 0.044
M[6, 2, 1:6, 1:6] = -0.2
M[6, 3, 1:6, 1:6] = 0.112
M[6, 4, 1:6, 1:6] = -0.08
M[6, 5, 1:6, 1:6] = -0.024
M[6, 6:8, 1:6, 1:6] = -0.16
M[6, 8:10, 2:5, 2:5] = -0.04

# Broad image-left lobe, anterior extension, posteromedial taper.
M[6, 0, 2:6, 1:3] += 0.04
M[6, 1, 2:6, 1:3] -= 0.04
M[6, 0, 4:6, 4:6] -= 0.08
M[6, 1, 4:6, 4:6] += 0.08
M[6, 0, 1:3, 3:6] += 0.02
M[6, 1, 1:3, 3:6] -= 0.02
M[6, 9, 3:6, 3:6] += 0.06
M[6, 8, 3:6, 3:6] -= 0.03

# 7 and 8: Lungs. Extensive air-like interior.
M[7:9, 5] = 0.04
M[7:9, 0, 1:6, 1:6] = -0.036
M[7:9, 1, 1:6, 1:6] = 0.032
M[7:9, 2, 1:6, 1:6] = 0.008
M[7:9, 3, 1:6, 1:6] = -0.004
M[7:9, 4, 1:6, 1:6] = -0.04
M[7:9, 5, 1:6, 1:6] = 0.18
M[7:9, 6:8, 1:6, 1:6] = 0.02
M[7:9, 5, 2:5, 2:5] += 0.07

# Left lung: medial-left tissue indentation and lateral-right air.
M[7, 0, 3:6, 1:3] += 0.048
M[7, 1, 3:6, 1:3] -= 0.048
M[7, 5, 3:6, 1:3] -= 0.048
M[7, 0, 3:6, 4:6] -= 0.048
M[7, 1, 3:6, 4:6] += 0.048
M[7, 5, 3:6, 4:6] += 0.048
M[7, 9, 3:6, 2:5] += 0.08
M[7, 8, 3:6, 2:5] -= 0.04

# Right lung: mirrored mediastinal boundary.
M[8, 0, 3:6, 1:3] -= 0.048
M[8, 1, 3:6, 1:3] += 0.048
M[8, 5, 3:6, 1:3] += 0.048
M[8, 0, 3:6, 4:6] += 0.048
M[8, 1, 3:6, 4:6] -= 0.048
M[8, 5, 3:6, 4:6] -= 0.048
M[8, 8, 3:6, 2:5] += 0.08
M[8, 9, 3:6, 2:5] -= 0.04

# 9: Pancreas. Heterogeneous tissue, internal edges, adjacent dark pockets.
M[9, 4] = -0.02
M[9, 0, 1:6, 1:6] = 0.036
M[9, 1, 1:6, 1:6] = -0.008
M[9, 2, 1:6, 1:6] = -0.072
M[9, 3, 1:6, 1:6] = 0.044
M[9, 4, 1:6, 1:6] = -0.08
M[9, 5, 1:6, 1:6] = 0.032
M[9, 6:8, 1:6, 1:6] = 0.24
M[9, 8:10, 1:6, 1:6] = 0.1
M[9, 0, 3:5, 1:6] += 0.02
M[9, 1, 3:5, 1:6] -= 0.02
M[9, 5, 0:2, 1:6] += 0.016
M[9, 5, 5:7, 1:6] += 0.016

# 10: Spleen. Smooth soft tissue with a compact core.
M[10, 0] = -0.02
M[10, 1] = 0.02
M[10, 0, 1:6, 1:6] = 0.024
M[10, 1, 1:6, 1:6] = 0.096
M[10, 2, 1:6, 1:6] = -0.256
M[10, 3, 1:6, 1:6] = 0.136
M[10, 4, 1:6, 1:6] = -0.1
M[10, 5, 1:6, 1:6] = -0.024
M[10, 6:8, 1:6, 1:6] = -0.12
M[10, 1, 2:5, 2:5] += 0.04
M[10, 2, 2:5, 2:5] -= 0.08
M[10, 3, 2:5, 2:5] += 0.04
M[10, 8:10, 2:5, 2:5] = -0.04

# Lateral-right fullness and anteromedial-left indentation.
M[10, 0, 2:6, 4:6] += 0.04
M[10, 1, 2:6, 4:6] -= 0.04
M[10, 0, 1:3, 1:3] -= 0.06
M[10, 1, 1:3, 1:3] += 0.06
M[10, 5, 1:3, 1:3] += 0.05
M[10, 8, 2:5, 1:4] += 0.04
M[10, 9, 2:5, 1:4] -= 0.02
```