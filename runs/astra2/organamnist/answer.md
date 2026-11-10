This is an **unvalidated anatomical heuristic**, not a substitute for learned weights. Its weak left/right cues assume conventional radiological axial orientation, which I cannot verify for these arrays.

**Filters.** Filter 0 measures very low attenuation; filters 1–4 are intensity hinges whose linear combinations form water-like, soft-tissue, and enhanced-tissue responses. Filter 5 detects nearly saturated white pixels, favoring bone. Filters 6–9 detect rightward, leftward, downward, and upward intensity transitions; their sums measure local edge activity.

**Output evidence.**
- **Bladder:** smooth, water-like center, with a more tissue-like surrounding region.
- **Femurs:** concentrated central/ring-like bone, allowing darker marrow; weak mirrored surrounding-tissue cues distinguish sides.
- **Heart:** a broad enhanced center with low-attenuation surroundings.
- **Kidneys:** enhanced central cortex with a darker, medially displaced hilum; weak medial peripheral bone/context evidence.
- **Liver:** broad, relatively homogeneous soft tissue, favoring upper/left coverage over lower-right coverage.
- **Lungs:** extensive central low attenuation, with mirrored medial soft-tissue notches.
- **Pancreas:** a narrow, slightly diagonal tissue band, allowing texture and weak posterior bone context.
- **Spleen:** a smooth, solid, diagonally elongated tissue region rather than a hollow center.

Readout weights are normalized by 25 after construction. Boundary gradient cells are discarded to reduce padding artifacts.

