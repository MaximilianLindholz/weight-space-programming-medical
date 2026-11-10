"""The paper's figures -> figs/{task_examples, uterus_examples, compare, weights}.pdf

    python figures.py
Fig. 1 needs MedMNIST+ at higher resolution (data/<task>_64.npz or _224.npz, `medmnist` downloads them with size=64/224);
without them it falls back to 28x28.
"""
import os, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
import synthuterus
from prognet import ROOT, TASKS
import calls
from evidence_maps import trained

written_all = lambda f: calls.networks("opus", f)
astra_all = lambda f: calls.networks("astra", f)

FIGS = os.path.join(ROOT, "figs")
INK2, BLUE, GREEN, ORANGE = "#52514e", "#2a78d6", "#1b9e77", "#eb6834"
# Fig. 2 columns: (task, output, title)
COLS = [("chestmnist", 1, "Chest\ncardiomeg."), ("pneumoniamnist", 0, "Pneumonia\npneumonia"),
        ("breastmnist", 0, "Breast\nmalignant"), ("organamnist", 4, "OrganA\nkidney (L)"),
        ("organamnist", 6, "OrganA\nliver"), ("uterusmnist", 0, "SynthUterus\nretroflexion")]
map_r = lambda R, f, o, k: float(np.corrcoef(np.ravel(R[f][k][o]), np.ravel(R[f]["Et"][o]))[0, 1])   # r with Adam's map
UT_PICKS = {0: ["class0_0170", "class0_0197"], 1: ["class3_0198", "class3_0138"]}   # the data owner's illustrative cases


def save(fig, name, **kw):
    fig.savefig(os.path.join(FIGS, name + ".pdf"), metadata={"CreationDate": None}, **kw)   # byte-reproducible; plt.close(fig); print("wrote figs/" + name + ".pdf")


def task_examples():
    plt.rcdefaults()
    tasks = [("chestmnist", 64, "Chest X-ray", "ChestMNIST", ("no finding", "finding")),
             ("pneumoniamnist", 224, "Chest X-ray", "PneumoniaMNIST", ("normal", "pneumonia")),
             ("breastmnist", 224, "Breast US", "BreastMNIST", ("malignant", "normal/benign")),
             ("organamnist", 64, "CT axial", "OrganAMNIST", ("bladder", "spleen")),
             ("organcmnist", 64, "CT coronal", "OrganCMNIST", ("bladder", "spleen")),
             ("organsmnist", 64, "CT sagittal", "OrganSMNIST", ("bladder", "spleen")),
             ("uterus", 96, "Pelvic MRI", "SynthUterus", ("anteflexion", "retroflexion"))]
    rng = np.random.default_rng(0)
    override = {("organamnist", 0): 28407}   # the random pick (2628) shows mainly bowel/rectum, not the bladder
    plt.rcParams.update({"font.family": "serif"})
    fig, ax = plt.subplots(2, 7, figsize=(6.9, 2.38))
    for j, (f, size, mod, name, cls) in enumerate(tasks):
        if f == "uterus":
            ims = [np.asarray(Image.open(os.path.join(synthuterus.IMAGES, n + ".png")).convert("L")) for n in ("class0_0197", "class3_0138")]
        else:
            z = np.load(os.path.join(ROOT, "data", f + ".npz")); Y = z["train_labels"]
            if f == "chestmnist":
                a, b = np.where(Y.sum(1) == 0)[0], np.where(Y.sum(1) > 0)[0]
            else:
                y = Y.ravel(); a, b = np.where(y == 0)[0], np.where(y == y.max())[0]
            idx = [override.get((f, i), k) for i, k in enumerate([int(rng.choice(a)), int(rng.choice(b))])]
            try:
                Z = np.load(os.path.join(ROOT, "data", f"{f}_{size}.npz")); X = Z["train_images"]
                assert (Z["train_labels"][idx] == Y[idx]).all()
            except Exception:
                print(f"{f}: {size}px not available, using 28px"); X = z["train_images"]
            ims = [X[i] for i in idx]
        for i, im in enumerate(ims):
            a_ = ax[i, j]; a_.imshow(im, cmap="gray", vmin=0, vmax=255, interpolation="lanczos")
            a_.set_xticks([]); a_.set_yticks([])
            for s_ in a_.spines.values(): s_.set_visible(False)
            a_.set_xlabel(cls[i], fontsize=6.5, labelpad=1.5, color="#333333")
        ax[0, j].set_title(f"{name}\n{mod}", fontsize=7, pad=3, linespacing=1.1)
    plt.subplots_adjust(left=0.005, right=0.995, top=0.86, bottom=0.06, wspace=0.06, hspace=0.2)
    save(fig, "task_examples")


