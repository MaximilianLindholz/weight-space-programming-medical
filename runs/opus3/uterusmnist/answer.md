## Design

**Assumed geometry.** I assume the standard radiological sagittal display: anterior (bladder) on the left, posterior (rectum/sacrum) on the right, superior at the top.

- **Anteflexion:** the uterine body runs from the cervix (lower right) up and forward to the fundus (upper left). The dominant structure is oriented like "\", or lies horizontally on the left over the bladder.
- **Retroflexion:** the body bends backward, so the upper part of the uterus runs like "/" toward the upper right, and the bulk sits on the right.

I don't know whether the uterus is brighter or darker than its surroundings. So every detector comes in both polarities, and the network measures orientation energy rather than intensity. If the arrays store anterior on the right instead, all signs flip; I cannot check this.

**Filters** (all kernels sum to zero, so flat regions give 0; small negative biases suppress noise):

| Filter | Detects |
|---|---|
| 0, 1 | Edges oriented "\" (both polarities) |
| 2, 3 | Edges oriented "/" (both polarities) |
| 4, 6 | Bright and dark thin lines oriented "\" (e.g. the endometrial stripe or the junctional zone) |
| 5, 7 | Bright and dark thin lines oriented "/" |
| 8, 9 | Horizontal edges (both polarities) |

**Output** (o = log-odds of retroflexion):

- **Diagonal filters.** "\" energy pushes the logit negative (anteflexion) and "/" energy pushes it positive (retroflexion). The grid rows 1–3 carry double weight, because the upper part, where the body and fundus lie, is most informative. Grid rows 4–5 carry half weight. The outer border ring of cells is ignored, to avoid artifacts from the zero padding.
- **Horizontal filters.** Horizontal-edge energy on the left (columns 1–2) means a body lying over the bladder, so it counts as anteflexion. On the right (columns 4–5) it means a body bent backward, so it counts as retroflexion.
- **Bias.** B = 0, since the classes are treated symmetrically.

```edits
# oriented edge detectors (both polarities)
CW[0, 0] = [[0, 1, 1], [-1, 0, 1], [-1, -1, 0]]
CW[1, 0] = [[0, -1, -1], [1, 0, -1], [1, 1, 0]]
CW[2, 0] = [[1, 1, 0], [1, 0, -1], [0, -1, -1]]
CW[3, 0] = [[-1, -1, 0], [-1, 0, 1], [0, 1, 1]]
# oriented line detectors: 4 bright "\", 5 bright "/", 6 dark "\", 7 dark "/"
CW[4, 0] = [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]]
CW[5, 0] = [[-1, -1, 2], [-1, 2, -1], [2, -1, -1]]
CW[6, 0] = [[-2, 1, 1], [1, -2, 1], [1, 1, -2]]
CW[7, 0] = [[1, 1, -2], [1, -2, 1], [-2, 1, 1]]
# horizontal edges
CW[8, 0] = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
CW[9, 0] = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
CB[0:4] = -0.3
CB[4:8] = -0.5
CB[8:10] = -0.3
# "\" evidence -> anteflexion (negative logit)
M[0, 0:2, 1:4, 1:6] = -0.3
M[0, 0:2, 4:6, 1:6] = -0.15
# "/" evidence -> retroflexion (positive logit)
M[0, 2:4, 1:4, 1:6] = 0.3
M[0, 2:4, 4:6, 1:6] = 0.15
# line evidence
M[0, 4, 1:4, 1:6] = -0.25
M[0, 4, 4:6, 1:6] = -0.12
M[0, 6, 1:4, 1:6] = -0.25
M[0, 6, 4:6, 1:6] = -0.12
M[0, 5, 1:4, 1:6] = 0.25
M[0, 5, 4:6, 1:6] = 0.12
M[0, 7, 1:4, 1:6] = 0.25
M[0, 7, 4:6, 1:6] = 0.12
# horizontal structures: left (anterior) -> anteflexion, right (posterior) -> retroflexion
M[0, 8:10, 1:6, 1:3] = -0.15
M[0, 8:10, 1:6, 4:6] = 0.15
B[:] = 0
```