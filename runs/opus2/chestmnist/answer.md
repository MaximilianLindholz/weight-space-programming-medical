# Hand-set CNN for ChestMNIST: design and weights

## Design

**Constraint behind the design.** Every label has a test prevalence well below 50%; the most common, infiltration, is about 18–20%. The mean ACC at threshold 0.5 is therefore best served by keeping every logit negative, which gives about 0.94–0.95. So each bias is set near logit(prevalence) minus a safety margin. The feature terms are kept moderate, so they reorder images for AUC without pushing logits past 0.

**Assumed anatomy on the 7×7 grid** (each cell is 4×4 pixels):
- Lungs: rows 1–4, columns 1–2 (patient's right) and columns 4–5 (patient's left).
- Mediastinum and spine: column 3.
- Heart: rows 4–5, extending to column 4 (and column 2 on the other side).
- Costophrenic angles and diaphragm: row 5, columns 1 and 5.

**Filters:**
- **F0, brightness:** ReLU(x + 1), which is exactly linear (x + 1), so it acts as a pure intensity map.
- **F1, darkness:** ReLU(−x − 0.3). Fires on air-dark lung.
- **F3, bright blob/line:** a Laplacian (center 1, each of the 8 neighbours −1/8, bias −0.05). Fires on nodules and masses, and on tubes, wires and ECG leads. These lines are an ICU/portable-film signal that correlates with effusion, atelectasis, edema and pneumothorax (chest tubes).
- **F4–F7, edge energy:** rectified ±Sobel-x and ±Sobel-y, scaled by 1/4. Together they measure lung texture.
- **F2, F8, F9:** unused.

**What each output reads.** Brightness is always taken as a difference against a reference region, so overall exposure largely cancels.

| Label | Evidence read |
|---|---|
| Atelectasis, consolidation | Lower-lung brightness minus mediastinum brightness, plus lines (F3) |
| Cardiomegaly | Brightness in the lateral heart-border cells (4,2), (4,4), (4,5), (5,2), (5,4) minus upper-lung brightness |
| Effusion | Lower-lateral (costophrenic) brightness, minus darkness in the same cells, minus upper-lung brightness, plus lines |
| Infiltration, pneumonia | Whole-lung brightness minus mediastinum brightness; pneumonia also reads lines |
| Mass, nodule | Blob detector (F3) over the lung fields; mass also reads lung opacity |
| Pneumothorax | Darkness at the upper lateral lung, plus lateral lines (chest tubes) |
| Edema | Scaled infiltration term plus scaled cardiomegaly term, plus lines |
| Emphysema | Lung darkness, extra weight for darkness at the low row (hyperinflation), plus a narrow heart relative to the mediastinum |
| Fibrosis | Lung edge/texture energy (F4–F7) |
| Pleural thickening | Brightness of the lateral lung rim minus the inner lung |
| Hernia | Weak cardiomegaly-like term, with a very negative bias |

