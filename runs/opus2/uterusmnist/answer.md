## Design

**Assumed anatomy.** These are sagittal slices shown in the usual radiological convention: anterior on the left, superior at the top, cervix near the bottom of the crop.
- **Anteflexion:** the uterine body and cavity run from the cervix up and to the left (anterior). The cavity line, the endometrial stripe and the uterine walls are then mostly oriented like "\".
- **Retroflexion:** the body bends up and to the right (posterior). These structures are then mostly oriented like "/".

**Filters (all 3×3 with zero sum, so flat regions give no response):**
- **Filters 0 and 1:** edges running along the "\" diagonal, one filter per polarity. After ReLU, together they measure edge strength along "\" regardless of which side is brighter.
- **Filters 2 and 3:** the same for edges along the "/" diagonal.
- **Filter 4:** bright thin line along "\" (for example the endometrial stripe).
- **Filter 5:** bright thin line along "/".
- **Filter 6:** dark thin line along "\" (for example the junctional zone or the canal).
- **Filter 7:** dark thin line along "/".
- **Biases:** a small negative bias of −0.1 suppresses noise.

**Readout:**
- **Orientation cue (main signal).** The "/" filters (2, 3, 5, 7) vote for retroflexion with positive weights. The "\" filters (0, 1, 4, 6) vote for anteflexion with the mirrored negative weights.
  - The upper grid rows 0–3, where the uterine body and fundus sit, get weight ±0.4.
  - The lower rows 4–6, where the cervix sits, get weight ±0.2.
- **Symmetry.** All weights are left-right symmetric, so a mirrored image gives exactly the negated logit. This also cancels artifacts from zero padding at the borders and corners, so the natural threshold is 0 and B = 0.
- **Weak position cue.** Edge energy (filters 0–3) in the upper-right cells (rows 0–3, columns 4–6) adds evidence for retroflexion. Edge energy in the upper-left cells (columns 0–2) adds evidence for anteflexion. The idea is that the body's structure sits on the side it is bent toward.

```edits
CW[0, 0] = [[0, 1, 1], [-1, 0, 1], [-1, -1, 0]]
CW[1, 0] = [[0, -1, -1], [1, 0, -1], [1, 1, 0]]
CW[2, 0] = [[1, 1, 0], [1, 0, -1], [0, -1, -1]]
CW[3, 0] = [[-1, -1, 0], [-1, 0, 1], [0, 1, 1]]
CW[4, 0] = [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]]
CW[5, 0] = [[-0.5, -0.5, 1], [-0.5, 1, -0.5], [1, -0.5, -0.5]]
CW[6, 0] = [[-1, 0.5, 0.5], [0.5, -1, 0.5], [0.5, 0.5, -1]]
CW[7, 0] = [[0.5, 0.5, -1], [0.5, -1, 0.5], [-1, 0.5, 0.5]]
CB[0:8] = -0.1
# "\" orientation -> anteflexion (negative)
M[0, 0, 0:4, :] = -0.4
M[0, 1, 0:4, :] = -0.4
M[0, 4, 0:4, :] = -0.4
M[0, 6, 0:4, :] = -0.4
M[0, 0, 4:7, :] = -0.2
M[0, 1, 4:7, :] = -0.2
M[0, 4, 4:7, :] = -0.2
M[0, 6, 4:7, :] = -0.2
# "/" orientation -> retroflexion (positive)
M[0, 2, 0:4, :] = 0.4
M[0, 3, 0:4, :] = 0.4
M[0, 5, 0:4, :] = 0.4
M[0, 7, 0:4, :] = 0.4
M[0, 2, 4:7, :] = 0.2
M[0, 3, 4:7, :] = 0.2
M[0, 5, 4:7, :] = 0.2
M[0, 7, 4:7, :] = 0.2
# weak position cue: structure upper-right (posterior) -> retro, upper-left (anterior) -> ante
M[0, 0:4, 0:4, 4:7] += 0.1
M[0, 0:4, 0:4, 0:3] -= 0.1
B[:] = 0
```