"""Score the written networks on exactly MedSigLIP's test images (prognet.test_subset), for Tab. 2's comparison.

    python score_subset.py      -> results/same_subset.json
"""
import json, os
import numpy as np
import calls
from prognet import MEDMNIST, ROOT, build, evaluate, test_subset


def mean(ms):
    return {"auc": float(np.mean([m["auc"] for m in ms])), "acc": float(np.mean([m["acc"] for m in ms])),
            "aucs": [m["auc"] for m in ms]}


def main():
    out = {}
    for f in MEDMNIST:
        x, y = test_subset(f); r = {"n": int(len(y))}
        for w in calls.WRITERS:
            r[w] = mean([evaluate(build(T["CW"], T["CB"], T["M"], T["B"]), x, y, f) for T in calls.networks(w, f)])
        out[f] = r
        print(f"{f:15s} n={r['n']:5d} opus={r['opus']['auc']:.3f} astra={r['astra']['auc']:.3f}")
    json.dump(out, open(os.path.join(ROOT, "results", "same_subset.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
