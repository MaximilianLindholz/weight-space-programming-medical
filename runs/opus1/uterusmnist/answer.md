## Design

**Anatomical reasoning.** In a standard sagittal MRI display, anterior (bladder) is on the left and superior is at the top. The two classes differ in where the uterine body points:

- **Anteflexion:** the cervix sits low and posterior. The body bends forward over the bladder, so the fundus points to the upper left. The main axis of the organ and its boundaries run like **"\\"** (upper-left to lower-right).
- **Retroflexion:** the body bends backward toward the sacrum, so the fundus points right (up-right or down-right). The axis typically runs like **"/"**.

Signal intensities on T2 MRI, especially in synthetic images, are unpredictable. So I use orientation-selective edge energy, which works whether a boundary goes dark-to-bright or bright-to-dark.

**Filters.** Filters 4 to 9 are unused.

- **Filter 0:** an edge running along "/" with the upper-left side brighter. Kernel 0.5·[[1,1,0],[1,0,−1],[0,−1,−1]].
- **Filter 1:** the negative of filter 0, so the same "/" edge with the opposite polarity.
- **Filter 2:** an edge running along "\\" with the upper-right side brighter. Kernel 0.5·[[0,1,1],[−1,0,1],[−1,−1,0]].
- **Filter 3:** the negative of filter 2.
- **Bias:** all four filters get a small bias of −0.05 to suppress noise.

Horizontal and vertical edges excite the "/" pair and the "\\" pair equally, so they cancel in the final difference. The same is true for most zero-padding border effects.

**Output.** The logit is roughly the total "/" edge energy minus the total "\\" edge energy over the whole 7×7 grid, with weights ±0.15.

I add a small spatial term in the upper grid rows 0 to 3, where the fundus usually lies. There, edge energy on the right side (posterior) pushes toward retroflexion, and edge energy on the left side (anterior, fundus over the bladder) pushes toward anteflexion. This term ranges over ±0.06 across the columns. The output bias B is 0.

```edits
CW[0, 0] = [[0.5, 0.5, 0], [0.5, 0, -0.5], [0, -0.5, -0.5]]
CW[1, 0] = [[-0.5, -0.5, 0], [-0.5, 0, 0.5], [0, 0.5, 0.5]]
CW[2, 0] = [[0, 0.5, 0.5], [-0.5, 0, 0.5], [-0.5, -0.5, 0]]
CW[3, 0] = [[0, -0.5, -0.5], [0.5, 0, -0.5], [0.5, 0.5, 0]]
CB[0:4] = -0.05
# "/" edge energy -> retroflexion
M[0, 0] = 0.15
M[0, 1] = 0.15
# "\" edge energy -> anteflexion
M[0, 2] = -0.15
M[0, 3] = -0.15
# upper rows: add left(-)/right(+) spatial term (edge energy on posterior side -> retroflexion)
M[0, 0, 0] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 0, 1] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 0, 2] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 0, 3] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 1, 0] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 1, 1] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 1, 2] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 1, 3] = [0.09, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21]
M[0, 2, 0] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 2, 1] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 2, 2] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 2, 3] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 3, 0] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 3, 1] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 3, 2] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
M[0, 3, 3] = [-0.21, -0.19, -0.17, -0.15, -0.13, -0.11, -0.09]
B[0] = 0
```