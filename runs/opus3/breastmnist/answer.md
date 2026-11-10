## Design

**Clinical cues used.** On a 28×28 breast ultrasound, malignant lesions tend to be large, dark (hypoechoic) masses in the centre of the image. They often have irregular, vertically oriented margins and a dark posterior acoustic shadow underneath. Normal tissue and benign lesions look different:
- Normal images are mostly bright, horizontally layered fibroglandular tissue.
- Benign masses are usually smaller and oval.
- Cysts are pitch-black and are often followed by a bright band below them (posterior enhancement).

**Filters** (most use a 3×3 smoothing so they ignore speckle):

| # | Filter | What it detects |
|---|--------|-----------------|
| k0 | Dark: ReLU(−mean − 0.6) | Hypoechoic regions (pixels below about 50/255) |
| k1 | Bright: ReLU(mean − 0.2) | Echogenic tissue (pixels above about 150/255) |
| k2, k3 | Sobel vertical gradient, ± signs, bias −0.15 | Horizontal edges (tissue layers, smooth oval margins) |
| k4, k5 | Sobel horizontal gradient, ± signs, bias −0.15 | Vertical edges (irregular or taller-than-wide margins, shadow borders) |
| k6 | Anechoic: ReLU(−mean − 0.88) | Pitch-black cyst interiors |
| k7 | Positive Laplacian, bias −0.3 | Isolated bright specks (microcalcification-like) |

**Readout** (one logit, positive = normal/benign):
- **k0, darkness:**
  - Strong negative weight in the central grid (−1.2 in the inner 3×3, −0.8 in the ring around it).
  - Extra negative weight (−0.9) on the lower-centre rows, to catch posterior shadowing.
  - Small positive weight on the remaining border cells, so that globally dark images are partly normalised.
- **k1, brightness:** positive weight in the centre (normal tissue, no mass). Larger positive weight in the lower centre, to catch posterior enhancement.
- **Edges:** horizontal-edge energy (k2, k3) gets +0.3 and vertical-edge energy (k4, k5) gets −0.3 over the central 5×5. For isotropic speckle these cancel, so the term only measures orientation.
- **k6, anechoic:** positive weight in the centre (cyst means benign). This partly cancels the darkness penalty on those pixels.
- **k7, bright specks:** small negative weight in the centre.
- **Bias B = 2.0:** reflects the roughly 73% prior for class 1 and offsets the typically negative darkness term, so the 0.5 threshold sits closer to the malignant cluster.

```edits
# k0: dark (hypoechoic), smoothed
CW[0, 0] = [[-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111]]
CB[0] = -0.6
# k1: bright tissue, smoothed
CW[1, 0] = [[0.111, 0.111, 0.111], [0.111, 0.111, 0.111], [0.111, 0.111, 0.111]]
CB[1] = -0.2
# k2/k3: horizontal edges (vertical gradient), both polarities
CW[2, 0] = [[-0.25, -0.5, -0.25], [0, 0, 0], [0.25, 0.5, 0.25]]
CB[2] = -0.15
CW[3, 0] = [[0.25, 0.5, 0.25], [0, 0, 0], [-0.25, -0.5, -0.25]]
CB[3] = -0.15
# k4/k5: vertical edges (horizontal gradient), both polarities
CW[4, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CB[4] = -0.15
CW[5, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[5] = -0.15
# k6: anechoic (cyst-black)
CW[6, 0] = [[-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111], [-0.111, -0.111, -0.111]]
CB[6] = -0.88
# k7: bright isolated specks
CW[7, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[7] = -0.3

# readout: darkness
M[0, 0, :, :] = 0.2
M[0, 0, 1:6, 1:6] = -0.8
M[0, 0, 2:5, 2:5] = -1.2
M[0, 0, 5:7, 2:5] = -0.9
# brightness in centre / posterior enhancement
M[0, 1, 1:6, 1:6] = 0.6
M[0, 1, 4:7, 2:5] = 0.8
# edge orientation: horizontal good, vertical bad
M[0, 2, 1:6, 1:6] = 0.3
M[0, 3, 1:6, 1:6] = 0.3
M[0, 4, 1:6, 1:6] = -0.3
M[0, 5, 1:6, 1:6] = -0.3
# anechoic cyst -> benign
M[0, 6, 1:6, 1:6] = 1.5
# bright specks in centre -> malignant
M[0, 7, 2:5, 2:5] = -0.1
B[0] = 2.0
```