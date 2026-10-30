#!/usr/bin/env python3
# omission.py: test Randal's Commission/Omission theorem signature on the 43-pair sample.
# Claim: Omission fixes are PURELY ADDITIVE, and they touch the same symbols C_k touched,
# but only on the + side. Metric: ADDITIVE-SAME-SYMBOL (ASS) = AddedIds(C_k+1) & AddedIds(C_k)
# != empty, computed on G1-selected pairs (13), against hand labels (4 TRUE, 3 PARTIAL, 6 FALSE).
import json, re, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
FIXV = re.compile(r"^(fix|hotfix|oops|revert|bug)\b", re.I)

def run(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True).stdout

def added_ids(h):
    ids = set()
    cur = None
    for line in run("show", "-U0", "--format=", h).splitlines():
        m = re.match(r"\+\+\+ b/(.*)", line)
        if m:
            cur = m.group(1); continue
        if line.startswith("@@") or line.startswith("---"):
            continue
        if line.startswith("+"):
            for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", line):
                ids.add(tok)
    return ids

sample = json.load(open("sample.json"))
labels = json.load(open("labels.json"))


sel = []
for idx, p in enumerate(sample):
    fix = bool(FIXV.match(p["subj_k1"]))
    if not fix:
        continue
    a_add = added_ids(p["c_k"])
    b_add = added_ids(p["c_k1"])
    ass = bool(a_add & b_add)
    label = labels[idx]["label"]
    sel.append((idx, label, ass, p["subj_k"][:40], p["subj_k1"][:55]))

print(f"{'idx':>4} {'label':>8} {'ASS':>5}  pair")
for idx, label, ass, sk, sk1 in sel:
    print(f"S{idx:02d} {label:>8} {str(ass):>5}  {sk} ==> {sk1}")

from collections import Counter
c = Counter(label for _, label, ass, _, _ in sel if ass)
print("\nASS=true by label:", dict(c))
t = [x for x in sel if x[1] == "TRUE"]
f = [x for x in sel if x[1] == "FALSE"]
print(f"TRUE with ASS: {sum(1 for x in t if x[2])}/{len(t)}   FALSE with ASS: {sum(1 for x in f if x[2])}/{len(f)}")
