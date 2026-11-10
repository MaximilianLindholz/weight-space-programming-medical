## Design

**Idea.** In pediatric chest X-rays, healthy lungs are dark, air-filled fields beside a bright mediastinum (spine and heart). Pneumonia adds opacities, which make the lung fields brighter and hazier. So the network measures lung brightness relative to the mediastinum, plus how much truly dark lung remains. The relative measure partly cancels out differences in exposure between images.

**Filters (only 2 of the 10 are used; the rest stay 0):**
- **Filter 0, brightness:** centre tap +1, bias +1, so h = x + 1. This is never negative, so the ReLU does nothing and the pooled value is exactly the cell's mean brightness + 1. The readout can therefore use it linearly with either sign.
- **Filter 1, dark air:** centre tap −1, bias −0.4, so h = ReLU(−x − 0.4). It responds only to pixels darker than about p ≈ 77, i.e. clear aerated lung.

**Regions on the 7×7 pooled grid:**
- **Lung fields:** grid rows 1–4 (pixel rows 4–19), grid columns 1–2 and 4–5 (pixels 4–11 and 16–23). That is 16 cells.
- **Mediastinum and spine:** grid column 3 (pixels 12–15), rows 1–4. That is 4 cells.

**Output (L = mean lung brightness, C = mean mediastinum brightness, D = mean dark-air response in the lungs):**
- **Brightness contrast:** +5/16 per lung cell and −5/4 per mediastinum cell on filter 0. This gives 5·(L − C), and the +1 offsets cancel.
  - Normal: L − C ≈ −0.8. Pneumonia: L − C ≈ −0.5.
- **Dark-air term:** −4/16 per lung cell on filter 1, giving −4·D. Less clear dark lung means more pneumonia evidence.
- **Bias:** set at the estimated midpoint of the two classes. My guessed typical logits are about −4.8 for normal and −2.7 for pneumonia, so B = 3.75.

```edits
# filter 0: brightness (linear, always >= 0)
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
# filter 1: dark-air detector
CW[1, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[1] = -0.4
# lung fields brighter -> pneumonia
M[0, 0, 1:5, 1:3] = 0.3125
M[0, 0, 1:5, 4:6] = 0.3125
# relative to mediastinum brightness
M[0, 0, 1:5, 3] = -1.25
# dark aerated lung -> normal
M[0, 1, 1:5, 1:3] = -0.25
M[0, 1, 1:5, 4:6] = -0.25
B[:] = 3.75
```