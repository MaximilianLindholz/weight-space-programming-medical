# Hand-written CNN weights for PneumoniaMNIST (normal vs pneumonia)

## What the network looks for

Pneumonia shows up as opacity in the lungs. The lungs look whiter and hazier, they contrast less with the bright mediastinum and spine, and they have fewer very dark pixels. Rib and vessel edges inside the lungs also look softer.

## Layout on the 7×7 pooled grid

Each grid cell covers 4×4 pixels.
- **Lung fields:** grid rows 1–4 (pixel rows 4–19), in two blocks:
  - Grid columns 1–2 (pixel columns 4–11) for the patient's right lung.
  - Grid columns 4–5 (pixel columns 16–23) for the left lung.
- **Mediastinum and spine reference:** grid column 3 (pixel columns 12–15), grid rows 1–4.

## Filters

| Filter | Kernel and bias | What it measures |
|---|---|---|
| 0 | Identity, bias +1 | Brightness x+1, which is always ≥ 0, so the ReLU stays linear |
| 1 | −identity, bias −0.2 | Darkness: active for pixels below about 102/255, i.e. aerated, clear lung |
| 2, 3 | ±horizontal Sobel ÷4, bias −0.05 | Vertical edges of either sign, with a small threshold against noise |
| 4, 5 | ±vertical Sobel ÷4, bias −0.05 | Horizontal edges of either sign, e.g. ribs |

Filters 2–5 together approximate edge magnitude.

## How the output reads the evidence

**Filter 0 (lung contrast, main feature):**
- +0.5 on each of the 16 lung cells and −2.0 on each of the 4 central cells.
- The totals cancel (+8 and −8), so this term equals 8 × (mean lung brightness − mean central brightness).
- Because it is a difference, it is unaffected by the overall exposure of the X-ray.
- A brighter lung relative to the mediastinum pushes towards pneumonia.

**Filter 1 (dark lung pixels):**
- −0.25 on each lung cell.
- Very dark lung pixels push towards normal.

**Filters 2–5 (edges):**
- −0.125 on each lung cell.
- Sharp rib and vessel edges in the lungs push slightly towards normal.

## Bias

- **Normal estimate:** lung around 90/255 and centre around 170/255.
- **Pneumonia estimate:** lung around 120/255 and centre around 175/255.
- **Midpoint logit:** with these numbers, the logit halfway between the classes comes out near −4.9.
- **Chosen bias:** B = +5. This sets the 0.5 threshold close to that midpoint, nudged slightly towards pneumonia because about 62% of the test set is pneumonia.

These brightness levels are guesses, since I have not seen any images from the dataset. The bias therefore affects accuracy (ACC) but not AUC.

```edits
# Filter 0: brightness (x+1 >= 0)
CW[0, 0] = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
CB[0] = 1
# Filter 1: darkness (pixel below ~102/255)
CW[1, 0] = [[0, 0, 0], [0, -1, 0], [0, 0, 0]]
CB[1] = -0.2
# Filters 2,3: horizontal gradient (vertical edges), both signs
CW[2, 0] = [[-0.25, 0, 0.25], [-0.5, 0, 0.5], [-0.25, 0, 0.25]]
CB[2] = -0.05
CW[3, 0] = [[0.25, 0, -0.25], [0.5, 0, -0.5], [0.25, 0, -0.25]]
CB[3] = -0.05
# Filters 4,5: vertical gradient (horizontal edges), both signs
CW[4, 0] = [[-0.25, -0.5, -0.25], [0, 0, 0], [0.25, 0.5, 0.25]]
CB[4] = -0.05
CW[5, 0] = [[0.25, 0.5, 0.25], [0, 0, 0], [-0.25, -0.5, -0.25]]
CB[5] = -0.05

# Lung-vs-mediastinum brightness contrast (offset-invariant: +8 total vs -8 total)
M[0, 0, 1:5, 1:3] = 0.5
M[0, 0, 1:5, 4:6] = 0.5
M[0, 0, 1:5, 3] = -2.0

# Dark (aerated) lung pixels -> normal
M[0, 1, 1:5, 1:3] = -0.25
M[0, 1, 1:5, 4:6] = -0.25

# Sharp edges inside lungs -> normal (weak)
M[0, 2:6, 1:5, 1:3] = -0.125
M[0, 2:6, 1:5, 4:6] = -0.125

B[0] = 5
```