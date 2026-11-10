"""Every number in the paper, generated from the result files (nothing copied by hand).

    python make_tables.py      -> tables/{numbers, step1, example_answer}.tex
"""
import json, os
import numpy as np
import pandas as pd
import calls
from prognet import MEDMNIST, TASKS, ROOT, shape

OUT = os.path.join(ROOT, "tables"); os.makedirs(OUT, exist_ok=True)
J = lambda n: json.load(open(os.path.join(ROOT, "results", n)))
ADAM, VLM, SUB, EV, PR, AG = (J(n) for n in ("adam.json", "medsiglip.json", "same_subset.json", "evidence_maps.json",
                                              "uterus_probe.json", "agreement.json"))
SPLIT, DEDUP = (pd.read_csv(os.path.join(ROOT, "results", n)) for n in ("uterus_split.csv", "uterus_dedup.csv"))
ORG = ("organamnist", "organcmnist", "organsmnist")
NAME = {"chestmnist": "Chest", "pneumoniamnist": "Pneumonia", "breastmnist": "Breast", "organamnist": "OrganA",
        "organcmnist": "OrganC", "organsmnist": "OrganS", "uterusmnist": "SynthUterus"}
MOD = {"chestmnist": "Chest X-ray", "pneumoniamnist": "Chest X-ray", "breastmnist": "Breast US",
       "organamnist": "Abdominal CT", "organcmnist": "Abdominal CT", "organsmnist": "Abdominal CT", "uterusmnist": "Pelvic MRI"}
CLS = {"chestmnist": "14 (ML)", "pneumoniamnist": "2", "breastmnist": "2", "organamnist": "11", "organcmnist": "11",
       "organsmnist": "11", "uterusmnist": "2"}
RESNET = {"chestmnist": .768, "pneumoniamnist": .944, "breastmnist": .901, "organamnist": .997, "organcmnist": .992,
          "organsmnist": .972}   # published ResNet-18 (28) test AUC, MedMNIST v2 (Yang et al. 2023)
HI, LO = "$^{\\bullet}$", "$^{\\circ}$"            # exposure risk: high (MedMNIST) / low (SynthUterus)
f3 = lambda x: f"{x:.3f}"[1:] if x < 1 else f"{x:.3f}"
sd3 = lambda v: f"{np.std(v, ddof=1):.3f}"[1:]
nb = lambda s: s.replace(",", "{,}")

# written networks: AUC on the full test split (eval.json), three calls per writer and task
AUC = {w: {f: [e["auc"] for e in calls.evals(w, f)] for f in TASKS} for w in calls.WRITERS}
ACC = {w: {f: [e["acc"] for e in calls.evals(w, f)] for f in TASKS} for w in calls.WRITERS}
mo = {f: np.mean(AUC["opus"][f]) for f in TASKS}; ma = {f: np.mean(AUC["astra"][f]) for f in TASKS}
a256 = {f: ADAM[f]["256"]["auc"] for f in MEDMNIST}; afull = {f: ADAM[f]["full"]["auc"] for f in MEDMNIST}
ut_adam = np.mean([ADAM["uterusmnist"][f"s{s}"]["auc"] for s in range(3)])
zs = {f: VLM[f]["zero_shot"]["auc"] for f in TASKS}
S = {}

# ---- Tab. 2: test AUC; bold = best without labels (Opus, Astra, MedSigLIP zero-shot) per row
def bold3(vals, cells):
    b = max(vals)
    return [("\\textbf{" + c[:4] + "}" + c[4:]) if v == b else c for v, c in zip(vals, cells)]


rows = []
for f in TASKS:
    cell = lambda w: f3(np.mean(AUC[w][f])) + "$\\pm$" + sd3(AUC[w][f])
    lf = bold3([round(mo[f], 3), round(ma[f], 3), round(zs[f], 3)], [cell("opus"), cell("astra"), f3(zs[f])])
    if f == "uterusmnist":
        rows += ["\\midrule", f"SynthUterus{LO} & {MOD[f]} & {CLS[f]} & {' & '.join(lf)} & {f3(ut_adam)}$^\\ddagger$ & = & \\textcolor{{gray}}{{--}} \\\\"]
        continue
    rows.append(f"{NAME[f]}{HI} & {MOD[f]} & {CLS[f]} & {' & '.join(lf)} & {f3(a256[f])} & {f3(afull[f])} & \\textcolor{{gray}}{{{f3(RESNET[f])}}} \\\\")
    if f == MEDMNIST[-1]:
        m = lambda d: np.mean([d[g] for g in MEDMNIST])
        lf = bold3([round(m(mo), 3), round(m(ma), 3), round(m(zs), 3)], [f3(m(mo)), f3(m(ma)), f3(m(zs))])
        rows += ["\\midrule", f"\\multicolumn{{3}}{{l}}{{Mean (6 MedMNIST tasks)}} & {' & '.join(lf)} & {f3(m(a256))} & "
                              f"{f3(m(afull))} & \\textcolor{{gray}}{{{f3(m(RESNET))}}} \\\\"]
