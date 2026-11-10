This is an **unvalidated anatomical heuristic**. I assume superior is up, the cavity is generally above the cervix, and anterior is image-left. The supplied description does not establish these conventions; reversing anterior/posterior would reverse the intended labels.

- **Filter 0:** thresholded tissue brightness. **Filter 1:** locally bright ridges.
- **Filters 2–5:** opposite-polarity diagonal gradients. Paired ReLUs measure contrast-insensitive edge energy for `/` versus `\` structures.
- **Filters 6–9:** opposite-polarity diagonal curvature, emphasizing bright or dark narrow structures with those orientations.
- **Readout:** compares `/` minus `\` energy in upper pooled rows against the same evidence in lower cervical rows. Weaker positional evidence favors rightward upper-body displacement relative to the lower region. Border cells are downweighted. Zero bias avoids imposing an unsupported class-frequency prior.

```edits
# Tissue brightness and local bright contrast.
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 0.5
CW[1, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[1] = -0.02

# Opposite gradients normal to / structures.
CW[2, 0] = [[-0.25, -0.125, 0], [-0.125, 0, 0.125], [0, 0.125, 0.25]]
CW[3, 0] = [[0.25, 0.125, 0], [0.125, 0, -0.125], [0, -0.125, -0.25]]

# Opposite gradients normal to \ structures.
CW[4, 0] = [[0, -0.125, -0.25], [0.125, 0, -0.125], [0.25, 0.125, 0]]
CW[5, 0] = [[0, 0.125, 0.25], [-0.125, 0, 0.125], [-0.25, -0.125, 0]]
CB[2:6] = -0.015

# Bright and dark curvature responses for / structures.
CW[6, 0] = [[-0.5, 0, 0], [0, 1, 0], [0, 0, -0.5]]
CW[7, 0] = [[0.5, 0, 0], [0, -1, 0], [0, 0, 0.5]]

# Bright and dark curvature responses for \ structures.
CW[8, 0] = [[0, 0, -0.5], [0, 1, 0], [-0.5, 0, 0]]
CW[9, 0] = [[0, 0, 0.5], [0, -1, 0], [0.5, 0, 0]]
CB[6:10] = -0.03

# Horizontal positional masks for tissue and bright-ridge evidence.
M[0, 0:2, :, 0] = -0.15
M[0, 0:2, :, 1:3] = -0.5
M[0, 0:2, :, 3] = 0
M[0, 0:2, :, 4:6] = 0.5
M[0, 0:2, :, 6] = 0.15

# Upper-body position relative to the lower cervical region.
M[0, 0:2, 0, :] *= 0.05
M[0, 0:2, 1, :] *= 0.15
M[0, 0:2, 2, :] *= 0.2
M[0, 0:2, 3, :] *= 0.1
M[0, 0:2, 4, :] *= -0.15
M[0, 0:2, 5, :] *= -0.2
M[0, 0:2, 6, :] *= -0.15
M[0, 1] *= 4

# Shared superior-versus-inferior orientation comparison.
M[0, 2:10, 0, :] = 0.1
M[0, 2:10, 1, :] = 0.35
M[0, 2:10, 2, :] = 0.6
M[0, 2:10, 3, :] = 0.35
M[0, 2:10, 4, :] = -0.4
M[0, 2:10, 5, :] = -0.65
M[0, 2:10, 6, :] = -0.35

# Prefer central anatomy over lateral boundaries.
M[0, 2:10, :, 0] *= 0.15
M[0, 2:10, :, 1] *= 0.5
M[0, 2:10, :, 5] *= 0.5
M[0, 2:10, :, 6] *= 0.15

# Subtract backslash energy from slash energy.
M[0, 4:6] *= -1
M[0, 8:10] *= -1

# Slightly favor narrow-structure curvature over broad edge evidence.
M[0, 2:6] *= 0.75

B[0] = 0
```