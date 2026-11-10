This is a hand-designed heuristic; its test performance is unknown.

- **Filters 0–1:** smoothed brightness and thresholded darkness (approximately below grey level 70).
- **Filters 2–5:** paired horizontal and vertical Sobel derivatives. Their paired responses measure edge strength regardless of polarity.
- **Filters 6–7:** positive and negative high-frequency residuals, with a small noise threshold.
- **Filters 8–9:** bright horizontal and vertical ridges, respectively.

**Output 0** ignores the outermost pooled cells. Its brightness/darkness templates compare the central vertical region with lateral tissue: narrow or vertically extended darkness and lower-central shadowing lower the benign logit. Horizontal rather than vertical edge/ridge organization raises it. Central high-frequency texture relative to lateral tissue lowers it, while a smoother center raises it. The positive intercept reflects the more common normal/benign class.

```edits
# Smoothed brightness and darkness.
CW[0, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]
CW[1, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]

# Opposite-polarity horizontal derivatives: vertical-edge evidence.
CW[2, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[3, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

# Opposite-polarity vertical derivatives: horizontal-edge evidence.
CW[4, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[5, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

# Opposite-polarity residuals from local Gaussian smoothing.
CW[6, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, 0.75, -0.125], [-0.0625, -0.125, -0.0625]]
CW[7, 0] = [[0.0625, 0.125, 0.0625], [0.125, -0.75, 0.125], [0.0625, 0.125, 0.0625]]

# Horizontal and vertical bright ridges.
CW[8, 0] = [[-0.125, -0.25, -0.125], [0.25, 0.5, 0.25], [-0.125, -0.25, -0.125]]
CW[9, 0] = [[-0.125, 0.25, -0.125], [-0.25, 0.5, -0.25], [-0.125, 0.25, -0.125]]

CB[:] = [1, -0.45, -0.025, -0.025, -0.025, -0.025, -0.04, -0.04, -0.05, -0.05]

# Brightness template: each populated row sums to zero.
# Central-column darkness and lower-central shadowing lower the logit.
M[0, 0] = [
[0, 0, 0, 0, 0, 0, 0],
[0, -0.2, 0.1, 0.2, 0.1, -0.2, 0],
[0, -0.35, 0.05, 0.6, 0.05, -0.35, 0],
[0, -0.25, -0.15, 0.8, -0.15, -0.25, 0],
[0, -0.35, 0.05, 0.6, 0.05, -0.35, 0],
[0, -0.5, 0.3, 0.4, 0.3, -0.5, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Additional evidence from genuinely dark regions relative to lateral tissue.
M[0, 1] = [
[0, 0, 0, 0, 0, 0, 0],
[0, 0.12, -0.08, -0.08, -0.08, 0.12, 0],
[0, 0.18, -0.12, -0.12, -0.12, 0.18, 0],
[0, 0.12, -0.08, -0.08, -0.08, 0.12, 0],
[0, 0.18, -0.12, -0.12, -0.12, 0.18, 0],
[0, 0.24, -0.16, -0.16, -0.16, 0.24, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Prefer horizontal over vertical edge organization, especially centrally.
M[0, 2:4, 1:6, 1:6] = -0.45
M[0, 2:4, 2:5, 2:5] = -0.65
M[0, 4:6, 1:6, 1:6] = 0.45
M[0, 4:6, 2:5, 2:5] = 0.65

# Central fine texture compared with equal-depth lateral reference tissue.
M[0, 6:8, 2:5, 2:5] = -0.6
M[0, 6:8, 2:5, 1] = 0.9
M[0, 6:8, 2:5, 5] = 0.9

# Additional orientation evidence from bright ridges.
M[0, 8, 1:6, 1:6] = 0.2
M[0, 8, 2:5, 2:5] = 0.35
M[0, 9, 1:6, 1:6] = -0.2
M[0, 9, 2:5, 2:5] = -0.35

B[0] = 1
```