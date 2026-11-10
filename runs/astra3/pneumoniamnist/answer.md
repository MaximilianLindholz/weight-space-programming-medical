I would use an **exposure-compensated lung-opacity heuristic**, with weaker evidence from lung boundaries and local contrast:

- **Filters 0, 1, 2, 9:** Gaussian-smoothed brightness, darkness below 0.40, highlights above 0.85, and darkness below 0.15, respectively, in pixel-intensity units of 0–1. Their readout combination clips extreme brightness and bounds the contribution of very dark pixels.
- **Filters 3–6:** Opposite horizontal and vertical gradients. The output reads their expected signs around dark lung fields: lateral/medial borders, apices, and bases. Preserved boundaries contribute normal evidence.
- **Filters 7–8:** Opposite center-surround contrasts, supplying a small normal-evidence contribution from retained fine contrast.
- **Spatial readout:** Opacity contributes positively across both lung fields, with reduced weight over the lower image-right heart region. Central chest brightness and bounded peripheral darkness provide exposure references. Dark lung interiors contribute negatively.

These are unvalidated hand-set weights; neither performance nor probability calibration can be established without evaluation.

```edits
# Smoothed intensity and intensity hinges.
CW[0, 0] = [[0.03125, 0.0625, 0.03125], [0.0625, 0.125, 0.0625], [0.03125, 0.0625, 0.03125]]
CW[1, 0] = [[-0.03125, -0.0625, -0.03125], [-0.0625, -0.125, -0.0625], [-0.03125, -0.0625, -0.03125]]
CW[2, 0] = [[0.03125, 0.0625, 0.03125], [0.0625, 0.125, 0.0625], [0.03125, 0.0625, 0.03125]]

# Rightward and leftward brightening.
CW[3, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[4, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

# Downward and upward brightening.
CW[5, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[6, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

# Bright and dark center-surround residuals.
CW[7, 0] = [[-0.03125, -0.0625, -0.03125], [-0.0625, 0.375, -0.0625], [-0.03125, -0.0625, -0.03125]]
CW[8, 0] = [[0.03125, 0.0625, 0.03125], [0.0625, -0.375, 0.0625], [0.03125, 0.0625, 0.03125]]

# Low-intensity clipping hinge.
CW[9, 0] = [[-0.03125, -0.0625, -0.03125], [-0.0625, -0.125, -0.0625], [-0.03125, -0.0625, -0.03125]]

CB[:] = [0.5, -0.1, -0.35, -0.025, -0.025, -0.025, -0.025, -0.015, -0.015, -0.35]

# Lung brightness minus central-chest reference.
M[0, 0] = [
[0, 0, 0, 0, 0, 0, 0],
[0, 0.25, 0.5, -0.75, 0.5, 0.25, 0],
[0, 0.55, 0.75, -2, 0.65, 0.55, 0],
[0, 0.65, 0.75, -2, 0.4, 0.7, 0],
[0, 0.7, 0.6, -1.75, 0.2, 0.65, 0],
[0, 0.4, 0.3, -0.5, 0.1, 0.55, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Dark lung evidence, with peripheral darkness as an exposure reference.
M[0, 1] = [
[0.5, 0, 0, 0, 0, 0, 0.5],
[0.4, -0.1, -0.2, 0, -0.2, -0.1, 0.4],
[0.25, -0.22, -0.3, 0, -0.26, -0.22, 0.25],
[0.15, -0.26, -0.3, 0, -0.16, -0.28, 0.15],
[0.1, -0.28, -0.24, 0, -0.08, -0.26, 0.1],
[0.1, -0.16, -0.12, 0, -0.04, -0.22, 0.1],
[0, 0, 0, 0, 0, 0, 0]
]

# Cap the brightness feature above 0.85.
M[0, 2] = [
[0, 0, 0, 0, 0, 0, 0],
[0, -0.25, -0.5, 0.75, -0.5, -0.25, 0],
[0, -0.55, -0.75, 2, -0.65, -0.55, 0],
[0, -0.65, -0.75, 2, -0.4, -0.7, 0],
[0, -0.7, -0.6, 1.75, -0.2, -0.65, 0],
[0, -0.4, -0.3, 0.5, -0.1, -0.55, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Expected horizontal boundaries of aerated lung fields.
M[0, 3, 1:6, 2] = [-0.15, -0.25, -0.25, -0.2, -0.1]
M[0, 3, 1:6, 5] = [-0.1, -0.2, -0.25, -0.25, -0.15]
M[0, 4, 1:6, 1] = [-0.1, -0.2, -0.25, -0.25, -0.15]
M[0, 4, 1:6, 4] = [-0.15, -0.25, -0.2, -0.1, -0.05]

# Basal and apical boundaries.
M[0, 5, 4] = [0, -0.1, -0.1, 0, -0.025, -0.1, 0]
M[0, 5, 5] = [0, -0.2, -0.15, 0, -0.05, -0.2, 0]
M[0, 6, 1] = [0, -0.1, -0.15, 0, -0.15, -0.1, 0]

# Weak fine-contrast evidence, avoiding the central heart and diaphragm.
M[0, 7:9, 1:5, 1:3] = -0.15
M[0, 7:9, 1:3, 4:6] = -0.15
M[0, 7:9, 3:5, 5] = -0.15

# Floor brightness at 0.15 and bound both darkness contributions.
M[0, 9] = [
[-0.5, 0, 0, 0, 0, 0, -0.5],
[-0.4, 0.35, 0.7, -0.75, 0.7, 0.35, -0.4],
[-0.25, 0.77, 1.05, -2, 0.91, 0.77, -0.25],
[-0.15, 0.91, 1.05, -2, 0.56, 0.98, -0.15],
[-0.1, 0.98, 0.84, -1.75, 0.28, 0.91, -0.1],
[-0.1, 0.56, 0.42, -0.5, 0.14, 0.77, -0.1],
[0, 0, 0, 0, 0, 0, 0]
]

B[0] = 0.2
```