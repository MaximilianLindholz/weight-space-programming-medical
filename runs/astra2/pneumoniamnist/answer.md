I would prioritize **lung opacity relative to the mediastinum**, with weaker evidence from aeration and edge contrast. This is an unvalidated heuristic; the thresholds and bias are hand-chosen, not calibrated.

- **Filters 0–1:** positive and negative parts of a Gaussian-smoothed image, allowing the output to recover signed local brightness.
- **Filters 2–3:** clipped darkness below −0.15, measuring aerated lung without letting nearly black regions dominate.
- **Filters 4–5:** clipped brightness above −0.05, providing additional evidence for opacification.
- **Filters 6–9:** paired horizontal and vertical Sobel responses. Their absolute magnitudes provide weak normal-class evidence from preserved structural contrast.
- **Spatial readout:** emphasizes bilateral lung regions in pooled rows 1–5, columns 1–2 and 4–5. It downweights the lower image-right region to reduce cardiac contamination. Midline cells in rows 2–5 provide a brightness reference. Outer borders receive no weight.

```edits
# Smoothed brightness and its negative.
CW[0, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]
CW[1, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]

# Two hinges whose difference measures clipped darkness.
CW[2, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CW[3, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]

# Two hinges whose difference measures clipped brightness.
CW[4, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]
CW[5, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]

# Paired horizontal derivatives.
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

# Paired vertical derivatives.
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

CB[:] = [0, 0, -0.15, -0.75, 0.05, -0.55, 0, 0, 0, 0]

# Initialize every channel with the same lung mask, summing to 1.
M[0, :, 1, 1:6:4] = 0.03
M[0, :, 1, 2:5:2] = 0.04
M[0, :, 2, 1:6:4] = 0.055
M[0, :, 2, 2:5:2] = 0.075
M[0, :, 3, 1:6:4] = 0.065
M[0, :, 3, 2] = 0.085
M[0, :, 3, 4] = 0.07
M[0, :, 4, 1] = 0.065
M[0, :, 4, 2] = 0.075
M[0, :, 4, 4] = 0.025
M[0, :, 4, 5] = 0.06
M[0, :, 5, 1:3] = 0.025
M[0, :, 5, 4] = 0.01
M[0, :, 5, 5] = 0.03

# Signed mean lung brightness.
M[0, 0] *= 6
M[0, 1] *= -6

# Aerated darkness is normal-class evidence.
M[0, 2] *= -1.5
M[0, 3] *= 1.5

# Clipped brightness is pneumonia-class evidence.
M[0, 5] *= -1

# Structural contrast is weaker normal-class evidence.
M[0, 6:8] *= -0.75
M[0, 8:10] *= -1

# Midline reference: normalized weights 0.25, 0.30, 0.25, 0.20.
# Subtract its signed brightness from lung brightness.
M[0, 0, 2:6, 3] = [-1.5, -1.8, -1.5, -1.2]
M[0, 1, 2:6, 3] = [1.5, 1.8, 1.5, 1.2]

# Partial exposure compensation for clipped darkness.
M[0, 2, 2:6, 3] = [0.1875, 0.225, 0.1875, 0.15]
M[0, 3, 2:6, 3] = [-0.1875, -0.225, -0.1875, -0.15]

# Partial exposure compensation for clipped brightness.
M[0, 4, 2:6, 3] = [-0.125, -0.15, -0.125, -0.1]
M[0, 5, 2:6, 3] = [0.125, 0.15, 0.125, 0.1]

B[0] = 2.9
```