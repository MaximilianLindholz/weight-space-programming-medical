## Design

The rule is that pneumonia makes the lung fields opaque. Normal pediatric lungs are dark (air) and contrast sharply with the bright mediastinum and spine. In pneumonia the lung fields turn hazy and whiter, so the gap between lung and mediastinum shrinks. I use two intensity features and no texture filters, because at 28×28 the sign of texture evidence is unreliable.

**Filters**
- **Filter 0, brightness:** identity kernel with bias +1, so h = x + 1, which is never negative. Each pooled cell then holds the mean brightness plus 1.
- **Filter 1, dark-air detector:** kernel −1 at the centre with bias −0.2, so h = ReLU(−x − 0.2). It fires on pixels darker than about p ≈ 100, which is the aerated lung of a normal film.

**Readout regions** (7×7 grid)
- Lung fields: grid rows 1–5 and grid columns 1–2 (image-left lung) plus 4–5 (image-right lung). That is pixel rows 4–23 and pixel columns 4–11 and 16–23.
- Mediastinum and spine: grid column 3, rows 1–5 (pixel columns 12–15).

**Evidence read by the output**
1. **Contrast term, D = mean(lung brightness) − mean(mediastinum brightness).**
   - Lung cells get weight +0.6 (that is 6/10) and mediastinum cells get −1.2 (that is 6/5), so the output adds 6·D.
   - The +1 offset of filter 0 cancels, because the weights sum to zero.
   - This term is relatively robust to exposure. My estimates are D ≈ −0.8 for normal films and ≈ −0.55 for pneumonia, so a higher D (less contrast) pushes toward pneumonia.
2. **Dark-air term.**
   - Each lung cell of filter 1 gets weight −0.8, so clearly aerated dark lungs push toward normal.
   - My estimates are about −1.4 for normal films and −0.4 for pneumonia.
3. **Bias +4.8.**
   - This centres the decision between my estimated class means.
   - It also leans slightly toward pneumonia, since about 62.5% of the test set is pneumonia.
   - Estimated logits are about −1.4 for normal and +1.1 for pneumonia.

The intensity values behind the bias are guesses, not measurements. Accuracy at the 0.5 threshold therefore depends on how close those guesses are to the real data. AUC does not depend on the bias.

```edits
# Filter 0: brightness (x + 1, always >= 0)
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
# Filter 1: dark aerated-lung detector ReLU(-x - 0.2)
CW[1, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[1] = -0.2

# Contrast: lung brightness (+) vs mediastinum brightness (-); weights sum to zero
M[0, 0, 1:6, 1:3] = 0.6
M[0, 0, 1:6, 4:6] = 0.6
M[0, 0, 1:6, 3] = -1.2

# Dark air in lung fields -> normal
M[0, 1, 1:6, 1:3] = -0.8
M[0, 1, 1:6, 4:6] = -0.8

# Bias: centres between estimated class means, slight pneumonia prior
B[0] = 4.8
```