"""Read each reply (answer.md) into a network and score it once on the test split.

    python evaluate.py runs/opus1      -> runs/opus1/<task>/{apply.json, network.npz, eval.json}
"""
import json, os, sys
import numpy as np
import edits, prompts
from prognet import TASKS, ROOT, build, load, evaluate


def read_network(flag, text):
    T = edits.zeros(*prompts.shape(flag))
    rep = edits.apply(text, T)
    rep["nonzero_weights"] = int(sum((v != 0).sum() for v in T.values()))
    rep["total_weights"] = int(sum(v.size for v in T.values()))
    return T, rep


def main(runs):
    for flag in TASKS:
        d = os.path.join(ROOT, runs, flag)
        if not os.path.exists(os.path.join(d, "answer.md")) or os.path.exists(os.path.join(d, "eval.json")):
            continue
        T, rep = read_network(flag, open(os.path.join(d, "answer.md")).read())
        json.dump(rep, open(os.path.join(d, "apply.json"), "w"), indent=1)
        np.savez(os.path.join(d, "network.npz"), **T)
        x, y = load(flag, "test")
        m = evaluate(build(T["CW"], T["CB"], T["M"], T["B"]), x, y, flag)
        json.dump({"split": "test", **m}, open(os.path.join(d, "eval.json"), "w"), indent=1)
        print(f"{flag:15s} read {rep['applied']}/{rep['statements']} statements -> test AUC={m['auc']:.3f} ACC={m['acc']:.3f}")


if __name__ == "__main__":
    main(sys.argv[1])
