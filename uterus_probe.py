"""Why GPT-6 Astra's SynthUterus networks are below chance while Opus's are above (analysis after the results).

(1) Line test: a bright "\\" and a bright "/" line on a dark 28x28 image. Both writers state the same rule
    ("\\" = anteflexion, "/" = retroflexion, anterior = image left); this checks that each network implements it.
(2) On the SynthUterus test split the logit is a sum of read-out contributions (filter k, grid cell); the AUC of the
    upper grid rows 0-3 and the lower rows 4-6 alone shows which part carries or inverts the result.

    python uterus_probe.py      -> results/uterus_probe.json
"""
import os, json
import numpy as np, torch, torch.nn.functional as F
from sklearn.metrics import roc_auc_score
import calls
from prognet import ROOT, build, load


def line(kind, w=2):
    x = -np.ones((28, 28), np.float32)
    for i in range(4, 24):
        j = i if kind == "\\" else 27 - i
        x[i, max(0, j - w // 2): j + w // 2 + 1] = 1
    return torch.tensor(x)[None, None]


def main():
    x, y = load("uterusmnist", "test"); y = np.asarray(y).ravel(); res = {}
    for w in calls.WRITERS:
        for d in calls.calls(w, "uterusmnist"):
            T = calls.network(d, "uterusmnist"); net = build(T["CW"], T["CB"], T["M"], T["B"])
            with torch.no_grad():
                lt = {k: float(net(line(k)).ravel()[0]) for k in ("\\", "/")}
            g = F.avg_pool2d(F.relu(F.conv2d(x, torch.tensor(T["CW"]).float(), torch.tensor(T["CB"]).float(), padding=1)), 4).numpy()
            C = g * T["M"].reshape(-1, T["CW"].shape[0], 7, 7)[0][None]          # N, K, 7, 7
            res[d] = {"writer": w, "line_logit": lt, "line_rule_ok": lt["/"] > lt["\\"],
                      "auc": float(roc_auc_score(y, C.sum((1, 2, 3)) + T["B"].ravel()[0])),
                      "auc_rows_0_3": float(roc_auc_score(y, C[:, :, :4].sum((1, 2, 3)))),
                      "auc_rows_4_6": float(roc_auc_score(y, C[:, :, 4:].sum((1, 2, 3))))}
            print(d, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[d].items() if k != "line_logit"})
    json.dump(res, open(os.path.join(ROOT, "results", "uterus_probe.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
