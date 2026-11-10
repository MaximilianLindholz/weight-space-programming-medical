"""Agreement between the two clinicians' independent SynthUterus ratings (% agreement, Cohen's kappa per field).

    python agreement.py      -> results/agreement.json
"""
import json, os
from sklearn.metrics import cohen_kappa_score
import synthuterus
from prognet import ROOT

FIELDS = {"realism": "Realism", "correct_class": "CorrectClass", "artefacts": "Artefacts", "anomalies": "Anomalies"}


def main():
    d = synthuterus.annotations(); d = d[d.file_exists].reset_index(drop=True)
    out = {"n_images": int(len(d)), "fields": {}}
    for f, col in FIELDS.items():
        a, b = d[f"{col}_1"].to_numpy(), d[f"{col}_2"].to_numpy()
        out["fields"][f] = {"agree_pct": float((a == b).mean() * 100), "kappa": float(cohen_kappa_score(a, b))}
    v1, v2 = d.validated_1.to_numpy(), d.validated_2.to_numpy()
    out["validated"] = {"reader_1": int(v1.sum()), "reader_2": int(v2.sum()), "both": int((v1 & v2).sum()),
                        "kappa": float(cohen_kappa_score(v1, v2))}
    json.dump(out, open(os.path.join(ROOT, "results", "agreement.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
