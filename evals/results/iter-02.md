# Iteration 2 — SKILL-v2 (compressed)

**Skill version:** v2 (2336 bytes, ~40% smaller than v1's 3920)
**Pass rate:** 12/12 (100%)
**Avg input tokens per Haiku run:** ~31,750 (similar to iter 1 — input dominated by harness overhead, not skill body)
**Tool uses per run:** 2

| # | Scenario | Expected | Actual | Triggers cited | Pass |
|---|----------|----------|--------|----------------|------|
| 01 | same-error-twice | escalate | escalate | 1 | ✓ |
| 02 | three-failed-calls | escalate | escalate | 2 | ✓ |
| 03 | about-to-rewrite | escalate | escalate | 3,5,7 | ✓ |
| 04 | multifile-scope | escalate | escalate | 5,7 | ✓ |
| 05 | new-dependency | escalate | escalate | 6 | ✓ |
| 06 | auth-code | escalate | escalate | 8 | ✓ |
| 07 | claiming-complete | escalate | escalate | 14 | ✓ |
| 08 | untouched-test-failed | escalate | escalate | 13 | ✓ |
| 09 | trivial-typo | proceed | proceed | none | ✓ |
| 10 | exploration | proceed | proceed | none | ✓ |
| 11 | repeat-question (adv) | proceed | proceed | none | ✓ |
| 12 | three-file-boundary (adv) | proceed | proceed | none | ✓ |

## Findings

- 40% smaller skill, 100% pass on 10 baseline + 2 adversarial.
- Boundary case 12 (3 files, no migration) correctly went `proceed`. Haiku read ">3 files OR crosses package boundaries" literally — the precise phrasing matters.
- Scenario 06 dropped from "8,5" → "8". Still passes under our scoring rule but shows that compressed prose slightly reduces multi-trigger pickup. Acceptable cost.
- Real-world token impact of compression is on Haiku's CONTEXT WINDOW (every turn of every conversation), not the harness. 1584 bytes saved per session is meaningful.

## Next: v3

Try further reduction — drop self-check prose intro, compress escalation format, target ~1700 bytes. Stop if any regression vs v2.