```edits
# ---- filters ----
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
CW[1, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[1] = -0.3
CW[3, 0] = [[-0.125, -0.125, -0.125], [-0.125, 1, -0.125], [-0.125, -0.125, -0.125]]
CB[3] = -0.05
CW[4, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CB[4] = -0.03
CW[5, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[5] = -0.03
CW[6, 0] = [[-0.25, -0.5, -0.25], [0, 0, 0], [0.25, 0.5, 0.25]]
CB[6] = -0.03
CW[7, 0] = [[0.25, 0.5, 0.25], [0, 0, 0], [-0.25, -0.5, -0.25]]
CB[7] = -0.03

# ---- 0 atelectasis ----
M[0, 0, 3:5, 1:3] = 0.25
M[0, 0, 3:5, 5] = 0.25
M[0, 0, 1:5, 3] = -0.375
M[0, 3, 1:4, 1:6] = 0.6
B[0] = -1.9

# ---- 1 cardiomegaly ----
M[1, 0, 4, 2] = 0.5
M[1, 0, 4, 4] = 0.5
M[1, 0, 4, 5] = 0.5
M[1, 0, 5, 2] = 0.5
M[1, 0, 5, 4] = 0.5
M[1, 0, 1:3, 1:3] = -0.3125
M[1, 0, 1:3, 4:6] = -0.3125
B[1] = -4.8

# ---- 2 effusion ----
M[2, 0, 4:6, 1] = 0.5
M[2, 0, 4:6, 5] = 0.5
M[2, 1, 4:6, 1] = -0.5
M[2, 1, 4:6, 5] = -0.5
M[2, 0, 1:3, 1:3] = -0.25
M[2, 0, 1:3, 4:6] = -0.25
M[2, 3, 1:4, 1:6] = 0.6
B[2] = -3.2

# ---- 3 infiltration ----
M[3, 0, 1:5, 1:3] = 0.2
M[3, 0, 1:5, 5] = 0.2
M[3, 0, 1:5, 3] = -0.6
B[3] = -1.1

# ---- 4 mass ----
M[4, 3, 1:5, 1:3] = 1.0
M[4, 3, 1:5, 4:6] = 1.0
M[4, 0, 1:5, 1:3] = 0.1
M[4, 0, 1:5, 5] = 0.1
M[4, 0, 1:5, 3] = -0.3
B[4] = -3.15

# ---- 5 nodule ----
M[5, 3, 1:5, 1:3] = 1.0
M[5, 3, 1:5, 4:6] = 1.0
B[5] = -3.6

# ---- 6 pneumonia ----
M[6, 0, 1:5, 1:3] = 0.2
M[6, 0, 1:5, 5] = 0.2
M[6, 0, 1:5, 3] = -0.6
M[6, 3, 1:4, 1:6] = 0.4
B[6] = -3.7

# ---- 7 pneumothorax ----
M[7, 1, 1:3, 1] = 0.5
M[7, 1, 1:3, 5] = 0.5
M[7, 3, 2:5, 1] = 1.0
M[7, 3, 2:5, 5] = 1.0
B[7] = -3.8

# ---- 8 consolidation ----
M[8, 0, 3:5, 1:3] = 0.25
M[8, 0, 3:5, 5] = 0.25
M[8, 0, 1:5, 3] = -0.375
M[8, 3, 1:4, 1:6] = 0.6
B[8] = -3.0

# ---- 9 edema ----
M[9, 0, 1:5, 1:3] = 0.12
M[9, 0, 1:5, 5] = 0.12
M[9, 0, 1:5, 3] = -0.36
M[9, 0, 1:3, 1:3] -= 0.15625
M[9, 0, 1:3, 4:6] -= 0.15625
M[9, 0, 4, 2] += 0.25
M[9, 0, 4, 4] = 0.25
M[9, 0, 4, 5] += 0.25
M[9, 0, 5, 2] = 0.25
M[9, 0, 5, 4] = 0.25
M[9, 3, 1:4, 1:6] = 0.4
B[9] = -4.0

# ---- 10 emphysema ----
M[10, 1, 1:6, 1:3] = 0.3
M[10, 1, 1:6, 5] = 0.3
M[10, 1, 1:3, 4] = 0.3
M[10, 1, 5, 1:3] += 0.5
M[10, 1, 5, 5] += 0.5
M[10, 0, 4, 2] = -0.3
M[10, 0, 4, 4] = -0.3
M[10, 0, 4, 5] = -0.3
M[10, 0, 5, 2] = -0.3
M[10, 0, 5, 4] = -0.3
M[10, 0, 1:5, 3] = 0.375
B[10] = -5.5

# ---- 11 fibrosis ----
M[11, 4:8, 1:5, 1:3] = 0.3
M[11, 4:8, 1:5, 5] = 0.3
B[11] = -5.2

# ---- 12 pleural thickening ----
M[12, 0, 1:4, 1] = 0.3
M[12, 0, 1:4, 5] = 0.3
M[12, 0, 1:4, 2] = -0.3
M[12, 0, 1:3, 4] = -0.45
B[12] = -4.1

# ---- 13 hernia ----
M[13, 0, 4, 2] = 0.25
M[13, 0, 4, 4] = 0.25
M[13, 0, 4, 5] = 0.25
M[13, 0, 5, 2] = 0.25
M[13, 0, 5, 4] = 0.25
M[13, 0, 1:3, 1:3] = -0.15625
M[13, 0, 1:3, 4:6] = -0.15625
B[13] = -6.8
```