open(f"{OUT}/step1.tex", "w").write("\n".join(rows) + "\n")

# ---- numbers in the text: written networks, Adam, MedSigLIP
S["nTasks"] = len(TASKS)
S["tfMeanTF"] = f3(np.mean([mo[f] for f in MEDMNIST])); S["astraMean"] = f3(np.mean([ma[f] for f in MEDMNIST]))
S["tfChest"], S["tfPneu"], S["tfBreast"] = (f3(mo[f]) for f in ("chestmnist", "pneumoniamnist", "breastmnist"))
S["tfOrganMin"], S["tfOrganMax"] = f3(min(mo[f] for f in ORG)), f3(max(mo[f] for f in ORG))
S["tfRepSDtasks"] = f"{np.mean([np.std(AUC['opus'][f], ddof=1) for f in MEDMNIST]):.3f}"[1:]
S["astraRepSD"] = f"{np.mean([np.std(AUC['astra'][f], ddof=1) for f in MEDMNIST]):.3f}"[1:]
rng_ = [max(AUC["opus"][f]) - min(AUC["opus"][f]) for f in MEDMNIST]
S["tfRepRangePts"] = f"{100 * min(rng_):.1f}--{100 * max(rng_):.1f}"
rng_ = [max(AUC["astra"][f]) - min(AUC["astra"][f]) for f in MEDMNIST]
S["astraRepRangePts"] = f"{100 * min(rng_):.1f}--{100 * max(rng_):.1f}"
S["tfUterus"] = f3(mo["uterusmnist"]); S["tfUterusAcc"] = f3(np.mean(ACC["opus"]["uterusmnist"]))
S["tfRepUterus"] = f3(mo["uterusmnist"]) + "$\\pm$" + sd3(AUC["opus"]["uterusmnist"])
S["astraUterus"] = f3(ma["uterusmnist"])
S["adamMean"] = f3(np.mean([a256[f] for f in MEDMNIST]))
S["gapAdam"] = f"{100 * np.mean([a256[f] - mo[f] for f in MEDMNIST]):.1f}"
S["astraGapAdam"] = f"{100 * np.mean([a256[f] - ma[f] for f in MEDMNIST]):.1f}"
gaps = [100 * (a256[f] - d[f]) for d in (mo, ma) for f in MEDMNIST if f != "chestmnist"]
S["gapAdamRangeBoth"] = f"{min(gaps):.0f}--{max(gaps):.0f}"
beats = {w: sum(SUB[f][w]["auc"] > zs[f] for f in MEDMNIST) for w in ("opus", "astra")}
assert beats["opus"] == beats["astra"]   # the text says "both LLMs"
S["tfBeatsVLM"] = beats["opus"]; S["tfVLMn"] = len(MEDMNIST)
S["vlmZSPneu"] = f3(zs["pneumoniamnist"])
S["vlmProbeMean"] = f3(np.mean([VLM[f]["linear_probe"]["auc"] for f in MEDMNIST]))
S["utVZS"] = f3(zs["uterusmnist"]); S["utAdam"] = f3(ut_adam)

# ---- architecture
tot = [shape(f)[0] * (9 * shape(f)[1] + 1) + shape(f)[2] * (49 * shape(f)[0] + 1) for f in TASKS]
S["archMin"], S["archMax"] = nb(f"{min(tot):,}"), nb(f"{max(tot):,}")

# ---- SynthUterus cases
n = SPLIT.split.value_counts()
S["utN"] = len(SPLIT); S["utTrain"], S["utVal"], S["utTest"] = int(n["train"]), int(n["val"]), int(n["test"])
S["utNante"], S["utNretro"] = int((SPLIT.label == 0).sum()), int((SPLIT.label == 1).sum())
S["utDupRemoved"] = len(DEDUP); S["utNvalid"] = len(SPLIT) + len(DEDUP)
S["agClsPct"] = f"{AG['fields']['correct_class']['agree_pct']:.1f}"; S["agClsK"] = f"{AG['fields']['correct_class']['kappa']:.2f}"

