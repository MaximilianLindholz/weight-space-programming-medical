"""Where a network looks (Fig. 2): per 7x7 grid cell, the mean contribution to the class logit in test cases of the
class minus in the other cases (Sec. 3.6), for the first call of each LLM and the Adam network (256 labels;
SynthUterus: all training labels, seed 0). Analysis only: test images are used to measure, never to write.

    python evidence_maps.py      -> results/evidence_maps.json
"""
import os, json
import numpy as np, torch
import calls
from prognet import ROOT, build, load

TASKS = ["chestmnist", "pneumoniamnist", "breastmnist", "organamnist", "uterusmnist"]   # the tasks shown in Fig. 2


def trained(f):
    """Adam reference network as a dict of numpy arrays"""
    sd = torch.load(os.path.join(ROOT, "checkpoints", ("uterusmnist_s0" if f == "uterusmnist" else f"{f}_256") + ".pt"),
                    map_location="cpu")
    return {k: v.numpy() for k, v in sd.items()}


def as_net(d):
    if "CW" in d: return build(d["CW"], d["CB"], d["M"], d["B"])
    K = d["conv.weight"].shape[0]
    return build(d["conv.weight"], d["conv.bias"], d["fc.weight"].reshape(len(d["fc.bias"]), K, 7, 7), d["fc.bias"])


@torch.no_grad()
def evidence(net, x, Y):
    """[n_out, 7, 7]; Y: N x n_out binary class membership"""
    g = net.pool(torch.relu(net.conv(x)))                                   # N,K,7,7
    M = net.fc.weight.reshape(net.fc.out_features, *g.shape[1:])           # n,K,7,7
    C = torch.einsum("nkij,okij->noij", g, M).numpy()                      # N,n,7,7
    if Y.shape[1] > 1 and M.shape[0] == Y.shape[1] and Y.sum(1).max() == 1:  # softmax: relative to the class mean
        C = C - C.mean(1, keepdims=True)
    return np.stack([C[Y[:, o] == 1, o].mean(0) - C[Y[:, o] == 0, o].mean(0) for o in range(M.shape[0])])


def main():
    res = {}
    for f in TASKS:
        x, y = load(f, "test", cap=None if f == "uterusmnist" else 2000)
        Y = np.eye(11)[y.ravel()] if f == "organamnist" else np.asarray(y).reshape(len(y), -1)
        res[f] = {"Ew": evidence(as_net(calls.networks("opus", f)[0]), x, Y).tolist(),
                  "Ea": evidence(as_net(calls.networks("astra", f)[0]), x, Y).tolist(),
                  "Et": evidence(as_net(trained(f)), x, Y).tolist()}
        print("evidence maps:", f)
    json.dump(res, open(os.path.join(ROOT, "results", "evidence_maps.json"), "w"))


if __name__ == "__main__":
    main()
