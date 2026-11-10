"""MedSigLIP baselines (google/medsiglip-448) on the 7 tasks.

  zero-shot    : cosine similarity to fixed class prompts (written once, never tuned)
  linear probe : logistic regression on image embeddings of the same labelled images as Adam
                 (MedMNIST: the 256 of the Adam-256 baseline; SynthUterus: all training images)
Inputs: the same 28x28 images, converted to RGB and resized by the MedSigLIP processor. MedMNIST test sets with more
than 2,000 images are scored on a fixed random subset (seed 0), saved in results/test_idx/ so that every model is
compared on the same images (score_subset.py).
The model is gated: accept its terms on huggingface.co/google/medsiglip-448, then `hf auth login`.

    python medsiglip.py      -> results/medsiglip.json
"""
import json, os, sys
import numpy as np, torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
import medmnist
from medmnist import INFO
from medmnist.evaluator import getAUC, getACC
import synthuterus
from prognet import MEDMNIST, ROOT, DATA_DIR
from adam import subsample, CAP

MAX_TEST = 2000
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
IDX = os.path.join(ROOT, "results", "test_idx")
ORG = {"femur-left": "left femur", "femur-right": "right femur", "kidney-left": "left kidney",
       "kidney-right": "right kidney", "lung-left": "left lung", "lung-right": "right lung"}


def prompts(flag):
    L = [INFO[flag]["label"][str(i)] for i in range(len(INFO[flag]["label"]))]
    if flag == "pneumoniamnist":
        return ["a normal pediatric chest x-ray", "a pediatric chest x-ray showing pneumonia"]
    if flag == "breastmnist":
        return ["a breast ultrasound image showing a malignant tumor",
                "a breast ultrasound image showing normal tissue or a benign lesion"]
    if flag.startswith("organ"):
        view = {"organamnist": "axial", "organcmnist": "coronal", "organsmnist": "sagittal"}[flag]
        return [f"an {view} abdominal CT image of the {ORG.get(l, l)}" for l in L]
    if flag == "chestmnist":  # pairs: [no finding_i, finding_i] for each label
        return [p for l in L for p in (f"a chest x-ray with no {l}", f"a chest x-ray showing {l}")]
    if flag == "uterusmnist":
        return [f"a sagittal pelvic MRI of a uterus with {d}" for d in ("anteflexion", "retroflexion")]
    raise ValueError(flag)


def raw(flag, split):
    if flag == "uterusmnist":
        return synthuterus.raw(split)
    ds = getattr(medmnist, INFO[flag]["python_class"])(split=split, download=True, root=DATA_DIR, size=28)
    return ds.imgs, np.asarray(ds.labels)


def test_indices(flag, n):
    p = os.path.join(IDX, f"{flag}_test_idx.npy")
    if not os.path.exists(p):
        os.makedirs(IDX, exist_ok=True)
        np.save(p, np.arange(n) if n <= MAX_TEST else np.sort(np.random.default_rng(0).choice(n, MAX_TEST, replace=False)))
    return np.load(p)


def train_indices(flag):
    """MedMNIST: exactly the 256 images of the Adam-256 baseline; SynthUterus: all training images"""
    _, y = raw(flag, "train")
    if flag == "uterusmnist":
        return np.arange(len(y))
    pool = np.random.default_rng(0).choice(len(y), CAP, replace=False) if len(y) > CAP else np.arange(len(y))
    return pool[subsample(y[pool], 256, np.random.default_rng(0))]


@torch.no_grad()
def embed_images(model, proc, imgs, bs=32):
    out = []
    for i in range(0, len(imgs), bs):
        inp = proc(images=[Image.fromarray(im).convert("RGB") for im in imgs[i:i + bs]], return_tensors="pt").to(DEVICE)
        e = model.get_image_features(**inp); e = e.pooler_output if hasattr(e, "pooler_output") else e
        out.append(torch.nn.functional.normalize(e.float(), dim=-1).cpu())
    return torch.cat(out).numpy()


@torch.no_grad()
def embed_texts(model, proc, texts):
    e = model.get_text_features(**proc(text=texts, padding="max_length", return_tensors="pt").to(DEVICE))
    e = e.pooler_output if hasattr(e, "pooler_output") else e
    return torch.nn.functional.normalize(e.float(), dim=-1).cpu().numpy()


def zero_shot(flag, sim):
    task = INFO[flag]["task"]
    if task == "multi-label, binary-class":
        return torch.softmax(torch.tensor(sim.reshape(len(sim), -1, 2) * 100), -1)[..., 1].numpy()
    s = torch.softmax(torch.tensor(sim * 100), -1).numpy()
    return s[:, 1] if task == "binary-class" else s


def probe(flag, Xtr, ytr, Xte):
    task = INFO[flag]["task"]
    if task == "multi-label, binary-class":
        return np.stack([LogisticRegression(max_iter=5000).fit(Xtr, ytr[:, j]).predict_proba(Xte)[:, 1]
                         if len(np.unique(ytr[:, j])) > 1 else np.full(len(Xte), ytr[:, j].mean())
                         for j in range(ytr.shape[1])], 1)
    clf = LogisticRegression(max_iter=5000).fit(Xtr, ytr[:, 0]); p = clf.predict_proba(Xte)
    full = np.zeros((len(Xte), len(INFO[flag]["label"]))); full[:, clf.classes_] = p
    return full[:, 1] if task == "binary-class" else full


def main():
    from transformers import AutoModel, AutoProcessor
    model = AutoModel.from_pretrained("google/medsiglip-448").to(DEVICE).eval()
    proc = AutoProcessor.from_pretrained("google/medsiglip-448")
    path = os.path.join(ROOT, "results", "medsiglip.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    for flag in (sys.argv[1:] or MEDMNIST + ["uterusmnist"]):
        task = INFO[flag]["task"]
        xt, yt = raw(flag, "test")
        if flag != "uterusmnist":
            ti = test_indices(flag, len(xt)); xt, yt = xt[ti], yt[ti]
        xr, yr = raw(flag, "train"); tr = train_indices(flag); xr, yr = xr[tr], yr[tr]
        Ete, Etr = embed_images(model, proc, xt), embed_images(model, proc, xr)
        zs = zero_shot(flag, Ete @ embed_texts(model, proc, prompts(flag)).T); lp = probe(flag, Etr, yr, Ete)
        res[flag] = {"n_test": int(len(yt)), "prompts": prompts(flag),
                     "zero_shot": {"auc": float(getAUC(yt, zs, task)), "acc": float(getACC(yt, zs, task))},
                     "linear_probe": {"auc": float(getAUC(yt, lp, task)), "acc": float(getACC(yt, lp, task))}}
        print(f"{flag:15s} n={len(yt):5d} zero-shot AUC={res[flag]['zero_shot']['auc']:.3f} "
              f"probe AUC={res[flag]['linear_probe']['auc']:.3f}", flush=True)
        json.dump(res, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
