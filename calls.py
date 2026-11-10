"""The calls the paper reports: three independent tool-free calls per task and writer (runs/<writer><i>/<task>/).
A call counts if it passed the audit (no tools offered or used, exactly one turn, reply not cut off) and was evaluated."""
import json, os
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
WRITERS = {"opus": ("runs/opus1", "runs/opus2", "runs/opus3"), "astra": ("runs/astra1", "runs/astra2", "runs/astra3")}


def passed(d, f):
    p = os.path.join(ROOT, d, f, "run.json")
    if not (os.path.exists(p) and os.path.exists(os.path.join(ROOT, d, f, "eval.json"))): return False
    a = json.load(open(p))["audit"]
    return bool(a.get("tool_free")) and a.get("num_turns") == 1 and a.get("complete", True)


def calls(writer, f):
    return [d for d in WRITERS[writer] if passed(d, f)]


def network(d, f):
    T = np.load(os.path.join(ROOT, d, f, "network.npz")); return {k: T[k] for k in ("CW", "CB", "M", "B")}


def networks(writer, f):
    return [network(d, f) for d in calls(writer, f)]


def evals(writer, f):
    return [json.load(open(os.path.join(ROOT, d, f, "eval.json"))) for d in calls(writer, f)]
