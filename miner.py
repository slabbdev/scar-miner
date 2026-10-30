#!/usr/bin/env python3
# miner.py: implementation of the Rapid-Regret Miner formula from dev.to/gde Part 4
#   CandidateScar <=> (t(C_{k+1}) - t(C_k) <= 60 min) AND (Symbols(C_{k+1}) & Symbols(C_k) != empty)
# Run against a local clone; prints mined candidate pairs and a control sample
# (consecutive same-author pairs NOT selected by the formula) for hand labeling.
#
# Symbol extraction is a PROXY for AST symbols: identifiers (len>=4, minus common
# keywords) appearing on added/removed diff lines. Disclosed in the run log.
# Implementation choice: consumed pairs do not overlap (after mining (C_k, C_k+1) the
# scan resumes at C_k+2). An overlapping-pair reading of "consecutive commits" yields
# different candidate counts; disclosed so re-implementations can align.
#
# usage: python3 miner.py /path/to/repo [CONTROL_N]
import re, subprocess, sys, json
from datetime import datetime

REPO = sys.argv[1]
CONTROL_N = int(sys.argv[2]) if len(sys.argv) > 2 else 30
DT_MIN = 60

KEYWORDS = set("""this self const let var function return if else for while import from export class
interface type enum async await new throw try catch finally true false null undefined void of in
extends implements public private readonly static get set yield delete typeof instanceof default
with as do switch case break continue string number boolean object any unknown never promise
fix feat docs chore test release merge init update add remove refactor style perf revert
src lib test app main index page data util utils core http https www com""".split())

def run(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True).stdout

def identifiers(diff_text):
    ids = set()
    for line in diff_text.splitlines():
        if line.startswith("+") or line.startswith("-"):
            for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", line):
                if tok.lower() not in KEYWORDS:
                    ids.add(tok)
    return ids

# sequential (non-merge) commits, oldest first
log = run("log", "--no-merges", "--reverse", "--format=%H|%ai|%an|%s").strip().splitlines()
commits = []
for line in log:
    h, ts, author, subject = line.split("|", 3)
    t = datetime.fromisoformat(ts).timestamp()
    commits.append({"h": h, "t": t, "author": author, "subject": subject,
                    "ids": identifiers(run("show", "-U0", "--format=", h))})

def label_pair(a, b):
    return {"c_k": a["h"][:10], "c_k1": b["h"][:10], "author": a["author"],
            "dt_min": round((b["t"] - a["t"]) / 60, 1),
            "subj_k": a["subject"][:90], "subj_k1": b["subject"][:90],
            "overlap": sorted(a["ids"] & b["ids"])[:8]}

mined, control = [], []
i = 0
while i < len(commits) - 1:
    a, b = commits[i], commits[i + 1]
    dt = (b["t"] - a["t"]) / 60
    if a["author"] == b["author"] and dt <= DT_MIN:
        ov = a["ids"] & b["ids"]
        if ov:
            mined.append(label_pair(a, b))
            i += 2  # Randal's pairs are consecutive; consumed pair
            continue
    else:
        if a["author"] == b["author"] and len(control) < CONTROL_N:
            control.append(label_pair(a, b))
    i += 1

print(json.dumps({"mined": mined, "control": control,
                  "total_commits": len(commits)}, indent=1))
