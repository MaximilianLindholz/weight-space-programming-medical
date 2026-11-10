I would use **lung opacity relative to central chest brightness** as the main signal, rather than absolute brightness alone.

- **Filters 0–5:** Gaussian-smoothed intensity and intensity hinges. Filters 0/1 preserve signed brightness; 2/3 detect darkness below −0.25/−0.75; 4/5 detect brightness above 0.15/0.65. Their combined readout clips extreme black and white values while emphasizing dark-to-gray changes.
- **Filters 6/7:** Opposite horizontal Sobel gradients. **Filters 8/9:** Opposite vertical Sobel gradients. Paired readouts measure gradient magnitude, providing a weak normal-favoring correction for sharp detail.
- **Output:** Compares bilateral lung regions with the central mediastinal column. It emphasizes middle lung fields, includes the bases, and downweights the expected cardiac region on image-right. Increased relative lung brightness raises the pneumonia logit. Image borders are ignored.

These are unvalidated heuristic weights; neither performance nor probability calibration can be established without data.

```edits
# Gaussian-smoothed intensity channels.
CW[0, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]
CW[1, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CW[2, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CW[3, 0] = [[-0.0625, -0.125, -0.0625], [-0.125, -0.25, -0.125], [-0.0625, -0.125, -0.0625]]
CW[4, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]
CW[5, 0] = [[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]]

# Opposite horizontal gradients.
CW[6, 0] = [[-0.125, 0, 0.125], [-0.25, 0, 0.25], [-0.125, 0, 0.125]]
CW[7, 0] = [[0.125, 0, -0.125], [0.25, 0, -0.25], [0.125, 0, -0.125]]

# Opposite vertical gradients.
CW[8, 0] = [[-0.125, -0.25, -0.125], [0, 0, 0], [0.125, 0.25, 0.125]]
CW[9, 0] = [[0.125, 0.25, 0.125], [0, 0, 0], [-0.125, -0.25, -0.125]]

CB[:] = [0, 0, -0.25, -0.75, -0.15, -0.65, 0, 0, 0, 0]

# Shared spatial contrast map for intensity channels.
# Positive lung weights sum to 1; negative reference weights sum to -1.

# Upper lung fields and upper central reference.
M[0, 0:6, 1, 1:6:4] = 0.02
M[0, 0:6, 1, 2:5:2] = 0.04
M[0, 0:6, 1, 3] = -0.10

# Upper-middle lung fields.
M[0, 0:6, 2, 1:6:4] = 0.05
M[0, 0:6, 2, 2:5:2] = 0.08
M[0, 0:6, 2, 3] = -0.20

# Middle and lower-middle fields; reduced image-right medial weighting.
M[0, 0:6, 3:5, 1] = 0.06
M[0, 0:6, 3:5, 5] = 0.08
M[0, 0:6, 3:5, 3] = -0.30
M[0, 0:6, 3, 2] = 0.09
M[0, 0:6, 3, 4] = 0.05
M[0, 0:6, 4, 2] = 0.08
M[0, 0:6, 4, 4] = 0.02

# Basal fields and lower central reference.
M[0, 0:6, 5, 1] = 0.03
M[0, 0:6, 5, 2] = 0.02
M[0, 0:6, 5, 3] = -0.10
M[0, 0:6, 5, 4] = 0.01
M[0, 0:6, 5, 5] = 0.04

# Combine hinges into a monotone, clipped brightness transform.
M[0, 0] *= 6
M[0, 1] *= -6
M[0, 2] *= -3
M[0, 3] *= 9
M[0, 4] *= -3
M[0, 5] *= -3

# Weak unsigned horizontal-gradient evidence in lateral lung fields.
M[0, 6:8, 2:5, 1:6:4] = -0.10

# Weak unsigned vertical-gradient evidence, avoiding the central heart.
M[0, 8:10, 2:4, 1:3] = -0.12
M[0, 8:10, 2:4, 4:6] = -0.12
M[0, 8:10, 4, 1:3] = -0.08
M[0, 8:10, 4, 5] = -0.08

B[0] = 2.90
```