# ---- Fig. 3: weight structure (Opus) vs Adam
flat = lambda d: np.concatenate([np.ravel(v) for v in d.values()])
from evidence_maps import trained  # noqa: E402
z, dd, da = [], [], []
for f in TASKS:
    for T in calls.networks("opus", f):
        w = flat(T); z.append(np.mean(w == 0)); dd.append(len(np.unique(np.round(w, 4))))
    da.append(len(np.unique(np.round(flat(trained(f)), 4))))
S["wZeroMin"], S["wZeroMax"] = f"{100 * min(z):.0f}", f"{100 * max(z):.0f}"
S["wDistMin"], S["wDistMax"] = min(dd), max(dd); S["aDistMin"], S["aDistMax"] = nb(f"{min(da):,}"), nb(f"{max(da):,}")

# ---- Fig. 2: correlation of each shown map with Adam's (the numbers below the columns)
from figures import COLS, map_r  # noqa: E402
sg = lambda v: f"{v:+.2f}".replace("0.", ".").replace("+", "$+$").replace("-", "$-$")
for (f, o, _), nm in zip(COLS, ("Chest", "Pneu", "Breast", "Kid", "Liv", "Ut")):
    if nm == "Chest": continue
    S[f"fg{nm}Op"], S[f"fg{nm}As"] = sg(map_r(EV, f, o, "Ew")), sg(map_r(EV, f, o, "Ea"))

# ---- SynthUterus probe: AUC of the lower grid rows alone
low = lambda w: [v["auc_rows_4_6"] for v in PR.values() if v["writer"] == w]
S["probeAsLow"] = f"{f3(min(low('astra')))}--{f3(max(low('astra')))}"; S["probeClLow"] = f"{f3(min(low('opus')))}--{f3(max(low('opus')))}"

# ---- output biases from the label distribution (Sec. 4.2): what no prompt states, and the example answer (Fig. S2)
from prognet import DATA_DIR  # noqa: E402
lab = lambda f, sp: np.load(os.path.join(DATA_DIR, f + ".npz"))[sp + "_labels"]
S["brPrior"] = f"{100 * lab('breastmnist', 'train').mean():.1f}"; S["pnPrior"] = f"{100 * lab('pneumoniamnist', 'test').mean():.1f}"
cp = 100 * lab("chestmnist", "test").mean(0); S["chPrevMin"], S["chPrevMax"] = f"{cp.min():.1f}", f"{cp.max():.1f}"
bb = lambda w, f: [float(T["B"][0]) for T in calls.networks(w, f)]
S["brBiasOp"] = f"{min(bb('opus', 'breastmnist')):+.1f}--{max(bb('opus', 'breastmnist')):.1f}"
S["brBiasAs"] = f"{min(bb('astra', 'breastmnist')):+.1f}--{max(bb('astra', 'breastmnist')):.1f}"
assert all(T["B"].max() < 0 for w in calls.WRITERS for T in calls.networks(w, "chestmnist"))       # every Chest bias negative
assert all(np.all(T["B"] == 0) for w in calls.WRITERS for T in calls.networks(w, "uterusmnist"))   # SynthUterus: all zero
EXAMPLE = ("runs/opus1", "breastmnist")
ans = open(os.path.join(ROOT, *EXAMPLE, "answer.md")).read().translate(str.maketrans({"\u2212": "-", "\u2013": "-", "\u00d7": "x"}))
assert ans.isascii()
import textwrap  # noqa: E402
wrapped = "\n".join(textwrap.fill(l, 118, subsequent_indent="  ", break_on_hyphens=False) if len(l) > 118 else l for l in ans.splitlines())
S["exAnsAUC"] = f3(json.load(open(os.path.join(ROOT, *EXAMPLE, "eval.json")))["auc"])
open(f"{OUT}/example_answer.tex", "w").write("\\begin{verbatim}\n" + wrapped + "\n\\end{verbatim}\n")

# ---- longest answer of either LLM (output tokens incl. reasoning)
tok = [json.load(open(os.path.join(ROOT, d, f, "run.json")))["usage"]["output_tokens"] for w in calls.WRITERS for f in TASKS for d in calls.calls(w, f)]
S["outTokMax"] = f"{round(max(tok), -3) / 1000:.0f}k"
open(f"{OUT}/numbers.tex", "w").write("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in S.items()))
print(f"wrote {len(S)} macros and step1.tex")
