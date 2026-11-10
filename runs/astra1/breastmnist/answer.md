This is a hand-designed ultrasound heuristic, not a validated classifier; its AUC and accuracy are unknown.

- **Filters 0–1:** opposite-sign local averages. Together they provide signed brightness evidence. The spatial readout favors lateral dark-region extension and penalizes vertical extension and lower-central darkness—a crude shape/shadow cue.
- **Filters 2–5:** opposite horizontal and vertical Sobel responses. Their readout favors horizontal boundaries over vertical boundaries, weakly favoring wider-than-tall structures.
- **Filters 6–7:** opposite local high-pass responses. Central texture is compared with surrounding texture, giving a small bonus to relatively homogeneous interiors.
- **Filters 8–9:** moderate-darkness and very-dark thresholds. Their combined center-versus-surround readout penalizes moderately dark interiors but gives back evidence for very dark, potentially fluid-filled interiors.
- All image-dependent reads exclude the outermost pooled cells. The bias mildly favors class 1.

```edits
# Local mean darkness and brightness.
CW[0, 0] = [[-0.111111111, -0.111111111, -0.111111111], [-0.111111111, -0.111111111, -0.111111111], [-0.111111111, -0.111111111, -0.111111111]]
CW[1, 0] = [[0.111111111, 0.111111111, 0.111111111], [0.111111111, 0.111111111, 0.111111111], [0.111111111, 0.111111111, 0.111111111]]

# Left-right contrast, both polarities.
CW[2, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[3, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

# Top-bottom contrast, both polarities.
CW[4, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[5, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

# Deviation from the eight neighboring pixels, both polarities.
CW[6, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CW[7, 0] = [[0.125, 0.125, 0.125], [0.125, -1, 0.125], [0.125, 0.125, 0.125]]

# Smoothed darkness below approximately grey levels 102 and 51.
CW[8, 0] = [[-0.111111111, -0.111111111, -0.111111111], [-0.111111111, -0.111111111, -0.111111111], [-0.111111111, -0.111111111, -0.111111111]]
CB[8] = -0.2
CW[9, 0] = [[-0.111111111, -0.111111111, -0.111111111], [-0.111111111, -0.111111111, -0.111111111], [-0.111111111, -0.111111111, -0.111111111]]
CB[9] = -0.6

# Signed intensity template: lateral extent versus axial extent and shadow.
M[0, 0] = [
[0, 0, 0, 0, 0, 0, 0],
[0, 0.1, -0.2, -0.4, -0.2, 0.1, 0],
[0, 0.25, -0.1, -0.2, -0.1, 0.25, 0],
[0, 0.35, 0.25, -0.2, 0.25, 0.35, 0],
[0, 0.4, -0.2, -0.3, -0.2, 0.4, 0],
[0, 0.4, -0.4, -0.6, -0.4, 0.4, 0],
[0, 0, 0, 0, 0, 0, 0]
]
M[0, 1] = [
[0, 0, 0, 0, 0, 0, 0],
[0, -0.1, 0.2, 0.4, 0.2, -0.1, 0],
[0, -0.25, 0.1, 0.2, 0.1, -0.25, 0],
[0, -0.35, -0.25, 0.2, -0.25, -0.35, 0],
[0, -0.4, 0.2, 0.3, 0.2, -0.4, 0],
[0, -0.4, 0.4, 0.6, 0.4, -0.4, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Absolute directional contrast.
M[0, 2:4, 1:6, 1:6] = -0.8
M[0, 4:6, 1:6, 1:6] = 0.65

# Central roughness relative to the surrounding sixteen-cell ring.
M[0, 6:8, 1:6, 1:6] = 0.16875
M[0, 6:8, 2:5, 2:5] = -0.3

# Moderate central darkness relative to surrounding tissue.
M[0, 8, 1:6, 1:6] = 0.140625
M[0, 8, 2:5, 2:5] = -0.25

# Very dark central interiors partially reverse the moderate-darkness penalty.
M[0, 9, 1:6, 1:6] = -0.365625
M[0, 9, 2:5, 2:5] = 0.65

B[0] = 0.9
```