This is an unvalidated, anatomy-inspired heuristic; I cannot estimate its accuracy without images.

Filters **0–5** measure grayscale intensity and five progressively brighter intensity hinges. Their combinations form broad, piecewise-linear intensity preferences. Filters **6–9** are opposing horizontal and vertical Sobel filters; paired responses measure local edge/texture strength.

The outputs read these features as follows:
- **Bladder:** fluid-like grayscale and a smooth, heavily weighted center.
- **Femurs:** near-white cortical evidence, emphasizing the surrounding ring.
- **Heart:** bright central tissue, central smoothness, and dark corners.
- **Kidneys:** relatively bright annular tissue and some interior texture.
- **Liver:** widespread medium-bright tissue, low texture, and relatively little center-to-corner contrast.
- **Lungs:** predominantly dark interiors.
- **Pancreas:** intermediate grayscale with comparatively strong texture.
- **Spleen:** compact, smooth, medium-bright central tissue.

Spatial templates are reflection-symmetric rather than assuming an unverified sagittal orientation. Kidney and lung laterality receive only weak brightness-context adjustments. The femur outputs deliberately share weights because I have no defensible laterality cue.

```edits
# Intensity basis: y, ReLU(y-0.15), ReLU(y-0.35),
# ReLU(y-0.55), ReLU(y-0.75), ReLU(y-0.90), where y=p/255.
CW[0:6, 0, 1, 1] = 0.5
CB[0:6] = [0.5, 0.35, 0.15, -0.05, -0.25, -0.4]

# Opposing horizontal gradients.
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

# Opposing vertical gradients.
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

# 0: Bladder. Fluid-like intensity, strongly center-weighted.
M[0, 0:6, 1:6, 1:6] = 0.0175
M[0, 0:6, 2:5, 2:5] = 0.08
M[0, 0] *= 6.666667
M[0, 1] *= 8.333333
M[0, 2] *= -25
M[0, 3] *= 5
M[0, 4] *= -1.666667
M[0, 5] *= 6.666667
M[0, 6:10, 2:5, 2:5] = -0.444444

# 1, 2: Femurs. Saturated bone, with a rim-favoring spatial mask.
M[1:3, 4:6] = 0.02
M[1:3, 4:6, 1:6, 1:6] = 0.025
M[1:3, 4:6, 2:5, 2:5] = 0.013333333
M[1:3, 4] *= 13.333333
M[1:3, 5] *= 126.666667
M[1:3, 6:10, 1:6, 1:6] = 0.02

# 3: Heart. Bright soft tissue in a compact central region.
M[3, 0:6, 1:6, 1:6] = 0.02875
M[3, 0:6, 2:5, 2:5] = 0.06
M[3, 0] *= 3.333333
M[3, 1] *= 4.166667
M[3, 2] *= 0.5
M[3, 3] *= -5
M[3, 4] *= -24.333333
M[3, 5] *= 21.333333

# Heart: center-to-corner contrast and additional dark-corner evidence.
M[3, 0, 2:5, 2:5] += 0.088888889
M[3, 0, 0:2, 0:2] -= 0.175
M[3, 0, 0:2, 5:7] -= 0.175
M[3, 0, 5:7, 0:2] -= 0.175
M[3, 0, 5:7, 5:7] -= 0.175
M[3, 1, 0:2, 0:2] += 0.125
M[3, 1, 0:2, 5:7] += 0.125
M[3, 1, 5:7, 0:2] += 0.125
M[3, 1, 5:7, 5:7] += 0.125
M[3, 6:10, 2:5, 2:5] = -0.222222222

# 4, 5: Kidneys. Bright parenchyma, with reduced weight on the hilum.
M[4:6, 0:6, 1:6, 1:6] = 0.045
M[4:6, 0:6, 2:5, 2:5] = 0.031111111
M[4:6, 0] *= 3.333333
M[4:6, 1] *= 0.166667
M[4:6, 2] *= 2
M[4:6, 3] *= -0.5
M[4:6, 4] *= -17
M[4:6, 5] *= -3
M[4:6, 0, 2:5, 2:5] += 0.088888889
M[4:6, 6:10, 2:5, 2:5] = 0.166666667

# Left kidney: slightly darker surrounding context.
M[4, 0, 0:2, 0:2] -= 0.075
M[4, 0, 0:2, 5:7] -= 0.075
M[4, 0, 5:7, 0:2] -= 0.075
M[4, 0, 5:7, 5:7] -= 0.075

# Right kidney: slightly brighter surrounding context.
M[5, 0, 0:2, 0:2] -= 0.025
M[5, 0, 0:2, 5:7] -= 0.025
M[5, 0, 5:7, 0:2] -= 0.025
M[5, 0, 5:7, 5:7] -= 0.025

# 6: Liver. Broad spatial coverage and medium-bright tissue.
M[6, 0:6] = 0.01
M[6, 0:6, 1:6, 1:6] = 0.025
M[6, 0:6, 2:5, 2:5] = 0.04
M[6, 0] *= 1.333333
M[6, 1] *= 6.666667
M[6, 2] *= -2
M[6, 3] *= -10
M[6, 4] *= -10.666667
M[6, 5] *= 14.666667

# Liver: favor broad filling rather than a sharply isolated central oval.
M[6, 0, 2:5, 2:5] -= 0.133333333
M[6, 0, 0:2, 0:2] += 0.075
M[6, 0, 0:2, 5:7] += 0.075
M[6, 0, 5:7, 0:2] += 0.075
M[6, 0, 5:7, 5:7] += 0.075
M[6, 6:10, 1:6, 1:6] = -0.1

# 7, 8: Lungs. Strong preference for dark interiors.
M[7:9, 0:6, 1:6, 1:6] = 0.04
M[7:9, 0] *= -8
M[7:9, 1] *= -3.5
M[7:9, 2] *= 4
M[7:9, 3] *= 5
M[7:9, 4] *= 2.5
M[7:9, 5] = 0
M[7:9, 6:10, 1:6, 1:6] = 0.01

# Weak laterality cue: more soft-tissue admixture favors left lung.
M[7, 0, 1:6, 1:6] += 0.02
M[8, 0, 1:6, 1:6] -= 0.02

# 9: Pancreas. Broad intermediate-intensity preference.
M[9, 0:6, 1:6, 1:6] = 0.04
M[9, 0] *= 3.333333
M[9, 1] *= 1.666667
M[9, 2] *= -2.5
M[9, 3] *= -6.5
M[9, 4] *= -7.333333
M[9, 5] *= 11.333333

# Pancreas: heterogeneous tissue and modest central concentration.
M[9, 6:10, 1:6, 1:6] = 0.16
M[9, 0, 2:5, 2:5] += 0.033333333
M[9, 0, 0:2, 0:2] -= 0.01875
M[9, 0, 0:2, 5:7] -= 0.01875
M[9, 0, 5:7, 0:2] -= 0.01875
M[9, 0, 5:7, 5:7] -= 0.01875

# 10: Spleen. Compact medium-bright tissue.
M[10, 0:6, 1:6, 1:6] = 0.02875
M[10, 0:6, 2:5, 2:5] = 0.06
M[10, 0] *= 3.333333
M[10, 1] *= 4.166667
M[10, 2] = 0
M[10, 3] *= -10
M[10, 4] *= -14.166667
M[10, 5] *= 16.666667

# Spleen: central concentration and low interior texture.
M[10, 0, 2:5, 2:5] += 0.133333333
M[10, 0, 0:2, 0:2] -= 0.075
M[10, 0, 0:2, 5:7] -= 0.075
M[10, 0, 5:7, 0:2] -= 0.075
M[10, 0, 5:7, 5:7] -= 0.075
M[10, 6:10, 2:5, 2:5] = -0.333333333

# Affinity intercepts and modest shape/texture offsets.
B[:] = [-1.8, -1.1, -1.1, -1.7, -1.1, -1.38, -0.73, 2.365, 2.585, -0.83, -1.5]
```