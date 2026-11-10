I use fixed intensity and shape heuristics, not learned organ templates.

- **Filters 0–4:** intensity hinges. Their linear combinations distinguish very dark air, lower-density fluid, ordinary soft tissue, and very bright bone.
- **Filters 5–8:** right-, left-, down-, and up-facing Sobel edges.
- **Filter 9:** bright local detail, such as cortical rims, vessels, and heterogeneous internal texture.

The readouts favor:
- **Bladder:** smooth, lower-density central contents with an enclosing boundary.
- **Femurs:** very bright material, vertical boundaries, and opposite head-to-shaft diagonals.
- **Heart:** a broad soft-tissue center with dark peripheral lung.
- **Kidneys:** soft-tissue cortex around a less-dense center, internal detail, and opposite medial indentations.
- **Liver:** relatively uniform soft tissue over a broad area.
- **Lungs:** extensive central darkness, reversed boundary polarity, and opposite medial soft-tissue intrusions.
- **Pancreas:** a heterogeneous horizontal central band.
- **Spleen:** a smoother, vertically concentrated soft-tissue region.

The paired-organ masks assume a radiological left–right convention; that assumption is unverified. These weights are an unvalidated attempt, and I cannot estimate their test performance.

```edits
# Intensity hinges
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[2, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CW[3, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[4, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]

# Signed, transversely smoothed gradients
CW[5, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[6, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[7, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[8, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

# Positive local contrast
CW[9, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[:] = [1, -0.5, -0.55, 0.2, -0.15, -0.025, -0.025, -0.025, -0.025, -0.04]

# Baseline intensity evidence; biases include hinge-combination constants
B[:] = [-4.31, -0.48075, -0.48075, -1.76275, -1.5935, -1.5935, -2.0845, 0.47175, 0.47175, -1.514, -2.46525]

# Bladder
M[0, 0] = 0.2
M[0, 1] = -0.375
M[0, 2] = 0.04
M[0, 3] = -0.375
M[0, 4] = 0.15

# Femurs
M[1:3, 0] = 0.015
M[1:3, 1] = 0.455
M[1:3, 2] = -0.045
M[1:3, 3] = -0.015
M[1:3, 4] = -0.015

# Heart
M[3, 0] = 0.055
M[3, 1] = 0.08
M[3, 2] = 0.025
M[3, 3] = 0.09
M[3, 4] = -0.345

# Kidneys
M[4:6, 0] = 0.07
M[4:6, 1] = 0.13
M[4:6, 2] = -0.05
M[4:6, 3] = 0.03
M[4:6, 4] = -0.27

# Liver
M[6, 0] = 0.09
M[6, 1] = 0.04
M[6, 2] = -0.11
M[6, 3] = 0.04
M[6, 4] = -0.35

# Lungs
M[7:9, 0] = -0.035
M[7:9, 1] = -0.165
M[7:9, 2] = 0.265
M[7:9, 3] = 0.045
M[7:9, 4] = 0.015

# Pancreas
M[9, 0] = 0.08
M[9, 1] = -0.06
M[9, 2] = -0.08
M[9, 3] = -0.06
M[9, 4] = -0.12

# Spleen
M[10, 0] = 0.105
M[10, 1] = -0.015
M[10, 2] = -0.015
M[10, 3] = -0.025
M[10, 4] = -0.265

# Bladder: central contents versus the four corners
M[0, 0, 2:5, 2:5] += 0.16
M[0, 0, 0:2, 0:2] -= 0.09
M[0, 0, 0:2, 5:7] -= 0.09
M[0, 0, 5:7, 0:2] -= 0.09
M[0, 0, 5:7, 5:7] -= 0.09

# Femur-left: medial upper head and lateral lower shaft
M[1, 1, 0:3, 0:3] += 0.14
M[1, 1, 0:3, 4:7] -= 0.14
M[1, 1, 4:7, 0:3] -= 0.14
M[1, 1, 4:7, 4:7] += 0.14

# Femur-right: reflected diagonal
M[2, 1, 0:3, 0:3] -= 0.14
M[2, 1, 0:3, 4:7] += 0.14
M[2, 1, 4:7, 0:3] += 0.14
M[2, 1, 4:7, 4:7] -= 0.14

# Heart: broad bright center
M[3, 0] -= 0.05
M[3, 0, 1:6, 1:6] += 0.098

# Heart: peripheral air is useful, central air is not
M[3, 2] += 0.16
M[3, 2, 1:6, 1:6] -= 0.32

# Kidneys: broad cortex with a less-dense central strip
M[4:6, 0] -= 0.03
M[4:6, 0, 1:6, 1:6] += 0.072
M[4:6, 0, 2:5, 3] -= 0.11

# Kidney-left: medial indentation on the image-left side
M[4, 0, 2:5, 1:3] -= 0.05
M[4, 0, 2:5, 4:6] += 0.05
M[4, 0, 0:2, 0:3] -= 0.02
M[4, 0, 0:2, 4:7] += 0.02

# Kidney-right: reflected indentation and superior context
M[5, 0, 2:5, 1:3] += 0.05
M[5, 0, 2:5, 4:6] -= 0.05
M[5, 0, 0:2, 0:3] += 0.02
M[5, 0, 0:2, 4:7] -= 0.02

# Liver: fuller inferior right lobe, on image-left
M[6, 0, 3:7, 0:3] += 0.04
M[6, 0, 3:7, 4:7] -= 0.04

# Lungs: dark center rather than only dark corners
M[7:9, 2, 2:5, 2:5] += 0.08
M[7:9, 2, 0:2, 0:2] -= 0.045
M[7:9, 2, 0:2, 5:7] -= 0.045
M[7:9, 2, 5:7, 0:2] -= 0.045
M[7:9, 2, 5:7, 5:7] -= 0.045

# Lung-left: lower medial soft-tissue intrusion
M[7, 0, 3:6, 0:2] += 0.06
M[7, 0, 3:6, 5:7] -= 0.06
M[7, 2, 3:6, 0:2] -= 0.08
M[7, 2, 3:6, 5:7] += 0.08

# Lung-right: reflected medial boundary
M[8, 0, 3:6, 0:2] -= 0.06
M[8, 0, 3:6, 5:7] += 0.06
M[8, 2, 3:6, 0:2] += 0.08
M[8, 2, 3:6, 5:7] -= 0.08

# Pancreas: horizontal central tissue band
M[9, 0] -= 0.03
M[9, 0, 2:5, 1:6] += 0.098

# Spleen: vertically concentrated tissue
M[10, 0] -= 0.03
M[10, 0, 1:6, 2:5] += 0.098
M[10, 0, 2:5, 1:3] -= 0.02
M[10, 0, 2:5, 4:6] += 0.02

# Internal texture evidence excludes the outer pooled border
M[0, 5:9, 1:6, 1:6] = -0.16
M[0, 9, 1:6, 1:6] = -0.8
M[1:3, 5:9, 1:6, 1:6] = 0.14
M[1:3, 9, 1:6, 1:6] = 0.35
M[3, 5:9, 1:6, 1:6] = -0.04
M[3, 9, 1:6, 1:6] = -0.12
M[4:6, 5:9, 1:6, 1:6] = 0.08
M[4:6, 9, 1:6, 1:6] = 0.45
M[6, 5:9, 1:6, 1:6] = -0.1
M[6, 9, 1:6, 1:6] = -0.35
M[7:9, 5:9, 1:6, 1:6] = 0.04
M[7:9, 9, 1:6, 1:6] = 0.08
M[9, 5:9, 1:6, 1:6] = 0.16
M[9, 9, 1:6, 1:6] = 0.65
M[10, 5:9, 1:6, 1:6] = -0.08
M[10, 9, 1:6, 1:6] = -0.35

# Bladder: enclosing bright-inside boundary
M[0, 5, 2:5, 1] += 0.5
M[0, 6, 2:5, 5] += 0.5
M[0, 7, 1, 2:5] += 0.4
M[0, 8, 5, 2:5] += 0.4

# Femurs: longitudinal cortical boundaries
M[1:3, 5, 2:6, 1:3] += 0.25
M[1:3, 6, 2:6, 4:6] += 0.25
M[1:3, 7, 1, 1:6] += 0.15

# Heart: broad convex boundary
M[3, 5, 2:5, 1] += 0.4
M[3, 6, 2:5, 5] += 0.4
M[3, 7, 1, 2:5] += 0.3
M[3, 8, 5, 2:5] += 0.3

# Kidneys: curved cortical sides and tapered ends
M[4:6, 5, 1:6, 1] += 0.3
M[4:6, 6, 1:6, 5] += 0.3
M[4:6, 7, 1, 2:5] += 0.2
M[4:6, 8, 5, 2:5] += 0.2

# Lungs: dark-inside boundary polarity
M[7:9, 6, 1:6, 1] += 0.15
M[7:9, 5, 1:6, 5] += 0.15
M[7:9, 8, 1, 2:5] += 0.15
M[7:9, 7, 5, 2:5] += 0.15

# Pancreas: horizontal upper and lower interfaces
M[9, 7, 1:3, 1:6] += 0.25
M[9, 8, 4:6, 1:6] += 0.25

# Spleen: smoother elongated outline
M[10, 5, 1:6, 1] += 0.35
M[10, 6, 1:6, 5] += 0.35
M[10, 7, 1, 2:5] += 0.2
M[10, 8, 5, 2:5] += 0.2
```