def uterus_examples():
    plt.rcdefaults()
    split = pd.read_csv(synthuterus.SPLIT_CSV).set_index("image").split
    assert all(split.get(n) in ("train", "val") for v in UT_PICKS.values() for n in v), "never a test case"
    fig, ax = plt.subplots(2, 4, figsize=(3.3, 1.9))
    for c in (0, 1):
        for k, name in enumerate(UT_PICKS[c]):
            im = Image.open(os.path.join(synthuterus.IMAGES, name + ".png")).convert("L"); j = 2 * c + k
            ax[0, j].imshow(np.asarray(im), cmap="gray", vmin=0, vmax=255)
            ax[1, j].imshow(np.asarray(im.resize((28, 28), Image.BOX)), cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    for x in ax.ravel():
        x.set_xticks([]); x.set_yticks([])
        for s_ in x.spines.values(): s_.set_linewidth(0.3)
    ax[0, 0].set_ylabel("96$\\times$96", fontsize=6); ax[1, 0].set_ylabel("28$\\times$28\n(input)", fontsize=6)
    plt.subplots_adjust(left=0.08, right=0.995, top=0.86, bottom=0.01, wspace=0.05, hspace=0.05)
    for c in (2, 3):
        for r_ in (0, 1):
            p = ax[r_, c].get_position(); ax[r_, c].set_position([p.x0 + 0.02, p.y0, p.width, p.height])
    for c, name in ((0, "anteflexion (label 0)"), (1, "retroflexion (label 1)")):
        l, r = ax[0, 2 * c].get_position(), ax[0, 2 * c + 1].get_position()
        fig.text((l.x0 + r.x1) / 2, 0.9, name, ha="center", va="bottom", fontsize=7)
        fig.add_artist(plt.Line2D([l.x0 + 0.01, r.x1 - 0.01], [0.885, 0.885], color="black", lw=0.5))
    save(fig, "uterus_examples", dpi=300)


def compare():
    plt.rcdefaults()
    R = json.load(open(os.path.join(ROOT, "results", "evidence_maps.json")))
    plt.rcParams.update({"font.family": "serif", "font.size": 6.3})
    fig, axs = plt.subplots(3, len(COLS), figsize=(3.3, 1.85))
    g = lambda v: f"{v:+.2f}".replace("0.", ".")
    for j, (f, o, title) in enumerate(COLS):
        for i, key in enumerate(("Ew", "Ea", "Et")):
            E = np.asarray(R[f][key])[o]; m = np.abs(E).max() or 1
            ax = axs[i, j]; ax.imshow(E, cmap="RdBu_r", vmin=-m, vmax=m); ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values(): s.set_linewidth(0.3)
        axs[0, j].set_title(title, fontsize=5.4, pad=2, linespacing=0.95)
        axs[2, j].set_xlabel(f"{g(map_r(R, f, o, 'Ew'))} / {g(map_r(R, f, o, 'Ea'))}", fontsize=5.4, labelpad=1.5)
    for i, lab in enumerate(("Opus", "Astra", "Adam")): axs[i, 0].set_ylabel(lab, fontsize=6.3)
    plt.subplots_adjust(left=0.07, right=0.995, top=0.84, bottom=0.08, wspace=0.08, hspace=0.08)
    save(fig, "compare")


def weights():
    plt.rcdefaults()
    flat = lambda d: np.concatenate([np.ravel(v) for v in d.values()])
    plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "axes.edgecolor": INK2})
    fig = plt.figure(figsize=(3.3, 2.8))
    ax = fig.add_axes([0.16, 0.585, 0.81, 0.32]); bins = np.linspace(-1, 1, 81)
    for get, lab, col in ((written_all, "Opus", BLUE), (astra_all, "GPT-6 Astra", GREEN), (lambda f: [trained(f)], "Adam (256 labels)", ORANGE)):
        v = np.concatenate([flat(n) / np.abs(flat(n)).max() for f in TASKS for n in get(f)])
        ax.hist(v, bins=bins, weights=np.full(len(v), 1 / len(v)), histtype="step", lw=1.1, color=col, label=lab)
    ax.set_yscale("log"); ax.set_xlim(-1, 1); ax.set_ylabel("share of weights")
    ax.set_xlabel("weight / largest |weight| of its network (all 7 tasks)", labelpad=1)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=6.3, loc="upper left", bbox_to_anchor=(0.0, 1.25), ncol=3, handlelength=1.2)
    ax.text(-0.17, 1.12, "(a)", transform=ax.transAxes, fontweight="bold")
    W, S_, A = written_all("uterusmnist")[0]["CW"][:, 0], astra_all("uterusmnist")[0]["CW"][:, 0], trained("uterusmnist")["conv.weight"][:, 0]
    for r, (F, lab) in enumerate(((W, "Opus"), (S_, "Astra"), (A, "Adam"))):
        for k in range(10):
            a = fig.add_axes([0.13 + k * 0.0845, 0.27 - r * 0.112, 0.075, 0.098]); m = np.abs(F[k]).max() or 1
            a.imshow(F[k], cmap="RdBu_r", vmin=-m, vmax=m); a.set_xticks([]); a.set_yticks([])
            for s in a.spines.values(): s.set_linewidth(0.3)
        fig.text(0.115, 0.319 - r * 0.112, lab, ha="right", va="center", fontsize=6.3)
    fig.text(0.13 - 0.135 * 0.84, 0.395, "(b)", fontweight="bold")
    fig.text(0.55, 0.395, "SynthUterus: the 10 convolution filters (red +, blue $-$)", ha="center", fontsize=6.3)
    save(fig, "weights")


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    task_examples(); uterus_examples(); compare(); weights()
