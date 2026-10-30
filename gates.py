#!/usr/bin/env python3
# gates.py: ablation of Randal's proposed gates on the hand-labeled 43-pair sample
# G1: fix-verb gate on C_k+1 subject (already measured, ~40%)
# G2: path exclusion (CHANGELOG*, *.md, package.json removed from overlap)
# G3: hunk-polarity inversion: AddedLines(C_k) intersect DeletedLines(C_k+1) != empty
# Combos: G1, G3, G2+G3, G1+G2+G3. Precision measured on the labeled sample;
# recall checked (do the 4 TRUE pairs survive?); selection rate on the full 171.
import re, subprocess, sys, json

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
FIXV = re.compile(r"^(fix|hotfix|oops|revert|bug)\b", re.I)
EXCLUDE = re.compile(r"(^|/)(CHANGELOG.*|.*\.md|package\.json)$", re.I)

def run(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout

def diff_lines(h):
    """return (added_set, deleted_set, added_identifiers_by_file) with excluded paths dropped"""
    text = run("show", "-U0", "--format=", h)
    added, deleted, ids = set(), set(), set()
    cur_path = None
    for line in text.splitlines():
        m = re.match(r"\+\+\+ b/(.*)", line)
        if m:
            cur_path = m.group(1); continue
        if line.startswith("@@") or line.startswith("---"):
            continue
        excl = bool(cur_path) and bool(EXCLUDE.match(cur_path))
        if line.startswith("+"):
            body = line[1:].strip()
            if body and not excl:
                added.add(body)
            if not excl:
                for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", line):
                    ids.add(tok)
        elif line.startswith("-"):
            body = line[1:].strip()
            if body and not excl:
                deleted.add(body)
            if not excl:
                for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", line):
                    ids.add(tok)
    return added, deleted, ids

sample = json.load(open("sample.json"))
results = []
for p in sample:
    a_add, _, a_ids = diff_lines(p["c_k"])
    _, d_del, b_ids = diff_lines(p["c_k1"])
    fix = bool(FIXV.match(p["subj_k1"]))
    g2 = bool(a_ids & b_ids)                      # overlap after path exclusion
    g3 = bool(a_add & d_del)                      # polarity inversion
    results.append({"c_k": p["c_k"], "label_true": None, "fix": fix,
                    "g2": g2, "g3": g3})

# attach hand labels from labels.json (index-aligned with sample.json)
labels = json.load(open("labels.json"))
for idx, r in enumerate(results):
    r["label_true"] = labels[idx]["label"] == "TRUE"
    r["label_partial"] = labels[idx]["label"] == "PARTIAL"

def evaluate(name, keep):
    sel = [r for r, k in zip(results, keep) if k]
    t = sum(1 for r in sel if r["label_true"])
    tp = sum(1 for r in sel if r["label_true"] or r["label_partial"])
    recall = all(k for r, k in zip(results, keep) if r["label_true"])
    print(f"{name:>16}: selected {len(sel):>2}/43  strict-true {t}  strict+partial {tp}  "
          f"precision {t/len(sel)*100 if sel else 0:.0f}%  "
          f"(+partial {tp/len(sel)*100 if sel else 0:.0f}%)  true-recall-kept={recall}")

evaluate("no gate", [True]*len(results))
evaluate("G1 fix-verb", [r["fix"] for r in results])
evaluate("G3 polarity", [r["g3"] for r in results])
evaluate("G2+G3", [r["g2"] and r["g3"] for r in results])
evaluate("G1+G3", [r["fix"] and r["g3"] for r in results])
evaluate("G1+G2+G3", [r["fix"] and r["g2"] and r["g3"] for r in results])
print()
for i, r in enumerate(results):
    if r["label_true"] or r["label_partial"]:
        print(f"S{i:02d} true={r['label_true']} partial={r['label_partial']} fix={r['fix']} g2={r['g2']} g3={r['g3']}")
