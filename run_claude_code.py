"""Tool-free, single-reply weight writing with Claude Opus 5.5 through Claude Code's headless mode.

    WSP_RUNS=runs/opus1 python run_claude_code.py [flag ...] [--effort high]
    python evaluate.py runs/opus1

Per task: a NEW empty working directory, one `claude -p` call with
    --tools ""                 no built-in tools          --strict-mcp-config   no MCP servers
    --setting-sources ""       no user/project settings   --system-prompt       "Answer the user's request."
    --no-session-persistence   nothing to resume          --output-format stream-json (full event log)
The prompt (prompts.build) is the only user message. A task is never re-asked once a reply exists.
Audit (run.json): tools offered at init == [], MCP servers == [], no tool_use block, exactly one turn.
"""
import argparse, json, os, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.environ.get("WSP_RUNS", "runs/opus1")   # runs/opus1..3: three independent calls per task
sys.path.insert(0, HERE)
import prompts  # noqa: E402
from prognet import TASKS  # noqa: E402

SYSTEM = "Answer the user's request."
MODEL = "claude-opus-5-5"


def run(flag, effort):
    out = os.path.join(HERE, RUNS, flag)
    if os.path.exists(os.path.join(out, "answer.md")):
        print(f"{flag}: already answered, skipping (never re-asked)"); return
    os.makedirs(out, exist_ok=True)
    prompt = prompts.build(flag)
    open(os.path.join(out, "prompt.txt"), "w").write(prompt)
    cmd = ["claude", "-p", "--tools", "", "--strict-mcp-config", "--setting-sources", "", "--system-prompt", SYSTEM,
           "--no-session-persistence", "--model", MODEL, "--effort", effort, "--output-format", "stream-json", "--verbose"]
    t0 = time.time()
    with tempfile.TemporaryDirectory() as cwd:   # empty folder: no CLAUDE.md, no project files, no data
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd, timeout=3 * 3600)
    wall = time.time() - t0
    open(os.path.join(out, "events.jsonl"), "w").write(p.stdout)
    ev = [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
    init = next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
    blocks = [c for e in ev if e.get("type") == "assistant" for c in e["message"]["content"]]
    result = next((e for e in ev if e.get("type") == "result"), {})
    answer = "\n".join(c.get("text", "") for c in blocks if c.get("type") == "text")
    thinking = "\n\n".join(c.get("thinking", "") or "" for c in blocks if c.get("type") == "thinking")
    if p.returncode != 0 or result.get("subtype") != "success" or not answer.strip():
        os.rename(os.path.join(out, "events.jsonl"), os.path.join(out, f"failed_{int(t0)}.jsonl"))
        print(f"{flag}: FAILED (exit {p.returncode}, {result.get('subtype')}): {p.stderr.strip()[:300]}"); return
    open(os.path.join(out, "answer.md"), "w").write(answer)
    open(os.path.join(out, "thinking.md"), "w").write(thinking)
    audit = {"tool_free": init.get("tools") == [] and not any(c.get("type") in ("tool_use", "server_tool_use") for c in blocks),
             "tools_at_init": init.get("tools"), "mcp_servers_at_init": init.get("mcp_servers"),
             "num_turns": result.get("num_turns"), "content_block_types": [c.get("type") for c in blocks]}
    rec = dict(runner="claude-code-headless", claude_code_version=init.get("claude_code_version"),
               model=MODEL, served_model=init.get("model"), effort=effort, max_output_tokens_env=os.environ.get("CLAUDE_CODE_MAX_OUTPUT_TOKENS"), auth=init.get("apiKeySource"),
               usage=result.get("usage"), notional_cost_usd=result.get("total_cost_usd"),
               wall_time_s=round(wall, 1), audit=audit, time=time.strftime("%Y-%m-%d %H:%M:%S"))
    json.dump(rec, open(os.path.join(out, "run.json"), "w"), indent=1)
    print(f"{flag}: ok, out_tokens={(result.get('usage') or {}).get('output_tokens')} tool_free={audit['tool_free']} "
          f"turns={audit['num_turns']} {wall:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("flags", nargs="*")
    ap.add_argument("--workers", type=int, default=1, help="independent calls run in parallel")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    a = ap.parse_args()
    def one(flag):
        try:
            run(flag, a.effort)
        except subprocess.TimeoutExpired:
            print(f"{flag}: timed out after 3 h")
    with ThreadPoolExecutor(a.workers) as ex:     # each task is still its own fresh, isolated call
        list(ex.map(one, a.flags or TASKS))


if __name__ == "__main__":
    main()
