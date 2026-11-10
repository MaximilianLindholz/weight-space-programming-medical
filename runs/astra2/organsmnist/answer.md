I use an **unvalidated, handcrafted intensity-and-shape model**:

- **Filters 0 and 5:** very dark pixels and broader low-density pixels. Their combination separates air-like darkness from fat-like gray.
- **Filters 1–4:** intensity hinges at −0.6, −0.2, 0.2, and 0.6. Linear combinations provide fluid-like, soft-tissue, enhanced-tissue, and bone evidence.
- **Filters 6–9:** opposite horizontal and vertical Sobel responses, with a small noise threshold. Their sum measures local texture.

The outputs compare the central **5×5 pooled cells**, the surrounding **24 cells**, and whole-image intensity statistics. Bladder favors smooth central fluid; femurs favor bone; heart favors central tissue with peripheral air; kidneys favor enhancement, fat, and texture; liver favors broad smooth tissue; lungs favor central darkness; pancreas favors mixed tissue/fat and texture; spleen favors a relatively uniform bright center with fatty surroundings.

Kidney and lung laterality receive weak contextual adjustments, without assuming horizontal mirroring. Femur logits are deliberately identical: I have no defensible hand-specified sagittal laterality cue. No performance claim is possible without evaluation.

```edits
# Intensity hinges
CW[0, 0, 1, 1] = -1
CW[1:5, 0, 1, 1] = 1
CW[5, 0, 1, 1] = -1

# Opposite horizontal and vertical derivatives
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[:] = [-0.8, 0.6, 0.2, -0.2, -0.6, -0.4, -0.025, -0.025, -0.025, -0.025]

B[:] = [-0.8, -1.1, -1.1, -1, -1.2, -1.4, -0.8, -0.45, -0.95, -1, -0.7]

# 0: bladder
M[0, 0] = -0.09
M[0, 1] = 0.05
M[0, 2] = -0.1
M[0, 3] = 0.05
M[0, 4] = -0.1
M[0, 5] = 0.03
M[0, 0, 1:6, 1:6] -= 0.21
M[0, 1, 1:6, 1:6] += 0.4
M[0, 2, 1:6, 1:6] -= 0.95
M[0, 3, 1:6, 1:6] += 0.55
M[0, 5, 1:6, 1:6] -= 0.03
M[0, 6:10, 1:6, 1:6] = -0.24

# 1 and 2: femurs, shared evidence
M[1:3, 3] = 0.075
M[1:3, 4] = 0.425
M[1:3, 0, 1:6, 1:6] = -0.4
M[1:3, 1, 1:6, 1:6] = -0.07
M[1:3, 2, 1:6, 1:6] = 0.14
M[1:3, 3, 1:6, 1:6] -= 0.07
M[1:3, 6:10, 1:6, 1:6] = 0.12

# 3: heart
M[3, 0] = 0.4
M[3, 1] = 0.04
M[3, 2] = -0.04
M[3, 4] = -0.1
M[3, 0, 1:6, 1:6] -= 0.35
M[3, 1, 1:6, 1:6] -= 0.04
M[3, 2, 1:6, 1:6] += 0.31
M[3, 3, 1:6, 1:6] = -0.27
M[3, 5, 1:6, 1:6] = -0.15
M[3, 6:10, 1:6, 1:6] = -0.08

# 4: kidney-left
M[4, 0] = -0.39
M[4, 1] = -0.12
M[4, 2] = 0.12
M[4, 4] = -0.1
M[4, 5] = 0.13
M[4, 0, 1:6, 1:6] -= 0.12
M[4, 1, 1:6, 1:6] += 0.12
M[4, 2, 1:6, 1:6] += 0.16
M[4, 3, 1:6, 1:6] = -0.13
M[4, 4, 1:6, 1:6] -= 0.15
M[4, 5, 1:6, 1:6] -= 0.06
M[4, 6:10, 1:6, 1:6] = 0.12

# 5: kidney-right
M[5, 0] = -0.27
M[5, 1] = -0.02
M[5, 2] = 0.02
M[5, 4] = -0.1
M[5, 5] = 0.09
M[5, 0, 1:6, 1:6] -= 0.24
M[5, 1, 1:6, 1:6] += 0.02
M[5, 2, 1:6, 1:6] += 0.26
M[5, 3, 1:6, 1:6] = -0.13
M[5, 4, 1:6, 1:6] -= 0.15
M[5, 5, 1:6, 1:6] -= 0.02
M[5, 6:10, 1:6, 1:6] = 0.12

# 6: liver
M[6, 1] = 0.15
M[6, 2] = -0.15
M[6, 4] = -0.1
M[6, 0, 1:6, 1:6] = -0.06
M[6, 1, 1:6, 1:6] -= 0.12
M[6, 2, 1:6, 1:6] += 0.4
M[6, 3, 1:6, 1:6] = -0.62
M[6, 4, 1:6, 1:6] += 0.34
M[6, 5, 1:6, 1:6] = -0.1
M[6, 6:10, 1:6, 1:6] = -0.12

# 7 and 8: shared lung evidence
M[7:9, 0] = 0.12
M[7:9, 4] = -0.075
M[7:9, 3, 1:6, 1:6] = 0.15
M[7:9, 6:10, 1:6, 1:6] = 0.02

# 7: lung-left
M[7, 1] = -0.075
M[7, 2] = 0.075
M[7, 0, 1:6, 1:6] += 0.81
M[7, 1, 1:6, 1:6] += 0.12
M[7, 2, 1:6, 1:6] -= 0.27

# 8: lung-right
M[8, 1] = -0.025
M[8, 2] = 0.025
M[8, 0, 1:6, 1:6] += 0.99
M[8, 1, 1:6, 1:6] -= 0.02
M[8, 2, 1:6, 1:6] -= 0.13

# 9: pancreas
M[9, 0] = -0.19
M[9, 1] = -0.05
M[9, 2] = 0.05
M[9, 4] = -0.1
M[9, 5] = 0.11
M[9, 0, 1:6, 1:6] -= 0.77
M[9, 1, 1:6, 1:6] += 0.23
M[9, 2, 1:6, 1:6] -= 0.23
M[9, 3, 1:6, 1:6] = -0.15
M[9, 4, 1:6, 1:6] += 0.15
M[9, 5, 1:6, 1:6] += 0.09
M[9, 6:10, 1:6, 1:6] = 0.14

# 10: spleen
M[10, 0] = -0.42
M[10, 1] = -0.1
M[10, 2] = 0.1
M[10, 4] = -0.1
M[10, 5] = 0.14
M[10, 0, 1:6, 1:6] += 0.72
M[10, 1, 1:6, 1:6] += 0.1
M[10, 2, 1:6, 1:6] += 0.23
M[10, 3, 1:6, 1:6] = -0.3
M[10, 4, 1:6, 1:6] -= 0.03
M[10, 5, 1:6, 1:6] -= 0.34
M[10, 6:10, 1:6, 1:6] = -0.16
```