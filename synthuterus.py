"""SynthUterus task: anteflexion vs retroflexion on synthetic sagittal uterine MRI crops.

Data: SynthUterus-ROI (Mueller et al. 2026, Zenodo 10.5281/zenodo.18587285, CC BY 4.0), unpacked to
data/SynthUterus-ROI/ (images/*.png at 96x96, synthuterus-roi_annotations.parquet with two clinicians' ratings).
Classes (file name digit): 0 anteflexed+anteverted -> label 0 (anteflexion), 3 retroflexed+retroverted -> label 1
(retroflexion); the mixed classes 1 and 2 are not used.
Case = rated by BOTH clinicians realistic, correct class and anomaly-free. Near-duplicates removed within each class:
repeatedly drop the image most similar to another remaining one while that similarity exceeds 0.95 (max Pearson
correlation over shifts of up to +-4 px at 32x32). Downsampled to 28x28 (PIL box filter); stratified split
40/20/40 (seed 0) -> results/uterus_split.csv, removed images -> results/uterus_dedup.csv.

    python synthuterus.py      # rebuilds the split and prints the counts
"""
import os
import numpy as np
import pandas as pd
import torch
from PIL import Image
from medmnist import INFO

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "data", "SynthUterus-ROI")
IMAGES = os.path.join(SRC, "images")
ANNOT = os.path.join(SRC, "synthuterus-roi_annotations.parquet")
SPLIT_CSV = os.path.join(ROOT, "results", "uterus_split.csv")
DEDUP_CSV = os.path.join(ROOT, "results", "uterus_dedup.csv")
CACHE = os.path.join(ROOT, "data", "synthuterus_28.npz")
FLAG = "uterusmnist"
FILE_CLASSES = {0: 0, 3: 1}            # file class -> label
FIELDS = ("Realism", "CorrectClass", "Artefacts", "Anomalies")
DUP_R, SIM_RES, SIM_SHIFT = 0.95, 32, 4

# the description is part of the prompt the LLMs received (prompts.py)
INFO[FLAG] = {"python_class": "UterusMNIST", "task": "binary-class", "n_channels": 1,
              "label": {"0": "anteflexion", "1": "retroflexion"},
              "description": "Synthetic sagittal uterine MRI slices (region-of-interest crops, greyscale): uterine flexion, "
                             "defined by the angle between the cervical canal line and the uterine cavity line: "
                             "anteflexion (cavity bent forward) or retroflexion (cavity bent backward)?"}


def annotations():
    """One row per image: per clinician (1, 2) the four fields as booleans meaning 'OK', plus label and validation."""
    a = pd.read_parquet(ANNOT).rename(columns={"file": "image"})
    d = pd.DataFrame({"image": a.image, "file_class": a.image.str[5].astype(int)})
    d["label"] = d.file_class.map(FILE_CLASSES)        # NaN for the mixed classes 1, 2
    d["file_exists"] = d.image.map(lambda n: os.path.exists(os.path.join(IMAGES, n + ".png")))
    for c in (1, 2):
        for f in FIELDS:
            d[f"{f}_{c}"] = a[f"{f}_clinician{c}"].astype(int).eq(1).to_numpy()
        d[f"validated_{c}"] = d.file_exists & d[f"Realism_{c}"] & d[f"CorrectClass_{c}"] & d[f"Anomalies_{c}"]
    d["validated"] = d.validated_1 & d.validated_2
    d["artefacts"] = np.where(~d.Artefacts_1 | ~d.Artefacts_2, "VISIBLE", "INVISIBLE")
    return d.sort_values("image").reset_index(drop=True)


def similarity(names):
    """Shift-tolerant pixel similarity between images (symmetric matrix, diagonal -1)."""
    R, S = SIM_RES, SIM_SHIFT
    X = np.stack([np.asarray(Image.open(os.path.join(IMAGES, n + ".png")).convert("L")
                             .resize((R + 2 * S, R + 2 * S), Image.BOX), float) for n in names])
    z = lambda a: (a - a.mean(1, keepdims=True)) / a.std(1, keepdims=True)
    core = z(X[:, S:S + R, S:S + R].reshape(len(X), -1)); best = np.full((len(X), len(X)), -1.0)
    for dy in range(-S, S + 1):
        for dx in range(-S, S + 1):
            sh = z(X[:, S + dy:S + dy + R, S + dx:S + dx + R].reshape(len(X), -1))
            best = np.maximum(best, core @ sh.T / core.shape[1])
    best = np.maximum(best, best.T); np.fill_diagonal(best, -1); return best


def dedup(v):
    keep, log = [], []
    for c in sorted(v.label.unique()):
        names = list(v.image[v.label == c]); S = similarity(names); alive = np.ones(len(names), bool)
        while True:
            m = np.where(alive[:, None] & alive[None, :], S, -1)
            nn = m.max(1); i = int(np.argmax(np.where(alive, nn, -2)))
            if nn[i] <= DUP_R: break
            log.append({"image": names[i], "label": int(c), "nearest_remaining": names[int(np.argmax(m[i]))],
                        "similarity": round(float(nn[i]), 4)})
            alive[i] = False
        keep += [n for n, a in zip(names, alive) if a]
    pd.DataFrame(log).to_csv(DEDUP_CSV, index=False)
    return v[v.image.isin(keep)].copy()


def make_split(seed=0):
    d = annotations()
    v = d[d.validated & d.label.notna()].copy(); v["label"] = v.label.astype(int)
    v = dedup(v)
    rng = np.random.default_rng(seed); v["split"] = ""
    for c in range(2):
        idx = rng.permutation(v.index[v.label == c].to_numpy())
        a, b = int(round(0.4 * len(idx))), int(round(0.6 * len(idx)))
        v.loc[idx[:a], "split"] = "train"; v.loc[idx[a:b], "split"] = "val"; v.loc[idx[b:], "split"] = "test"
    v[["image", "label", "split", "artefacts"]].to_csv(SPLIT_CSV, index=False)
    return d, v


def raw(split):
    """uint8 images [N,28,28] and labels [N,1]"""
    s = pd.read_csv(SPLIT_CSV)
    if not os.path.exists(CACHE):
        X = np.stack([np.asarray(Image.open(os.path.join(IMAGES, n + ".png")).convert("L").resize((28, 28), Image.BOX))
                      for n in s.image])
        np.savez_compressed(CACHE, X=X, names=s.image.to_numpy())
    z = np.load(CACHE, allow_pickle=True); assert list(z["names"]) == list(s.image)
    m = (s.split == split).to_numpy()
    return z["X"][m], s.label.to_numpy()[m].reshape(-1, 1)


def load(split):
    x, y = raw(split)
    x = torch.tensor(x, dtype=torch.float32).unsqueeze(1)
    return (x / 255.0 - 0.5) / 0.5, y


if __name__ == "__main__":
    d, v = make_split()
    print(f"annotated {len(d)}, validated by both (classes 0 and 3) + de-duplicated: {len(v)}")
    print(pd.crosstab(v.label, v.split))
