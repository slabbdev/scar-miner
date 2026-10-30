# RUN-LOG: Rapid-Regret Miner precision test (28-29 Oct 2026)

Formula under test (Randal Part 4, dev.to/gde): CandidateScar <=> (same author, consecutive commits, delta-t <= 60 min) AND (non-empty AST symbol overlap).

Repo: tinyjsapp (public Electron/TypeScript app, 445 non-merge commits, bursty multi-platform history). Chosen because public, real human history, and the labeler knows the codebase from a prior security audit (bias disclosed).

Symbol extraction: IDENTIFIER PROXY, not a true AST parse: identifiers (len >= 4, minus keyword list) appearing on added/removed diff lines of each commit. Known to over-match generic tokens (CHANGELOG, TODO, html, download...).

Selection: 171 mined candidate pairs; hand-labeled stratified sample of 43 (every 4th); plus 30 un-mined same-author consecutive pairs collected as an unlabeled control.

## Labels (43 pairs, single labeler)
- TRUE: C_k+1 corrects what C_k itself just shipped. Count: 4 (9.3%).
  Examples: feat Vite templates -> fix backend/tsconfig.json in the Vite scaffolds; feat(windows) drag handoff -> fix(windows) DoDragDrop watchdog; feat edit menus -> fix(linux) stock actions replaced by editing commands; feat windowless tray -> fix windowless review fixes.
- PARTIAL: correction in the same subsystem, but the flaw predates C_k (misattribution). Count: 3 (16.3% cumulative).
- FALSE: forward progress riding the same symbols: feature waves (feat: X then feat: Y), docs, changelogs, releases, CI. Count: 36.

## Signals
- Recall looks fine: all 4 true regrets in the sample were captured by the formula.
- Precision is the bottleneck: 9.3% strict, 16.3% with partials.
- A fix-verb gate on C_k+1 (subject starts with fix/hotfix) lifted sample precision to 4/10 = 40%.
- Data artifact: 3 pairs with negative delta-t (rebased author dates) in the full 171; the formula assumes monotone timestamps.

## Honest limits
One repo, one labeler (who audited this codebase before), identifier proxy instead of true AST, message-level labeling with diff inspection only for ambiguous cases. The protocol, script (miner.py), and labeled sample (sample.json) are public in this directory; the number moves with a real AST parser, commit-type pre-filtering (drop docs/CI/changelog), and a second labeler.

## Gate ablation (30/10, Randal 3jfph proposed gates), same 43-pair labeled sample
- G1 fix-verb (C_k+1 subject starts fix/hotfix/oops/revert/bug): selected 13/43, 4/4 TRUE kept, precision 31% strict / 54% with partials. Stage-1 safe.
- G3 hunk-polarity inversion (AddedLines(C_k) ∩ DeletedLines(C_k+1) ≠ ∅): selected 7/43 but only 2/4 TRUE kept (S01 and S04 fail: their fixes ADD the correct artifact rather than delete C_k's lines). As a Stage-1 filter it breaks recall, which violates the funnel criterion (Stage 1 must not drop true regrets). As a Stage-2 confirmation signal: 2-for-2 strict-TRUE in the sample (anecdote, not a rate).
- G2 path exclusion (CHANGELOG*, *.md, package.json dropped from overlap): no measurable change on this sample (the noise pairs it targets were already failing G3); should matter on noisier repos.
- Funnel conclusion: G1 filters (Stage 1), G3 confirms (Stage 2), the auditor adjudicates.
Script: scar-miner/gates.py. Labels: hand-labeled sample of 43, single labeler, disclosed.

## Omission signature test (30/10, after Randal 3jgal Commission/Omission theorem)
Randal's theorem: G3 sees only Errors of Commission (deletions/repairs); Errors of Omission (missing companion artifact) fix PURELY ADDITIVELY, invisible to polarity.
- Theorem VERIFIED on sample: 4/4 TRUE regrets are additive-only fixes (S01 tsconfig, S04 watchdog, S29 editing commands, S42 review fixes).
- Derived feature tested: ASS (Additive-Same-Symbol: AddedIds(C_k+1) ∩ AddedIds(C_k) ≠ ∅) on the 13 fix-verb pairs. Result: 12/13 pass, including 6/6 FALSE. No lift: on a bursty repo, same-hour fixes share added symbols whether or not they are regrets. The separator stays semantic (fix-verb to the auditor, auditor reads the diff).
- Mapping: Commission = the class structural checks catch (sealed verdict contradicting inputs); Omission = the class only COUNTING catches (outcomes ≤ attempts, fetches_served vs receipts_held). The chain cannot see absence, it can only count it. Same two-species taxonomy, journal-side and miner-side.
Script: scar-miner/omission.py.
