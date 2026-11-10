# Hand-built CNN weights for BreastMNIST (malignant vs. normal/benign)

These weights are an untested guess. They are based on how breast ultrasound lesions usually look. The bias is set so that if the cues don't help, the network falls back to the majority class.

## Design

**What the network relies on.** Lesions are dark (hypoechoic) blobs, usually near the image centre. Compared with benign lesions, malignant ones are usually:
- larger and darker,
- less well-defined, with irregular, "taller-than-wide" outlines,
- often followed by dark *acoustic shadowing* below them.

Benign cysts often show the opposite: a sharp, horizontal lower border and a *bright* zone below (posterior enhancement). Normal images show no central dark mass.

**Filters** (the input x is in [-1, 1]):

| # | Kernel | Bias | Output | Detects |
|---|---|---|---|---|
| F0 | 3×3 smoothed mean × (−2) | −1.0 | 2·ReLU(−mean − 0.5) | dark tissue (pixel value below about 64) |
| F1 | same kernel | −1.4 | 2·ReLU(−mean − 0.7) | very dark / anechoic tissue |
| F2 | 3×3 mean × 2 | −0.4 | 2·ReLU(mean − 0.2) | bright tissue |
| F3 | top row +0.5, bottom row −0.5 | −0.3 | bright-above / dark-below edge | top border of a lesion |
| F4 | negative of F3 | −0.3 | dark-above / bright-below edge | sharp bottom border of a lesion |
| F5 | left column +0.5, right column −0.5 | −0.3 | vertical edge | left border of a lesion |
| F6 | negative of F5 | −0.3 | vertical edge | right border of a lesion |
| F7 | centre 1, neighbours −0.125 | −0.2 | bright speckle | texture of normal glandular tissue |

**Readout:** o = B + Σ M·g. A positive logit means "normal/benign".

- **Lesion darkness (malignant evidence):**
  - F0 in the central 5×5 grid cells weighs −0.1, and −0.25 in the core 3×3 cells.
  - F1 adds −0.1 in the core 3×3 cells.
  - So a large dark central mass pulls the logit down by about 2.
- **Acoustic shadowing (malignant evidence):** F0 in the bottom grid rows 5–6, central columns, weighs −0.1.
- **Posterior enhancement (benign evidence):** F2 in grid rows 4–6, central columns, weighs +0.1.
- **Lesion outline:**
  - Horizontal edges (F3 at +0.1, F4 at +0.15) in the centre count as benign: an oval, wider-than-tall shape with a sharp outline.
  - Vertical edges (F5, F6 at −0.05) count as malignant: a taller-than-wide shape.
- **Normal texture (weak benign evidence):** F7 over the whole image weighs +0.02.
- **Bias:** B = 1.6. This is a little above the class prior (log(73/27) ≈ 1.0). The network predicts "malignant" only when there is strong dark-mass or shadowing evidence, which protects accuracy against the 73% majority-class baseline.

```edits
# F0: dark (smoothed)
CW[0, 0] = [[-0.222, -0.222, -0.222], [-0.222, -0.222, -0.222], [-0.222, -0.222, -0.222]]
CB[0] = -1.0
# F1: very dark (smoothed)
CW[1, 0] = [[-0.222, -0.222, -0.222], [-0.222, -0.222, -0.222], [-0.222, -0.222, -0.222]]
CB[1] = -1.4
# F2: bright (smoothed)
CW[2, 0] = [[0.222, 0.222, 0.222], [0.222, 0.222, 0.222], [0.222, 0.222, 0.222]]
CB[2] = -0.4
# F3: bright above, dark below (lesion top border)
CW[3, 0] = [[0.5, 0.5, 0.5], [0, 0, 0], [-0.5, -0.5, -0.5]]
CB[3] = -0.3
# F4: dark above, bright below (sharp lesion bottom border)
CW[4, 0] = [[-0.5, -0.5, -0.5], [0, 0, 0], [0.5, 0.5, 0.5]]
CB[4] = -0.3
# F5 / F6: vertical edges
CW[5, 0] = [[0.5, 0, -0.5], [0.5, 0, -0.5], [0.5, 0, -0.5]]
CB[5] = -0.3
CW[6, 0] = [[-0.5, 0, 0.5], [-0.5, 0, 0.5], [-0.5, 0, 0.5]]
CB[6] = -0.3
# F7: bright speckle texture
CW[7, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[7] = -0.2

# Readout
M[0, 0, 1:6, 1:6] = -0.1          # dark mass in central region -> malignant
M[0, 0, 2:5, 2:5] = -0.25         # dark mass in core -> strongly malignant
M[0, 1, 2:5, 2:5] = -0.1          # very dark core
M[0, 0, 6, 2:5] = -0.1            # posterior shadowing -> malignant
M[0, 2, 4:7, 2:5] = 0.1           # posterior enhancement -> benign
M[0, 3, 1:5, 1:6] = 0.1           # sharp top border -> circumscribed
M[0, 4, 2:6, 1:6] = 0.15          # sharp bottom border -> benign
M[0, 5, 1:5, 1:6] = -0.05         # vertical borders -> taller-than-wide
M[0, 6, 1:5, 1:6] = -0.05
M[0, 7, :, :] = 0.02              # normal tissue texture
B[:] = 1.6
```