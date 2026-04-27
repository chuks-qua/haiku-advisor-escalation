# Iteration 1 — baseline SKILL.md

**Skill version:** original (88 lines, ~3270 chars)
**Pass rate:** 10/10 (100%)
**Avg input tokens per Haiku run:** ~30,200
**Tool uses per run:** 2 (Read SKILL + Read scenario)

| # | Scenario | Expected | Actual decision | Triggers cited | Pass |
|---|----------|----------|-----------------|----------------|------|
| 01 | same-error-twice | escalate | escalate | 1 | ✓ |
| 02 | three-failed-calls | escalate | escalate | 2 | ✓ |
| 03 | about-to-rewrite | escalate | escalate | 3,5,7 | ✓ |
| 04 | multifile-scope | escalate | escalate | 5,7 | ✓ |
| 05 | new-dependency | escalate | escalate | 6 | ✓ |
| 06 | auth-code | escalate | escalate | 8,5 | ✓ |
| 07 | claiming-complete | escalate | escalate | 14 | ✓ |
| 08 | untouched-test-failed | escalate | escalate | 13 | ✓ |
| 09 | trivial-typo | proceed | proceed | none | ✓ |
| 10 | exploration | proceed | proceed | none | ✓ |

## Findings

- Skill is directionally correct — Haiku reliably picks the right trigger and reliably abstains on excluded cases.
- Multi-trigger detection (e.g. 03 fires 3,5,7; 06 fires 8,5) shows Haiku is reading the rule list, not just matching one keyword.
- GAP/NEXT lines are concise; format compliance was 100%.

## Improvement axis for iter 2

- Skill is verbose. References section, prose intros, and self-check rationale add tokens to every invocation without behavioural lift.
- Hypothesis: ~50% size reduction is achievable without regression. Validate by re-running same 10 scenarios + 2 adversarial cases on a compressed skill.
