This is an unvalidated anatomical heuristic. I assume **anterior is image-left and the fundus is above the cervix**; the description does not establish these conventions, and reversing left/right would reverse the intended label polarity.

- **Filters 0–1:** bright-signal and broader foreground maps.
- **Filters 2–3:** local bright and dark contrast, emphasizing narrow structures.
- **Filters 4–5:** bright `\` and `/` ridge responses.
- **Filters 6–9:** paired diagonal gradients; adding opposite-polarity responses measures edge orientation independently of contrast polarity.

The readout combines weak upper-versus-lower lateral displacement, an interior bend-position template, and stronger upper-versus-inferior orientation evidence. Upper `/` evidence relative to the inferior canal favors retroflexion; upper `\` evidence favors anteflexion. Border cells are excluded from the contrast/orientation evidence. The zero output bias imposes no class-prevalence preference.

```edits
# Bright signal and foreground
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CW[1, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = -0.1
CB[1] = 0.5

# Bright and dark local contrast
CW[2, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CW[3, 0] = [[0.125, 0.125, 0.125], [0.125, -1, 0.125], [0.125, 0.125, 0.125]]

# Bright backslash and slash ridges
CW[4, 0] = [[0.5, -0.25, -0.25], [-0.25, 0.5, -0.25], [-0.25, -0.25, 0.5]]
CW[5, 0] = [[-0.25, -0.25, 0.5], [-0.25, 0.5, -0.25], [0.5, -0.25, -0.25]]
CB[2:6] = -0.04

# Opposite-polarity gradients normal to slash-oriented edges
CW[6, 0] = [[-0.25, -0.25, 0], [-0.25, 0, 0.25], [0, 0.25, 0.25]]
CW[7, 0] = [[0.25, 0.25, 0], [0.25, 0, -0.25], [0, -0.25, -0.25]]

# Opposite-polarity gradients normal to backslash-oriented edges
CW[8, 0] = [[0, -0.25, -0.25], [0.25, 0, -0.25], [0.25, 0.25, 0]]
CW[9, 0] = [[0, 0.25, 0.25], [-0.25, 0, 0.25], [-0.25, -0.25, 0]]
CB[6:10] = -0.03

# Weak lateral displacement: upper right versus inferior right
M[0, 0:2, 1:6, 0] = -0.15
M[0, 0:2, 1:6, 1] = -0.1
M[0, 0:2, 1:6, 2] = -0.05
M[0, 0:2, 1:6, 4] = 0.05
M[0, 0:2, 1:6, 5] = 0.1
M[0, 0:2, 1:6, 6] = 0.15
M[0, 0:2, 3] *= 0.5
M[0, 0:2, 4] *= -1
M[0, 0:2, 5] *= -1.5
M[0, 1] *= 0.3

# Interior bend-position template on local contrast
M[0, 2:4, 1:6, 1] = -0.2
M[0, 2:4, 1:6, 2] = -0.1
M[0, 2:4, 1:6, 4] = 0.1
M[0, 2:4, 1:6, 5] = 0.2
M[0, 2:4, 1:3] *= 0.5
M[0, 2:4, 3] *= -1.5
M[0, 2:4, 4] *= -0.5
M[0, 3] *= 0.5

# Shared spatial envelope for orientation evidence
M[0, 4:10, 1:6, 1:6] = 0.4
M[0, 4:10, 1:6, 2:5] = 0.8
M[0, 4:10, 1:6, 3] = 1
M[0, 4:10, 1] *= 0.5
M[0, 4:10, 3] *= 0.5
M[0, 4:10, 4:6] *= -1

# Slash minus backslash, upper region minus inferior region
M[0, 4] *= -1
M[0, 6:10] *= 0.6
M[0, 8:10] *= -1

B[0] = 0
```