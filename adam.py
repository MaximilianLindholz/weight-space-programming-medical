"""Adam baselines on the identical ProgNet (K = 10), early stopping on validation AUC.

  MedMNIST, "256": 256 class-stratified labelled images | "full": all training images (capped at 20k), seed 0
  SynthUterus: all training labels, seeds 0-2
Learning rate 3e-3, weight decay 1e-4, batch size 64.

    python adam.py train     -> checkpoints/*.pt   (the released checkpoints are the ones reported)
    python adam.py eval      -> results/adam.json  (test AUC/ACC of the checkpoints)
"""
import json, os, sys
import numpy as np, torch, torch.nn.functional as F
from medmnist import INFO
from prognet import MEDMNIST, ROOT, K, ProgNet, load, evaluate, n_out, load_checkpoint

CAP = 20000
OUT = os.path.join(ROOT, "checkpoints")


def loss_fn(logits, y, task):
    if task == "binary-class":
        return F.binary_cross_entropy_with_logits(logits.squeeze(1), y.float().squeeze(1))
    if task == "multi-label, binary-class":
        return F.binary_cross_entropy_with_logits(logits, y.float())
    return F.cross_entropy(logits, y.long().squeeze(1))


def subsample(y, n, rng):
    """n class-stratified indices (multi-label: random), >= 1 per class"""
    if n is None or n >= len(y):
        return np.arange(len(y))
    if y.shape[1] > 1:
        return rng.choice(len(y), n, replace=False)
    idx = []
    for c in np.unique(y[:, 0]):
        pool = np.where(y[:, 0] == c)[0]
        idx.append(rng.choice(pool, min(max(1, int(round(n * len(pool) / len(y)))), len(pool)), replace=False))
    return np.concatenate(idx)[:n] if sum(len(i) for i in idx) > n else np.concatenate(idx)


def fit(flag, x, y, xv, yv, epochs, every):
    task = INFO[flag]["task"]; y = torch.tensor(y)
    net = ProgNet(x.shape[1], K, n_out(flag))
    opt = torch.optim.Adam(net.parameters(), lr=3e-3, weight_decay=1e-4)
    best, state = -1, None
    for ep in range(epochs):
        net.train()
        for b in torch.randperm(len(x)).split(64):
            loss = loss_fn(net(x[b]), y[b], task); opt.zero_grad(); loss.backward(); opt.step()
        if ep % every == 0 or ep == epochs - 1:
            m = evaluate(net, xv, yv, flag)
            if m["auc"] > best:
                best, state = m["auc"], {k: v.clone() for k, v in net.state_dict().items()}
    net.load_state_dict(state); return net


def train_medmnist(flag, n, seed=0, epochs=40):
    rng = np.random.default_rng(seed); torch.manual_seed(seed)
    x, y = load(flag, "train", cap=CAP); xv, yv = load(flag, "val")
    idx = subsample(y, n, rng); x, y = x[idx], y[idx]
    steps = max(1, len(x) // 64)
    epochs = epochs if n is None else max(epochs, 2000 // steps)       # small sets: >= ~2000 steps
    return fit(flag, x, y, xv, yv, epochs, max(1, epochs // 20))


def train_uterus(seed, epochs=200):
    torch.manual_seed(seed)
    x, y = load("uterusmnist", "train"); xv, yv = load("uterusmnist", "val")
    return fit("uterusmnist", x, y, xv, yv, epochs, 10)


def main(stage):
    os.makedirs(OUT, exist_ok=True)
    if stage == "train":
        for f in MEDMNIST:
            for b, n in (("256", 256), ("full", None)):
                torch.save(train_medmnist(f, n).state_dict(), os.path.join(OUT, f"{f}_{b}.pt"))
        for s in (0, 1, 2):
            torch.save(train_uterus(s).state_dict(), os.path.join(OUT, f"uterusmnist_s{s}.pt"))
    res = {}
    for f in MEDMNIST:
        x, y = load(f, "test")
        res[f] = {b: evaluate(load_checkpoint(f"{f}_{b}"), x, y, f) for b in ("256", "full")}
    x, y = load("uterusmnist", "test")
    res["uterusmnist"] = {f"s{s}": evaluate(load_checkpoint(f"uterusmnist_s{s}"), x, y, "uterusmnist") for s in (0, 1, 2)}
    json.dump(res, open(os.path.join(ROOT, "results", "adam.json"), "w"), indent=1)
    for f, r in res.items():
        print(f"{f:15s} " + "  ".join(f"{k}: AUC {v['auc']:.3f}" for k, v in r.items()))


if __name__ == "__main__":
    main(sys.argv[1])
