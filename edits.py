"""A small, safe 'edits' language for writing ProgNet weights as text (modelled on the
`edits` blocks of the Weight-Space Programming logs).

Tensors (all start at 0):
  CW  conv weights  [K, C, 3, 3]      CB  conv biases  [K]
  M   read-out maps [n_out, K, 7, 7]  B   output biases [n_out]

Statement forms (one per line, '#' starts a comment, a list may continue over lines):
  M[0, 3, 2:5, 2:5] = 0.25                 fill a block
  CW[0, 0] = [[0,0,0],[0,1,0],[0,0,0]]     explicit nested list (shape must match)
  B[:] += -1.5                             also -=, *=
Only the LAST ```edits block of a reply is read. Unreadable statements are skipped and reported.
No code is executed: indices are parsed by a regex, values by ast.literal_eval.
"""
import ast
import re
import numpy as np

TENSORS = ("CW", "CB", "M", "B")
_STMT = re.compile(r"^\s*(CW|CB|M|B)\s*\[([^\]]*)\]\s*(=|\+=|-=|\*=)\s*(.+?)\s*$", re.S)
_INT = r"-?\d+"
_PART = re.compile(rf"^\s*(?:({_INT})|({_INT})?\s*:\s*({_INT})?(?:\s*:\s*({_INT}))?)\s*$")


def zeros(k, c, n_out):
    return {"CW": np.zeros((k, c, 3, 3), np.float32), "CB": np.zeros(k, np.float32),
            "M": np.zeros((n_out, k, 7, 7), np.float32), "B": np.zeros(n_out, np.float32)}


def last_block(text):
    blocks = re.findall(r"```edits[ \t]*\n(.*?)```", text, re.S)
    return blocks[-1] if blocks else None


def _statements(block):
    """Join continuation lines: a statement ends when its brackets are balanced."""
    out, cur, depth = [], "", 0
    for raw in block.split("\n"):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        cur = (cur + " " + line) if cur else line
        depth = cur.count("[") - cur.count("]")
        if depth <= 0:
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return out


def _index(spec, ndim):
    parts = [p for p in spec.split(",")] if spec.strip() else []
    if len(parts) > ndim:
        raise ValueError(f"too many indices ({len(parts)} > {ndim})")
    idx = []
    for p in parts:
        m = _PART.match(p)
        if not m:
            raise ValueError(f"bad index '{p}'")
        if m.group(1) is not None:
            idx.append(int(m.group(1)))
        else:
            g = lambda i: None if m.group(i) is None else int(m.group(i))
            idx.append(slice(g(2), g(3), g(4)))
    return tuple(idx)


def apply(text, tensors, max_abs=1e6):
    """Apply the last edits block of `text` to `tensors` in place. Returns a report dict."""
    block = last_block(text)
    rep = {"found_block": block is not None, "statements": 0, "applied": 0, "errors": []}
    if block is None:
        return rep
    for st in _statements(block):
        rep["statements"] += 1
        try:
            m = _STMT.match(st)
            if not m:
                raise ValueError("not a statement")
            name, spec, op, val = m.groups()
            t = tensors[name]
            idx = _index(spec, t.ndim)
            v = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
            if not np.all(np.isfinite(v)) or np.abs(v).max(initial=0) > max_abs:
                raise ValueError("value out of range")
            target = t[idx]
            if v.ndim and v.shape != np.shape(target):
                raise ValueError(f"shape {v.shape} != target {np.shape(target)}")
            if op == "=":
                t[idx] = v
            elif op == "+=":
                t[idx] = target + v
            elif op == "-=":
                t[idx] = target - v
            else:
                t[idx] = target * v
            rep["applied"] += 1
        except Exception as e:  # noqa: BLE001 - every failure is reported, never raised
            rep["errors"].append({"statement": st[:200], "error": str(e)})
    return rep


def export(conv_w, conv_b, maps, bias, tol=1e-12):
    """Write existing arrays as an edits block (used to round-trip-test the parser)."""
    lines = ["```edits"]
    W = np.asarray(conv_w); M = np.asarray(maps)
    for k in range(W.shape[0]):
        for c in range(W.shape[1]):
            if np.abs(W[k, c]).max() > tol:
                lines.append(f"CW[{k}, {c}] = {np.round(W[k, c], 6).tolist()}")
    if np.abs(conv_b).max() > tol:
        lines.append(f"CB[:] = {np.round(np.asarray(conv_b), 6).tolist()}")
    for o in range(M.shape[0]):
        for k in range(M.shape[1]):
            if np.abs(M[o, k]).max() > tol:
                lines.append(f"M[{o}, {k}] = {np.round(M[o, k], 6).tolist()}")
    lines.append(f"B[:] = {np.round(np.asarray(bias).reshape(-1), 6).tolist()}")
    lines.append("```")
    return "\n".join(lines)
