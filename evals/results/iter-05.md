# Iteration 5 — SKILL-v4 (S12 fix)

**Skill version:** v4 (2933 bytes, +25% vs v2 / -25% vs v1)
**Decision pass rate:** 12/12 (100%)
**Format compliance:** 12/12 (100%)
**Diff vs v2:** added (a) literal-trigger default in DO NOT list, (b) "Near-misses" block with four concrete counter-examples.

| # | Scenario | Expected | v2 | v4 | Triggers cited (v4) | Notes |
|---|----------|----------|----|----|---------------------|-------|
| 01 | same-error-twice | escalate | escalate ✓ | escalate ✓ | 1 | clean |
| 02 | three-failed-calls | escalate | escalate ✓ | escalate ✓ | 1,4 | T1 acceptable per scenario notes |
| 03 | about-to-rewrite | escalate | escalate ✓ | escalate ✓ | 3,5,8 | T3 cited correctly |
| 04 | multifile-scope | escalate | escalate ✓ | escalate ✓ | 5 | clean |
| 05 | new-dependency | escalate | escalate ✓ | escalate ✓ | 6,8 | T6 cited (T8 over-cite, harmless) |
| 06 | auth-code | escalate | escalate ✓ | escalate ✓ | 8 | clean |
| 07 | claiming-complete | escalate | escalate ✓ | escalate ✓ | 13,14 | T14 cited |
| 08 | untouched-test-failed | escalate | escalate ✓ | escalate ✓ | 13 | clean |
| 09 | trivial-typo | proceed | proceed ✓ | proceed ✓ | none | clean |
| 10 | exploration | proceed | proceed ✓ | proceed ✓ | none | clean |
| 11 | repeat-question | proceed | proceed ✓ | proceed ✓ | none | clean |
| **12** | **three-file-boundary** | **proceed** | **escalate ✗** | **proceed ✓** | **none** | **regression fixed** |

## What changed v2 → v4

1. **DO NOT list** gained a literal-trigger default: *"Changes where no trigger above LITERALLY fires. Read each by number; if none match the change in front of you, proceed."* This counters the v2 "checklist bias" where Haiku reaches for ANY trigger to fire on neutral changes.
2. **New `## Near-misses` section** with four concrete counter-examples:
   - Exactly 3 files in one package = below T5
   - Routine column with default in non-shared schema ≠ T7
   - First occurrence of a test failure ≠ T1
   - Vague phrasing in your head ≠ T10 (T10 is about *user's* requirement being ambiguous)

The four near-misses target the actual failure mode observed in iter-04: Haiku invented ambiguity (T10-style) and mis-cited it as T5/T7/T8 on S12.

## What v4 costs

- **+597 bytes vs v2** (2336 → 2933). Still 25% smaller than v1.
- **~150 input tokens per turn** (over a 50-turn session: ~7,500 tokens).
- Worth it: the S12 false-positive is now structurally addressed, not just papered over.

## Verdict

**Lock in v4.** Better than v2 on the regression that motivated this iteration; identical on every other case; format discipline preserved.

Next: validate against real-codebase scenarios (sample-projects/flask-orders-api/) where Haiku actually reads code rather than synthetic prompts.