```edits
# Intensity filters
CW[0, 0, 1, 1] = -2
CW[1, 0, 1, 1] = 2.5
CW[2, 0, 1, 1] = 2.5
CW[3, 0, 1, 1] = 2.5
CW[4, 0, 1, 1] = 2.5
CW[5, 0, 1, 1] = 10

# Directional edge filters
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[:] = [-1, 1.5, 0.5, -0.5, -1.5, -9, -0.04, -0.04, -0.04, -0.04]

# Bladder: surrounding region
M[0, 0] = 0.15
M[0, 1] = 0.2
M[0, 2] = 0.05
M[0, 3] = -0.9
M[0, 4] = 0.65
M[0, 5] = -1.5
M[0, 6:10] = -0.15

# Bladder: water-like central body
M[0, 0, 1:6, 1:6] = -1.5
M[0, 1, 1:6, 1:6] = 3
M[0, 2, 1:6, 1:6] = -5.45
M[0, 3, 1:6, 1:6] = 0.7
M[0, 4, 1:6, 1:6] = 1.75
M[0, 5, 1:6, 1:6] = -2
M[0, 6:10, 1:6, 1:6] = -0.8

# Bladder: especially smooth fluid core
M[0, 0, 2:5, 2:5] = -1.8
M[0, 1, 2:5, 2:5] = 3.4
M[0, 2, 2:5, 2:5] = -6.45
M[0, 3, 2:5, 2:5] = 1.2
M[0, 4, 2:5, 2:5] = 1.85
M[0, 6:10, 2:5, 2:5] = -1.2

# Femurs: shared surrounding region
M[1:3, 0] = 0.2
M[1:3, 1] = 0.05
M[1:3, 2] = -0.05
M[1:3, 3] = 0.1
M[1:3, 4] = -0.1
M[1:3, 5] = 0.7
M[1:3, 6:10] = 0.15

# Femurs: cortical and trabecular bone
M[1:3, 0, 1:6, 1:6] = -0.3
M[1:3, 1, 1:6, 1:6] = 0.15
M[1:3, 2, 1:6, 1:6] = -0.15
M[1:3, 3, 1:6, 1:6] = 0.55
M[1:3, 4, 1:6, 1:6] = -0.55
M[1:3, 5, 1:6, 1:6] = 6.5
M[1:3, 6:10, 1:6, 1:6] = 0.5

# Femurs: allow marrow within the bone
M[1:3, 0, 2:5, 2:5] = 0
M[1:3, 1, 2:5, 2:5] = 0.35
M[1:3, 2, 2:5, 2:5] = -0.4
M[1:3, 3, 2:5, 2:5] = 0.05
M[1:3, 4, 2:5, 2:5] = 0
M[1:3, 5, 2:5, 2:5] = 4.5
M[1:3, 6:10, 2:5, 2:5] = 0.3

# Femurs: weak mirrored lateral-fat and medial-tissue cues
M[1, 0, 1:6, 0:2] -= 0.2
M[1, 0, 1:6, 5:7] += 0.2
M[2, 0, 1:6, 0:2] += 0.2
M[2, 0, 1:6, 5:7] -= 0.2
M[1, 2, 1:6, 0:2] += 0.12
M[1, 3, 1:6, 0:2] -= 0.12
M[1, 2, 1:6, 5:7] -= 0.12
M[1, 3, 1:6, 5:7] += 0.12
M[2, 2, 1:6, 0:2] -= 0.12
M[2, 3, 1:6, 0:2] += 0.12
M[2, 2, 1:6, 5:7] += 0.12
M[2, 3, 1:6, 5:7] -= 0.12
M[1, 5, 1:4, 1:3] += 0.2
M[1, 5, 1:4, 4:6] -= 0.2
M[2, 5, 1:4, 1:3] -= 0.2
M[2, 5, 1:4, 4:6] += 0.2

# Heart: low-attenuation surroundings
M[3, 0] = 0.55
M[3, 2] = -0.15
M[3, 3] = 0.15
M[3, 5] = -1.5
M[3, 6:10] = -0.05

# Heart: broad soft/enhanced central body
M[3, 0, 1:6, 1:6] = -1.6
M[3, 1, 1:6, 1:6] = 0.2
M[3, 2, 1:6, 1:6] = 1.2
M[3, 3, 1:6, 1:6] = -0.5
M[3, 4, 1:6, 1:6] = -0.9
M[3, 5, 1:6, 1:6] = -2
M[3, 6:10, 1:6, 1:6] = -0.15

# Heart: filled central chambers
M[3, 0, 2:5, 2:5] = -2.2
M[3, 1, 2:5, 2:5] = 0.1
M[3, 2, 2:5, 2:5] = 1.6
M[3, 3, 2:5, 2:5] = -0.5
M[3, 4, 2:5, 2:5] = -1.2
M[3, 5, 2:5, 2:5] = -2.5
M[3, 6:10, 2:5, 2:5] = -0.2

# Kidneys: shared surrounding region
M[4:6, 0] = 0.5
M[4:6, 1] = 0.05
M[4:6, 2] = -0.25
M[4:6, 3] = 0.25
M[4:6, 4] = -0.05
M[4:6, 5] = -1

# Kidneys: enhanced cortex and parenchyma
M[4:6, 0, 1:6, 1:6] = -1.1
M[4:6, 1, 1:6, 1:6] = 0.15
M[4:6, 2, 1:6, 1:6] = 1
M[4:6, 3, 1:6, 1:6] = 0.15
M[4:6, 4, 1:6, 1:6] = -1.3
M[4:6, 5, 1:6, 1:6] = -2.5
M[4:6, 6:10, 1:6, 1:6] = -0.1

# Kidneys: narrow oval rather than rectangular coverage
M[4:6, 0, 1:6, 1:6:4] += 0.4
M[4:6, 2, 1:6, 1:6:4] -= 0.2
M[4:6, 3, 1:6, 1:6:4] += 0.2

# Kidneys: shared central renal sinus
M[4:6, 0, 2:5, 3] = 1
M[4:6, 1, 2:5, 3] = 0.65
M[4:6, 2, 2:5, 3] = -0.75
M[4:6, 3, 2:5, 3] = 0.35
M[4:6, 4, 2:5, 3] = -0.25
M[4:6, 6:10, 2:5, 3] = 0.25

# Left kidney: medial extension of the hilum
M[4, 0, 3:5, 2] = 1
M[4, 1, 3:5, 2] = 0.65
M[4, 2, 3:5, 2] = -0.75
M[4, 3, 3:5, 2] = 0.35
M[4, 4, 3:5, 2] = -0.25
M[4, 6:10, 3:5, 2] = 0.25

# Right kidney: mirrored hilum
M[5, 0, 3:5, 4] = 1
M[5, 1, 3:5, 4] = 0.65
M[5, 2, 3:5, 4] = -0.75
M[5, 3, 3:5, 4] = 0.35
M[5, 4, 3:5, 4] = -0.25
M[5, 6:10, 3:5, 4] = 0.25

# Kidneys: weak medial vertebral and surrounding-tissue context
M[4, 0, 2:6, 0] -= 0.25
M[4, 2, 2:6, 0] += 0.25
M[4, 3, 2:6, 0] -= 0.25
M[4, 5, 3:6, 0] = 0.5
M[5, 0, 2:6, 6] -= 0.25
M[5, 2, 2:6, 6] += 0.25
M[5, 3, 2:6, 6] -= 0.25
M[5, 5, 3:6, 6] = 0.5

# Liver: broad soft-tissue coverage
M[6, 0] = -0.4
M[6, 1] = 0.25
M[6, 2] = 0.6
M[6, 3] = -1.3
M[6, 4] = 0.45
M[6, 5] = -1.2
M[6, 6:10] = -0.2

# Liver: homogeneous central parenchyma
M[6, 0, 1:6, 1:6] = -1.4
M[6, 1, 1:6, 1:6] = 0.45
M[6, 2, 1:6, 1:6] = 1.6
M[6, 3, 1:6, 1:6] = -3.4
M[6, 4, 1:6, 1:6] = 1.35
M[6, 5, 1:6, 1:6] = -2
M[6, 6:10, 1:6, 1:6] = -0.5

# Liver: broad upper-left body and lower-right taper
M[6, 0, 0:5, 0:4] -= 0.2
M[6, 2, 0:5, 0:4] += 0.3
M[6, 3, 0:5, 0:4] -= 0.4
M[6, 4, 0:5, 0:4] += 0.1
M[6, 6:10, 0:5, 0:4] -= 0.05
M[6, 0, 4:7, 4:7] += 0.6
M[6, 2, 4:7, 4:7] -= 0.3
M[6, 3, 4:7, 4:7] += 0.4
M[6, 4, 4:7, 4:7] -= 0.1

# Lungs: surrounding pleural and soft-tissue region
M[7:9, 0] = 0.45
M[7:9, 1] = 0.1
M[7:9, 3] = -0.2
M[7:9, 4] = 0.1
M[7:9, 5] = -1.5
M[7:9, 6:10] = 0.1

# Lungs: central low attenuation
M[7:9, 0, 1:6, 1:6] = 3
M[7:9, 1, 1:6, 1:6] = -0.4
M[7:9, 2, 1:6, 1:6] = -0.1
M[7:9, 3, 1:6, 1:6] = 0.6
M[7:9, 4, 1:6, 1:6] = -0.1
M[7:9, 5, 1:6, 1:6] = -2.5
M[7:9, 6:10, 1:6, 1:6] = 0.05

# Lungs: dark central parenchyma
M[7:9, 0, 2:5, 2:5] = 3.5
M[7:9, 1, 2:5, 2:5] = -0.45
M[7:9, 2, 2:5, 2:5] = -0.1
M[7:9, 3, 2:5, 2:5] = 0.65
M[7:9, 4, 2:5, 2:5] = -0.1
M[7:9, 5, 2:5, 2:5] = -3
M[7:9, 6:10, 2:5, 2:5] = 0

# Left lung: medial cardiac/hilar notch
M[7, 0, 1:4, 1:3] = 0.5
M[7, 1, 1:4, 1:3] = 0.25
M[7, 2, 1:4, 1:3] = 0.5
M[7, 3, 1:4, 1:3] = -0.55
M[7, 4, 1:4, 1:3] = -0.2
M[7, 5, 1:4, 1:3] = -2

# Right lung: mirrored medial notch
M[8, 0, 1:4, 4:6] = 0.5
M[8, 1, 1:4, 4:6] = 0.25
M[8, 2, 1:4, 4:6] = 0.5
M[8, 3, 1:4, 4:6] = -0.55
M[8, 4, 1:4, 4:6] = -0.2
M[8, 5, 1:4, 4:6] = -2

# Lungs: weak medial surrounding tissue
M[7, 2, 2:6, 0] += 0.4
M[7, 3, 2:6, 0] -= 0.4
M[8, 2, 2:6, 6] += 0.4
M[8, 3, 2:6, 6] -= 0.4

# Pancreas: low-attenuation surrounding region
M[9, 0] = 0.55
M[9, 1] = -0.1
M[9, 2] = -0.1
M[9, 3] = 0.25
M[9, 4] = -0.05
M[9, 5] = -0.8
M[9, 6:10] = 0.1

# Pancreas: transverse central tissue band
M[9, 0, 2:5, 1:6] = -1.1
M[9, 1, 2:5, 1:6] = 0.6
M[9, 2, 2:5, 1:6] = 1.5
M[9, 3, 2:5, 1:6] = -2.9
M[9, 4, 2:5, 1:6] = 0.8
M[9, 5, 2:5, 1:6] = -2
M[9, 6:10, 2:5, 1:6] = 0.35

# Pancreas: diagonal extensions
M[9, 0, 1, 4:6] = -0.7
M[9, 1, 1, 4:6] = 0.4
M[9, 2, 1, 4:6] = 1.2
M[9, 3, 1, 4:6] = -2
M[9, 4, 1, 4:6] = 0.4
M[9, 5, 1, 4:6] = -1.5
M[9, 6:10, 1, 4:6] = 0.25
M[9, 0, 5, 1:3] = -0.7
M[9, 1, 5, 1:3] = 0.4
M[9, 2, 5, 1:3] = 1.2
M[9, 3, 5, 1:3] = -2
M[9, 4, 5, 1:3] = 0.4
M[9, 5, 5, 1:3] = -1.5
M[9, 6:10, 5, 1:3] = 0.25

# Pancreas: weak posterior vertebral context
M[9, 5, 5:7, 2:5] = 0.3

# Spleen: surrounding low attenuation
M[10, 0] = 0.5
M[10, 2] = -0.1
M[10, 3] = 0.1
M[10, 5] = -1.3
M[10, 6:10] = -0.05

# Spleen: solid soft/enhanced central body
M[10, 0, 1:6, 1:6] = -1.3
M[10, 1, 1:6, 1:6] = 0.2
M[10, 2, 1:6, 1:6] = 1.6
M[10, 3, 1:6, 1:6] = -1.8
M[10, 4, 1:6, 1:6] = 0
M[10, 5, 1:6, 1:6] = -2.5
M[10, 6:10, 1:6, 1:6] = -0.35

# Spleen: smooth filled core
M[10, 0, 2:5, 2:5] = -1.8
M[10, 1, 2:5, 2:5] = 0.2
M[10, 2, 2:5, 2:5] = 2
M[10, 3, 2:5, 2:5] = -2.2
M[10, 4, 2:5, 2:5] = 0
M[10, 5, 2:5, 2:5] = -3
M[10, 6:10, 2:5, 2:5] = -0.5

# Spleen: remove opposing corners to form an oblique oval
M[10, 0, 1:3, 1:3] = 0.4
M[10, 1, 1:3, 1:3] = 0
M[10, 2, 1:3, 1:3] = 0.15
M[10, 3, 1:3, 1:3] = -0.15
M[10, 4, 1:3, 1:3] = 0
M[10, 5, 1:3, 1:3] = -2
M[10, 6:10, 1:3, 1:3] = 0.1
M[10, 0, 4:6, 4:6] = 0.4
M[10, 1, 4:6, 4:6] = 0
M[10, 2, 4:6, 4:6] = 0.15
M[10, 3, 4:6, 4:6] = -0.15
M[10, 4, 4:6, 4:6] = 0
M[10, 5, 4:6, 4:6] = -2
M[10, 6:10, 4:6, 4:6] = 0.1

# Discard gradient evidence in boundary pooling cells
M[:, 6:10, 0:7:6, :] = 0
M[:, 6:10, :, 0:7:6] = 0

# Normalize spatial accumulation and set decision offsets
M[:] *= 0.04
B[:] = [-0.55, -0.35, -0.35, -0.85, -0.85, -0.85, -0.65, -0.25, -0.25, -0.65, -0.35]
```