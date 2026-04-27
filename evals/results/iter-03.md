# Iteration 3 — SKILL-v3 (further compressed)

**Skill version:** v3 (2176 bytes, ~7% smaller than v2, ~44% smaller than v1)
**Decision pass rate:** 12/12 (100%)
**Format compliance:** 10/12 (83%) — REGRESSION vs v2 (12/12)
**Avg input tokens per Haiku run:** ~31,750

| # | Scenario | Decision | Triggers | Format clean? |
|---|----------|----------|----------|---------------|
| 01 | same-error-twice | escalate | 1 | ✓ |
| 02 | three-failed-calls | escalate | 2 | ✗ preamble: "The advisor-escalation skill is not available. Let me apply the MUST-Triggers manually..." |
| 03 | about-to-rewrite | escalate | 3,5,7 | ✓ |
| 04 | multifile-scope | escalate | 5,7 | ✓ |
| 05 | new-dependency | escalate | 6 | ✓ |
| 06 | auth-code | escalate | 8 | ✓ |
| 07 | claiming-complete | escalate | 14 | ✓ |
| 08 | untouched-test-failed | escalate | 13 | ✗ preamble: "Based on the SKILL-v3.md rules..." |
| 09 | trivial-typo | proceed | none | ✓ |
| 10 | exploration | proceed | none | ✓ |
| 11 | repeat-question | proceed | none | ✓ |
| 12 | three-file-boundary | proceed | none | ✓ |

## Findings

- Decisions: 12/12 — semantic behaviour preserved.
- Format: 2 violations. Haiku wrote chain-of-thought preamble before the strict 5-line trace.
- Likely cause: v3 collapsed the visually distinct `## Self-Check` section into inline prose. The visual scaffolding seems to anchor Haiku into "format mode" — removing it costs format discipline.
- Diminishing returns: v3 saved only 160 bytes vs v2 for a measurable behaviour cost.

## Verdict

**Reject v3. Lock in v2.** v2 is the optimum on this test set:
- 12/12 decisions
- 12/12 format compliance
- 40% smaller than baseline
