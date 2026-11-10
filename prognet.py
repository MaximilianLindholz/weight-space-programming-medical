"""ProgNet: the small CNN whose weights the LLMs write, plus data loading and the official MedMNIST metrics.

    x (1 x 28 x 28, in [-1, 1]) -> Conv3x3 (K=10) -> ReLU -> AvgPool4 (10 x 7 x 7) -> Linear(490 -> n_out)

binary: n_out = 1 (sigmoid) | multi-label (Chest): 14 sigmoids | multi-class (Organ): softmax
"""
import os
import numpy as np
import torch
import torch.nn as nn
import medmnist
from medmnist import INFO
from medmnist.evaluator import getAUC, getACC
import synthuterus  # noqa: F401  (registers the task "uterusmnist")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
MEDMNIST = ["chestmnist", "pneumoniamnist", "breastmnist", "organamnist", "organcmnist", "organsmnist"]
TASKS = MEDMNIST + ["uterusmnist"]
K = 10


def n_out(flag):
    return 1 if INFO[flag]["task"] == "binary-class" else len(INFO[flag]["label"])


def shape(flag):
    """(filters, input channels, outputs)"""
    return K, INFO[flag]["n_channels"], n_out(flag)


def load(flag, split, cap=None, seed=0):
    """Images scaled to [-1, 1] as [N, 1, 28, 28] and labels [N, ...] (MedMNIST layout)."""
    if flag == "uterusmnist":
        return synthuterus.load(split)
    cls = getattr(medmnist, INFO[flag]["python_class"])
    ds = cls(split=split, download=True, root=DATA_DIR, size=28)
    imgs, y = ds.imgs, ds.labels
    if cap and len(imgs) > cap:
        idx = np.random.default_rng(seed).choice(len(imgs), cap, replace=False)
        imgs, y = imgs[idx], y[idx]
    x = torch.tensor(imgs, dtype=torch.float32).unsqueeze(1)
    return (x / 255.0 - 0.5) / 0.5, np.asarray(y)


class ProgNet(nn.Module):
    def __init__(self, c_in, k, n_out):
        super().__init__()
        self.conv = nn.Conv2d(c_in, k, 3, padding=1)
        self.pool = nn.AvgPool2d(4)
        self.fc = nn.Linear(k * 49, n_out)

    def forward(self, x):
        return self.fc(self.pool(torch.relu(self.conv(x))).flatten(1))


def build(conv_w, conv_b, maps, bias):
    """conv_w [K,C,3,3], conv_b [K], maps [n_out,K,7,7], bias [n_out] -> ProgNet"""
    conv_w = np.asarray(conv_w, dtype=np.float32); maps = np.asarray(maps, dtype=np.float32)
    net = ProgNet(conv_w.shape[1], conv_w.shape[0], maps.shape[0])
    with torch.no_grad():
        net.conv.weight.copy_(torch.from_numpy(conv_w))
        net.conv.bias.copy_(torch.tensor(np.asarray(conv_b), dtype=torch.float32))
        net.fc.weight.copy_(torch.from_numpy(maps.reshape(maps.shape[0], -1)))
        net.fc.bias.copy_(torch.tensor(np.asarray(bias, dtype=np.float32).reshape(-1)))
    return net


def load_checkpoint(name):
    """Adam baseline from checkpoints/<name>.pt, e.g. 'organamnist_256', 'uterusmnist_s0'"""
    sd = torch.load(os.path.join(ROOT, "checkpoints", name + ".pt"), map_location="cpu")
    k, c = sd["conv.weight"].shape[:2]
    net = ProgNet(c, k, sd["fc.bias"].shape[0]); net.load_state_dict(sd); return net


@torch.no_grad()
def predict(net, x, flag, bs=8192):
    net.eval()
    logits = torch.cat([net(x[i:i + bs]) for i in range(0, len(x), bs)])
    if INFO[flag]["task"] in ("binary-class", "multi-label, binary-class"):
        return torch.sigmoid(logits).numpy(), logits.numpy()
    return torch.softmax(logits, 1).numpy(), logits.numpy()


def evaluate(net, x, y, flag):
    score, _ = predict(net, x, flag)
    task = INFO[flag]["task"]
    return dict(auc=float(getAUC(y, score, task)), acc=float(getACC(y, score, task)))


def test_subset(flag):
    """The test images every model is compared on in Tab. 2's MedSigLIP column: the full test set if it has
    <= 2,000 images, else a fixed random subset (results/test_idx). SynthUterus: its full test split."""
    x, y = load(flag, "test")
    if flag == "uterusmnist":
        return x, y
    idx = np.load(os.path.join(ROOT, "results", "test_idx", f"{flag}_test_idx.npy"))
    return x[idx], y[idx]
