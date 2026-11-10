**Design.** I assume superior is up, anterior is image-left, and the cavity is relatively bright. These conventions are not established by the prompt; the weights below are an unvalidated geometric heuristic.

- Filters **0–1** measure overall intensity and brighter structures.
- Filters **2–5** detect bright vertical, horizontal, `\`, and `/` ridges.
- Filters **6–9** are positive/negative diagonal-derivative pairs, providing boundary-orientation evidence regardless of contrast polarity.
- The output combines superior-versus-inferior intensity displacement, a three-region ridge-position stencil approximating curvature, and superior-versus-inferior diagonal orientation. Superior-right displacement and superior `/` orientation favor **retroflexion**; their leftward counterparts favor **anteflexion**. The curvature stencil suppresses uniform displacement and straight tilt when ridge strength is uniform.
- Border pooling cells are unused. The bias is zero, and horizontal reflection reverses the logit.

```edits
# Intensity channels.
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[1] = -0.1

# Bright vertical and horizontal ridges.
CW[2, 0] = [[-0.125, 0.25, -0.125], [-0.25, 0.5, -0.25], [-0.125, 0.25, -0.125]]
CW[3, 0] = [[-0.125, -0.25, -0.125], [0.25, 0.5, 0.25], [-0.125, -0.25, -0.125]]

# Bright backslash and slash ridges, respectively.
CW[4, 0] = [[0, 0, -0.5], [0, 1, 0], [-0.5, 0, 0]]
CW[5, 0] = [[-0.5, 0, 0], [0, 1, 0], [0, 0, -0.5]]
CB[2:6] = -0.04

# Opposite-polarity derivatives normal to backslash structures.
CW[6, 0] = [[0, 0.25, 0.25], [-0.25, 0, 0.25], [-0.25, -0.25, 0]]
CW[7, 0] = [[0, -0.25, -0.25], [0.25, 0, -0.25], [0.25, 0.25, 0]]

# Opposite-polarity derivatives normal to slash structures.
CW[8, 0] = [[-0.25, -0.25, 0], [-0.25, 0, 0.25], [0, 0.25, 0.25]]
CW[9, 0] = [[0.25, 0.25, 0], [0.25, 0, -0.25], [0, -0.25, -0.25]]
CB[6:10] = -0.03

# Weak broad-intensity evidence: superior-right versus inferior-right.
M[0, 0] = [
[0, 0, 0, 0, 0, 0, 0],
[0, -0.06, -0.03, 0, 0.03, 0.06, 0],
[0, -0.1, -0.05, 0, 0.05, 0.1, 0],
[0, -0.02, -0.01, 0, 0.01, 0.02, 0],
[0, 0.08, 0.04, 0, -0.04, -0.08, 0],
[0, 0.1, 0.05, 0, -0.05, -0.1, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Stronger displacement evidence from bright structures.
M[0, 1] = [
[0, 0, 0, 0, 0, 0, 0],
[0, -0.48, -0.24, 0, 0.24, 0.48, 0],
[0, -0.8, -0.4, 0, 0.4, 0.8, 0],
[0, -0.16, -0.08, 0, 0.08, 0.16, 0],
[0, 0.64, 0.32, 0, -0.32, -0.64, 0],
[0, 0.8, 0.4, 0, -0.4, -0.8, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Ridge-position curvature evidence.
# Superior rows: positive rightward moment.
M[0, 2:6, 1:3, 1] = -0.25
M[0, 2:6, 1:3, 2] = -0.125
M[0, 2:6, 1:3, 4] = 0.125
M[0, 2:6, 1:3, 5] = 0.25

# Middle rows: subtract the junction-region rightward moment.
M[0, 2:6, 3, 1] = 0.75
M[0, 2:6, 3, 2] = 0.375
M[0, 2:6, 3, 4] = -0.375
M[0, 2:6, 3, 5] = -0.75
M[0, 2:6, 4, 1] = 0.25
M[0, 2:6, 4, 2] = 0.125
M[0, 2:6, 4, 4] = -0.125
M[0, 2:6, 4, 5] = -0.25

# Inferior row: cervical-position reference.
M[0, 2:6, 5, 1] = -0.5
M[0, 2:6, 5, 2] = -0.25
M[0, 2:6, 5, 4] = 0.25
M[0, 2:6, 5, 5] = 0.5
M[0, 3] *= 0.5
M[0, 4:6] *= 0.75

# Bright diagonal orientation: backslash superiorly favors anteflexion.
M[0, 4, 1, 1:6] -= 0.6
M[0, 4, 2, 1:6] -= 0.8
M[0, 4, 3, 1:6] -= 0.2
M[0, 4, 4, 1:6] += 0.6
M[0, 4, 5, 1:6] += 1

# Slash superiorly favors retroflexion; inferior evidence is reversed.
M[0, 5, 1, 1:6] += 0.6
M[0, 5, 2, 1:6] += 0.8
M[0, 5, 3, 1:6] += 0.2
M[0, 5, 4, 1:6] -= 0.6
M[0, 5, 5, 1:6] -= 1

# Polarity-independent backslash boundary evidence.
M[0, 6:8, 1, 1:6] = -0.18
M[0, 6:8, 2, 1:6] = -0.24
M[0, 6:8, 3, 1:6] = -0.06
M[0, 6:8, 4, 1:6] = 0.18
M[0, 6:8, 5, 1:6] = 0.3

# Polarity-independent slash boundary evidence.
M[0, 8:10, 1, 1:6] = 0.18
M[0, 8:10, 2, 1:6] = 0.24
M[0, 8:10, 3, 1:6] = 0.06
M[0, 8:10, 4, 1:6] = -0.18
M[0, 8:10, 5, 1:6] = -0.3

B[0] = 0
```