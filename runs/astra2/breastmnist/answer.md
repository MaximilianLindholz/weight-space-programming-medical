This is an **unvalidated morphology heuristic**; its performance cannot be established without images or evaluation.

- **Filter 0:** smoothed grayscale intensity. The readout compares lower-central tissue with same-depth flanks: posterior brightness favors normal/benign; central shadowing favors malignant.
- **Filters 1–2:** moderately dark and very dark smoothed regions. Filter 1 favors horizontally extended central darkness over vertically extended darkness. Filter 2 gives a smaller benign contribution for a very dark central core.
- **Filters 3–6:** paired horizontal and vertical Sobel derivatives. Together they measure unsigned edge strength: horizontal boundaries favor normal/benign, while vertical boundaries favor malignant.
- **Filters 7–8:** thresholded positive and negative high-pass responses, providing a weak penalty for strong fine-scale variation.
- **Filter 9:** bright horizontal ridges, weakly favoring preserved horizontal tissue structure.

The outer pooled border is ignored to reduce frame artifacts. A positive bias favors the more prevalent normal/benign label when these cues are weak.

```edits
# Smoothed grayscale, approximately in [0, 1].
CW[0, 0] = [[0.03125, 0.0625, 0.03125], [0.0625, 0.125, 0.0625], [0.03125, 0.0625, 0.03125]]
CB[0] = 0.5

# Smoothed darkness below grayscale 0.35.
CW[1, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CB[1] = -0.3

# Smoothed darkness below grayscale 0.15.
CW[2, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CB[2] = -0.7

# Opposite polarities of horizontal intensity change.
CW[3, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CB[3] = -0.03
CW[4, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]
CB[4] = -0.03

# Opposite polarities of vertical intensity change.
CW[5, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CB[5] = -0.03
CW[6, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]
CB[6] = -0.03

# Thresholded positive and negative local high-pass responses.
CW[7, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, 0.75, -0.125], [-0.0625, -0.125, -0.0625]]
CB[7] = -0.12
CW[8, 0] = [[0.0625, 0.125, 0.0625], [0.125, -0.75, 0.125], [0.0625, 0.125, 0.0625]]
CB[8] = -0.12

# Bright horizontal ridge, smoothed along its length.
CW[9, 0] = [[-0.125, -0.25, -0.125], [0.25, 0.5, 0.25], [-0.125, -0.25, -0.125]]
CB[9] = -0.08

# Posterior enhancement versus shadowing; each row sums to zero.
M[0, 0, 4] = [0, -0.45, 0.3, 0.3, 0.3, -0.45, 0]
M[0, 0, 5] = [0, -0.9, 0.6, 0.6, 0.6, -0.9, 0]

# Dark-region extent and coarse horizontal-versus-vertical shape.
M[0, 1] = [
[0, 0, 0, 0, 0, 0, 0],
[0, 0.15, -0.65, -0.85, -0.65, 0.15, 0],
[0, 0.25, -0.2, -0.35, -0.2, 0.25, 0],
[0, 0.5, 0.25, 0, 0.25, 0.5, 0],
[0, 0.25, -0.2, -0.35, -0.2, 0.25, 0],
[0, 0.15, -0.65, -0.85, -0.65, 0.15, 0],
[0, 0, 0, 0, 0, 0, 0]
]

# Modest reward for a very dark central core.
M[0, 2, 2:5, 1:6] = 0.15
M[0, 2, 2:5, 2:5] = 0.3
M[0, 2, 3, 2:5] = 0.5

# Vertical boundaries: negative evidence, strongest centrally.
M[0, 3:5, 1:6, 1:6] = -0.5
M[0, 3:5, 2:5, 1:6] = -0.85
M[0, 3:5, 2:5, 2:5] = -1.1

# Horizontal boundaries: positive evidence with matching spatial weights.
M[0, 5:7, 1:6, 1:6] = 0.5
M[0, 5:7, 2:5, 1:6] = 0.85
M[0, 5:7, 2:5, 2:5] = 1.1

# Weak fine-scale variation penalty.
M[0, 7:9, 2:5, 1:6] = -0.18

# Weak reward for horizontal tissue ridges.
M[0, 9, 1:6, 1:6] = 0.12
M[0, 9, 2:5, 2:5] = 0.18

B[0] = 0.8
```