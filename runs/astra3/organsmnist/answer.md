This is an **unvalidated, hand-designed heuristic**. It uses intensity, texture, and center-versus-periphery structure without assuming which stored axis is superior–inferior.

**Filters**
- **0:** brightness, \(x+1\).
- **1–4:** intensity hinges at −0.50, −0.15, 0.20, and 0.55. Their linear combinations form broad fluid-like and soft-tissue-like intensity bands; filter 4 also detects very bright material.
- **5:** very dark, air-like pixels.
- **6–9:** positive and negative horizontal/vertical Sobel responses, with a small noise deadband. Paired responses measure edge strength.

**Output evidence**
- **Bladder:** smooth, fluid-like central pixels; penalizes air and very bright material.
- **Femurs:** strong high-intensity and edge evidence. Both sides share the same main detector; a negligible, arbitrary signed-edge cue breaks ties rather than pretending reliable laterality is available.
- **Heart:** central soft tissue with dark peripheral surroundings.
- **Kidneys:** textured soft tissue surrounding a lower-density core. Right kidney receives a weak preference for more surrounding soft tissue; left receives the opposite.
- **Liver:** smooth soft tissue extending into the periphery.
- **Lungs:** central darkness; the left score tolerates more soft-tissue intrusion.
- **Pancreas:** mixed soft-tissue/fat intensities and internal texture.
- **Spleen:** smooth, centrally concentrated soft tissue, with less emphasis on peripheral filling than liver.

Intensity evidence emphasizes the central 5×5 pooled cells; texture emphasizes the central 3×3. The weights below implement those choices directly.

