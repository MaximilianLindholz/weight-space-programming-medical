"""Tool-free, single-reply weight writing with OpenAI's GPT-6 Astra via the Responses API (one fresh request per task).
Same prompt (prompts.build) and same output files as run_claude_code.py, so evaluate.py works unchanged.

    export OPENAI_API_KEY=...       # or put the key in ~/.openai_api_key (outside the repository, chmod 600)
    WSP_RUNS=runs/astra1 python run_openai.py [flag ...] [--effort high] [--workers 4]
    python evaluate.py runs/astra1

Per task: ONE POST /v1/responses, standard library only (no SDK), streamed (server-sent events) so that long
reasoning does not hit an HTTP timeout. The request has NO `tools` field, `instructions` = "Answer the user's
request." (the neutral system line of the WSP harness), the prompt as the only input, no previous_response_id,
store=false. Unlike Claude Code, nothing is added by a client: request.json is exactly what the model received
(apart from OpenAI's own server-side formatting).
Files per run:  prompt.txt   request.json (exact body sent)   events.jsonl (raw stream)   response.json (final object)
                answer.md    thinking.md (reasoning summaries, if returned)   run.json (usage, audit)
Audit (run.json): no tools in the request and in the echoed response, output items only of type reasoning/message,
status "completed" (not cut off by max_output_tokens). A task is never re-asked once it has an answer; a request that
fails before answering (HTTP error, network) is kept as failed_<time>.json and may be sent again.
"""
import argparse, json, os, socket, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.environ.get("WSP_RUNS", "runs/astra1")   # runs/astra1..3: three independent calls per task
sys.path.insert(0, HERE)
import prompts  # noqa: E402
from prognet import TASKS  # noqa: E402

URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-6-astra"
SYSTEM = "Answer the user's request."
MAX_OUT = 128000                                      # model maximum (developers.openai.com model page)
KEY_FILE = os.path.expanduser("~/.openai_api_key")    # never inside the repository


def api_key():
    k = os.environ.get("OPENAI_API_KEY") or (open(KEY_FILE).read().strip() if os.path.exists(KEY_FILE) else "")
    if not k:
        sys.exit("no API key: export OPENAI_API_KEY=... or write it to ~/.openai_api_key")
    return k


def stream(body, key, events_path):
    """POST with stream=true; write every SSE event to events_path; return (final response object, error or None)."""
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "Accept": "text/event-stream"})
    final, err = None, None
    with urllib.request.urlopen(req, timeout=900) as r, open(events_path, "w") as ev:   # 15 min max silence
        for raw in r:
            line = raw.decode("utf-8").rstrip("\n")
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            ev.write(data + "\n")
            e = json.loads(data)
            t = e.get("type", "")
            if t in ("response.completed", "response.incomplete", "response.failed"):
                final = e.get("response")
            elif t == "error":
                err = e
    return final, err


def run(flag, effort, summary):
    out = os.path.join(HERE, RUNS, flag)
    if os.path.exists(os.path.join(out, "answer.md")):
        print(f"{flag}: already answered, skipping (never re-asked)"); return
    os.makedirs(out, exist_ok=True)
    prompt = prompts.build(flag)
    open(os.path.join(out, "prompt.txt"), "w").write(prompt)
    body = {"model": MODEL, "instructions": SYSTEM, "input": prompt, "max_output_tokens": MAX_OUT,
            "reasoning": {"effort": effort, **({"summary": "auto"} if summary else {})},
            "store": False, "stream": True}
    open(os.path.join(out, "request.json"), "w").write(json.dumps(body, indent=1))
    t0 = time.time(); ev_path = os.path.join(out, "events.jsonl")
    try:
        resp, err = stream(body, api_key(), ev_path)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        json.dump({"http_status": e.code, "body": msg, "request": body}, open(os.path.join(out, f"failed_{int(t0)}.json"), "w"), indent=1)
        if os.path.exists(ev_path): os.remove(ev_path)
        print(f"{flag}: FAILED before answering (HTTP {e.code}): {msg[:300]}"); return
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
        if os.path.exists(ev_path): os.rename(ev_path, os.path.join(out, f"failed_{int(t0)}.jsonl"))
        print(f"{flag}: FAILED (network: {e}); events kept"); return
    wall = time.time() - t0
    if resp is None:
        os.rename(ev_path, os.path.join(out, f"failed_{int(t0)}.jsonl"))
        print(f"{flag}: FAILED (no final response; error={err})"); return
    json.dump(resp, open(os.path.join(out, "response.json"), "w"), indent=1)
    items = resp.get("output") or []
    answer = "\n".join(c.get("text", "") for it in items if it.get("type") == "message"
                       for c in it.get("content") or [] if c.get("type") == "output_text")
    thinking = "\n\n".join(s.get("text", "") for it in items if it.get("type") == "reasoning"
                           for s in it.get("summary") or [])
    status = resp.get("status")
    if not answer.strip():
        os.rename(ev_path, os.path.join(out, f"failed_{int(t0)}.jsonl"))
        os.rename(os.path.join(out, "response.json"), os.path.join(out, f"failed_{int(t0)}_response.json"))
        print(f"{flag}: FAILED (status {status}, no answer text; {resp.get('incomplete_details')})"); return
    open(os.path.join(out, "answer.md"), "w").write(answer)
    open(os.path.join(out, "thinking.md"), "w").write(thinking)
    types = [it.get("type") for it in items]
    audit = {"tool_free": "tools" not in body and not resp.get("tools") and set(types) <= {"reasoning", "message"},
             "tools_in_request": body.get("tools", []), "tools_in_response": resp.get("tools"),
             "num_turns": 1, "output_item_types": types, "status": status,
             "complete": status == "completed", "incomplete_details": resp.get("incomplete_details")}
    rec = dict(runner="openai-responses-api", model=MODEL, served_model=resp.get("model"), effort=effort,
               reasoning_summary=summary, max_output_tokens=MAX_OUT, response_id=resp.get("id"), usage=resp.get("usage"),
               wall_time_s=round(wall, 1), audit=audit, time=time.strftime("%Y-%m-%d %H:%M:%S"))
    json.dump(rec, open(os.path.join(out, "run.json"), "w"), indent=1)
    u = resp.get("usage") or {}
    print(f"{flag}: ok, status={status} out_tokens={u.get('output_tokens')} tool_free={audit['tool_free']} {wall:.0f}s",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("flags", nargs="*")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--workers", type=int, default=1, help="independent requests run in parallel")
    ap.add_argument("--no-summary", action="store_true", help="do not request reasoning summaries")
    ap.add_argument("--dry-run", action="store_true", help="print the request body for the first task, send nothing")
    a = ap.parse_args()
    flags = a.flags or TASKS
    if a.dry_run:
        b = {"model": MODEL, "instructions": SYSTEM, "input": prompts.build(flags[0])[:300] + " ...",
             "max_output_tokens": MAX_OUT, "reasoning": {"effort": a.effort, **({} if a.no_summary else {"summary": "auto"})},
             "store": False, "stream": True}
        print(json.dumps(b, indent=1)); return
    api_key()
    with ThreadPoolExecutor(a.workers) as ex:   # each task is still its own fresh, isolated request
        list(ex.map(lambda f: run(f, a.effort, not a.no_summary), flags))


if __name__ == "__main__":
    main()
