# scar-miner

A precision test of the **Rapid-Regret Miner** formula published in Randal Schwartz's Synthetic Scars series, Part 4 ("Giving AI Pain"):
`CandidateScar <=> (same author, consecutive commits, delta-t <= 60 min) AND (non-empty symbol overlap)`.

The formula was implemented as published, run against a public repository (`tinyjsapp`, 445 non-merge commits), and the candidate pairs were hand-labeled to measure how many mined pairs are true trap-to-reflex regrets.

## Results (43-pair hand-labeled stratified sample)

| Gate | Selected | True kept | Precision |
|---|---|---|---|
| no gate | 43/43 | 4/4 | 9% strict (16% with partials) |
| G1 fix-verb on `C_k+1` | 13/43 | 4/4 | 31% (54%) |
| G3 hunk-polarity inversion alone | 7/43 | 2/4 | 29% |
| G1 + G3 | 2/43 | 2/4 | 100% (n = 2) |

Findings:

- **Recall is clean**: every true regret in the sample was captured by the raw formula. The bottleneck is precision.
- **Misses have a shape**: development bursts (`feat: X` then `feat: Y`) and release/changelog commits riding shared symbols.
- **Hunk-polarity inversion is a Stage 2 confirmer, not a Stage 1 filter**: it drops half the true regrets (omission fixes are purely additive, they add the missing artifact instead of deleting what `C_k` wrote), which violates the Stage 1 high-recall requirement. Passing it is strong evidence a pair is a true commission regret (2-for-2 in sample).
- The funnel that survives measurement: **G1 filters, G3 confirms, a pair-level auditor adjudicates.**

## Files

- `miner.py`: the formula as published (identifier proxy for AST symbols, disclosed; non-overlapping pair consumption, disclosed). Prints mined candidate pairs plus an unlabeled control sample.
- `sample.json`: the 43 hand-labeled pairs (every 4th mined pair).
- `labels.json`: the hand labels, index-aligned with `sample.json`.
- `gates.py`: the gate ablation (G1 fix-verb, G2 path exclusion, G3 hunk-polarity).
- `omission.py`: test of the Commission/Omission theorem (omission fixes are purely additive and touch the same symbols; confirmed on 4/4 true regrets, but the additive-same-symbol feature does not separate true from false on a bursty repo: 12/13 pass including 6/6 false).
- `RUN-LOG.md`: full protocol, verdicts, honest limits.

## Reproduce

```bash
python3 miner.py /path/to/local/clone
# label the printed pairs (or reuse labels.json for the original sample)
python3 gates.py /path/to/local/clone
python3 omission.py /path/to/local/clone
```

## Honest limits

One repository, one labeler (who had audited this codebase before, so ground truth was known: bias disclosed), identifier proxy instead of a true AST parse, message-level labeling with diff inspection on ambiguous cases, stratified every-4th sampling. The numbers move with a real AST parser, commit-type pre-filtering (drop docs/CI/changelog commits), a second labeler, and different repositories. That is the point of shipping the protocol.

## Attribution

Formula: Randal Schwartz, Synthetic Scars Part 4 (dev.to/gde). Repository: `tinyjsapp` by Tarwin Stroh-Spijer. Labels and scripts: slabb (slabb.dev). MIT license.