```edits
# Intensity filters.
CW[0:5, 0, 1, 1] = 1
CW[5, 0, 1, 1] = -1
CB[0:6] = [1, 0.5, 0.15, -0.2, -0.55, -0.75]

# Signed Sobel filters.
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[6:10] = -0.02

B[:] = [0.75, -0.3, -0.3, -0.7, -0.48, -0.62, -0.65, -0.05, -0.25, 0.35, -0.45]

# 0: Bladder. Fluid-like intensity, low brightness, low texture.
M[0, 0] = -0.012
M[0, 1] = 0.07
M[0, 2] = -0.13
M[0, 3] = 0.05
M[0, 4] = -0.04
M[0, 5] = -0.09
M[0, 0, 1:6, 1:6] -= 0.024
M[0, 1, 1:6, 1:6] += 0.14
M[0, 2, 1:6, 1:6] -= 0.26
M[0, 3, 1:6, 1:6] += 0.1
M[0, 4, 1:6, 1:6] -= 0.08
M[0, 5, 1:6, 1:6] -= 0.18
M[0, 6:10, 1:6, 1:6] = -0.06
M[0, 6:10, 2:5, 2:5] -= 0.15

# Extra central fluid preference.
M[0, 1, 2:5, 2:5] += 0.06
M[0, 2, 2:5, 2:5] -= 0.15
M[0, 3, 2:5, 2:5] += 0.12
M[0, 4, 2:5, 2:5] -= 0.03

# 1 and 2: Shared femur detector.
M[1:3, 1] = 0.01
M[1:3, 3] = -0.03
M[1:3, 4] = 0.22
M[1:3, 5] = -0.03
M[1:3, 1, 1:6, 1:6] += 0.02
M[1:3, 3, 1:6, 1:6] -= 0.06
M[1:3, 4, 1:6, 1:6] += 0.44
M[1:3, 5, 1:6, 1:6] -= 0.06
M[1:3, 6:10, 1:6, 1:6] = 0.05
M[1:3, 6:10, 2:5, 2:5] += 0.125

# Tiny arbitrary laterality tie-break, not a validated anatomical cue.
M[1, 6, 1:4, 1:6] += 0.004
M[1, 7, 1:4, 1:6] -= 0.004
M[2, 6, 1:4, 1:6] -= 0.004
M[2, 7, 1:4, 1:6] += 0.004

# 3: Heart. Central soft tissue.
M[3, 0] = 0.002
M[3, 1] = 0.04
M[3, 2] = 0.01
M[3, 3] = -0.14
M[3, 4] = 0.07
M[3, 5] = -0.04
M[3, 0, 1:6, 1:6] += 0.004
M[3, 1, 1:6, 1:6] += 0.08
M[3, 2, 1:6, 1:6] += 0.02
M[3, 3, 1:6, 1:6] -= 0.28
M[3, 4, 1:6, 1:6] += 0.14
M[3, 5, 1:6, 1:6] -= 0.08
M[3, 6:10, 1:6, 1:6] = -0.01
M[3, 6:10, 2:5, 2:5] -= 0.025

# Heart core tissue and peripheral air.
M[3, 1, 2:5, 2:5] += 0.06
M[3, 2, 2:5, 2:5] -= 0.06
M[3, 3, 2:5, 2:5] -= 0.06
M[3, 4, 2:5, 2:5] += 0.06
M[3, 5] += 0.24
M[3, 5, 1:6, 1:6] -= 0.24

# 4 and 5: Shared kidney intensity and texture evidence.
M[4:6, 1] = 0.04
M[4:6, 3] = -0.12
M[4:6, 4] = 0.07
M[4:6, 5] = -0.04
M[4:6, 1, 1:6, 1:6] += 0.08
M[4:6, 3, 1:6, 1:6] -= 0.24
M[4:6, 4, 1:6, 1:6] += 0.14
M[4:6, 5, 1:6, 1:6] -= 0.08
M[4:6, 6:10, 1:6, 1:6] = 0.03
M[4:6, 6:10, 2:5, 2:5] += 0.075

# Kidney soft-tissue annulus and lower-density core.
M[4:6, 1, 1:6, 1:6] += 0.04
M[4:6, 2, 1:6, 1:6] -= 0.04
M[4:6, 3, 1:6, 1:6] -= 0.04
M[4:6, 4, 1:6, 1:6] += 0.04
M[4:6, 1, 2:5, 2:5] += 0.02
M[4:6, 2, 2:5, 2:5] -= 0.14
M[4:6, 3, 2:5, 2:5] += 0.22
M[4:6, 4, 2:5, 2:5] -= 0.1

# Left kidney: weak preference for less peripheral soft tissue.
M[4, 1] -= 0.03
M[4, 2] += 0.03
M[4, 3] += 0.03
M[4, 4] -= 0.03
M[4, 1, 1:6, 1:6] += 0.03
M[4, 2, 1:6, 1:6] -= 0.03
M[4, 3, 1:6, 1:6] -= 0.03
M[4, 4, 1:6, 1:6] += 0.03

# Right kidney: weak preference for more peripheral soft tissue.
M[5, 1] += 0.03
M[5, 2] -= 0.03
M[5, 3] -= 0.03
M[5, 4] += 0.03
M[5, 1, 1:6, 1:6] -= 0.03
M[5, 2, 1:6, 1:6] += 0.03
M[5, 3, 1:6, 1:6] += 0.03
M[5, 4, 1:6, 1:6] -= 0.03

# 6: Liver. Broad, smooth soft-tissue occupancy.
M[6, 0] = 0.0015
M[6, 1] = 0.05
M[6, 2] = -0.02
M[6, 3] = -0.11
M[6, 4] = 0.02
M[6, 5] = -0.06
M[6, 0, 1:6, 1:6] += 0.003
M[6, 1, 1:6, 1:6] += 0.1
M[6, 2, 1:6, 1:6] -= 0.04
M[6, 3, 1:6, 1:6] -= 0.22
M[6, 4, 1:6, 1:6] += 0.04
M[6, 5, 1:6, 1:6] -= 0.12
M[6, 6:10, 1:6, 1:6] = -0.04
M[6, 6:10, 2:5, 2:5] -= 0.1

# Extra soft-tissue support from the outer pooled ring.
M[6, 1] += 0.06
M[6, 2] -= 0.06
M[6, 3] -= 0.06
M[6, 4] += 0.06
M[6, 1, 1:6, 1:6] -= 0.06
M[6, 2, 1:6, 1:6] += 0.06
M[6, 3, 1:6, 1:6] += 0.06
M[6, 4, 1:6, 1:6] -= 0.06

# 7: Left lung. Air, with greater tolerance of soft-tissue intrusion.
M[7, 0] = -0.0035
M[7, 1] = 0.015
M[7, 2] = -0.015
M[7, 3] = -0.015
M[7, 4] = -0.035
M[7, 5] = 0.12
M[7, 0, 1:6, 1:6] -= 0.007
M[7, 1, 1:6, 1:6] += 0.03
M[7, 2, 1:6, 1:6] -= 0.03
M[7, 3, 1:6, 1:6] -= 0.03
M[7, 4, 1:6, 1:6] -= 0.07
M[7, 5, 1:6, 1:6] += 0.24
M[7, 6:10, 1:6, 1:6] = 0.006
M[7, 6:10, 2:5, 2:5] += 0.015

# 8: Right lung. Slightly stronger preference for air-dominated crops.
M[8, 0] = -0.0035
M[8, 1] = 0.005
M[8, 2] = -0.005
M[8, 3] = -0.005
M[8, 4] = -0.045
M[8, 5] = 0.135
M[8, 0, 1:6, 1:6] -= 0.007
M[8, 1, 1:6, 1:6] += 0.01
M[8, 2, 1:6, 1:6] -= 0.01
M[8, 3, 1:6, 1:6] -= 0.01
M[8, 4, 1:6, 1:6] -= 0.09
M[8, 5, 1:6, 1:6] += 0.27
M[8, 6:10, 1:6, 1:6] = 0.004
M[8, 6:10, 2:5, 2:5] += 0.01

# 9: Pancreas. Mixed tissue/fat and internal texture.
M[9, 0] = -0.001
M[9, 1] = 0.02
M[9, 2] = -0.01
M[9, 3] = -0.04
M[9, 5] = -0.03
M[9, 0, 1:6, 1:6] -= 0.002
M[9, 1, 1:6, 1:6] += 0.04
M[9, 2, 1:6, 1:6] -= 0.02
M[9, 3, 1:6, 1:6] -= 0.08
M[9, 5, 1:6, 1:6] -= 0.06
M[9, 6:10, 1:6, 1:6] = 0.06
M[9, 6:10, 2:5, 2:5] += 0.15

# 10: Spleen. Smooth, centrally concentrated soft tissue.
M[10, 1] = 0.05
M[10, 2] = -0.02
M[10, 3] = -0.11
M[10, 4] = 0.03
M[10, 5] = -0.04
M[10, 1, 1:6, 1:6] += 0.1
M[10, 2, 1:6, 1:6] -= 0.04
M[10, 3, 1:6, 1:6] -= 0.22
M[10, 4, 1:6, 1:6] += 0.06
M[10, 5, 1:6, 1:6] -= 0.08
M[10, 6:10, 1:6, 1:6] = -0.03
M[10, 6:10, 2:5, 2:5] -= 0.075
M[10, 1, 2:5, 2:5] += 0.07
M[10, 2, 2:5, 2:5] -= 0.07
M[10, 3, 2:5, 2:5] -= 0.07
M[10, 4, 2:5, 2:5] += 0.07
```