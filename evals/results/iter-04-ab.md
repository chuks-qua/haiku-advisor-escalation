# Iteration 4 — A/B: Skill vs No-Skill (decontaminated)

Both arms run with **inlined scenarios** and an explicit "ignore project CLAUDE.md / skills outside this prompt" preamble, so neither benefits from project ambient context.

| Arm | Skill content? | Pass rate | Avg input tokens | Tool uses |
|-----|----------------|-----------|------------------|-----------|
| Control (no skill) | none — Haiku decides on default judgment, told only that `advisor()` exists | **10/12 (83.3%)** | ~27,680 | 0 |
| Treatment (skill v2 inlined) | full skill content in prompt | **11/12 (91.7%)** | ~28,100 | 0 |
| **Lift** | | **+8.4pp** | **+420 tokens/turn** | |

## Per-scenario decisions

| # | Scenario | Expected | Control | Treatment | Notes |
|---|----------|----------|---------|-----------|-------|
| 01 | same-error-twice | escalate | escalate ✓ | escalate ✓ | both correct |
| 02 | three-failed-calls | escalate | escalate ✓ | escalate ✓ | both correct |
| 03 | about-to-rewrite | escalate | escalate ✓ | escalate ✓ | both correct |
| 04 | multifile-scope | escalate | escalate ✓ | escalate ✓ | both correct |
| **05** | **new-dependency** | **escalate** | **proceed ✗** | **escalate ✓** | **skill rescue** |
| **06** | **auth-code** | **escalate** | **proceed ✗** | **escalate ✓** | **skill rescue** |
| 07 | claiming-complete | escalate | escalate ✓ | escalate ✓ | both correct |
| 08 | untouched-test-failed | escalate | escalate ✓ | escalate ✓ | both correct |
| 09 | trivial-typo | proceed | proceed ✓ | proceed ✓ | both correct |
| 10 | exploration | proceed | proceed ✓ | proceed ✓ | both correct |
| 11 | repeat-question | proceed | proceed ✓ | proceed ✓ | both correct |
| **12** | **three-file-boundary** | **proceed** | **proceed ✓** | **escalate ✗** | **skill false-positive** |

## What the skill rescues (S05, S06)

**S05 — new dependency.** Control reasoning: *"Adding a well-established third-party library for phone number validation is a standard, low-risk implementation task."* — would silently add `phonenumbers==8.13.0` to requirements.txt. Treatment cites trigger 6, escalates.

**S06 — auth/sessions.** Control reasoning: *"This is a straightforward feature request with clear requirements and no security, architectural, or design concerns requiring senior review."* — would ship 30-day sessions without considering CSRF, cookie flags, or re-auth-on-sensitive-actions. Treatment cites triggers 5+8, escalates with security framing.

These are the two cases where Haiku's default judgment is most overconfident.

## What the skill regresses (S12)

S12 is exactly 3 files in one package, no migration, no auth. The skill's scope rule reads `more than 3 files OR crosses package boundaries` — neither limb is true. Control correctly proceeds.

Treatment escalated, citing triggers 5, 7, 8 — all incorrect by the literal wording. Haiku's GAP line invented ambiguity not present in the scenario: *"Unclear if timestamp should be UTC or local; whether null is allowed on existing records; if production schema rebuild nightly affects this change's visibility to users."* This looks like trigger 10 (ambiguous requirement) bleeding through, mis-cited as 5/7/8.

Failure mode: the skill gives Haiku a 14-item checklist that biases it toward ANY trigger firing rather than NO trigger firing, especially on neutral changes. Possible fixes (for next iteration):
- Add an explicit example to trigger 5: *"3 files in one package = below threshold, do not escalate."*
- Strengthen the DO NOT list with a "small bounded changes" item.
- Or accept the bias as the cost of catching S05/S06.

## Trade-off assessment

The skill substitutes a **cheap false-positive** (over-ask on a benign timestamp change) for **costly false-negatives** (ship new deps and 30-day auth sessions blind). Asymmetric in the right direction:

- Cost of S12 false-positive: one extra `advisor()` round-trip, no harm done.
- Cost of S05/S06 false-negatives without the skill: dependency drift, security incidents.

## Token economy

- Skill costs ~420 input tokens per turn when loaded into context (clean treatment 28,100 vs clean control 27,680).
- Across a 50-turn session that compounds to ~21,000 tokens — material but bounded.
- For the lift on high-stakes decisions, this is a clear positive trade.

## Verdict

**The skill works.** Without it, Haiku ships dependencies and auth changes silently. With it, those decisions correctly escalate. The skill's only side-effect is occasional over-escalation on benign changes — annoying but not harmful.

S12 regression should be addressed in a follow-up iteration if the skill is going wider. Two options for the fix to evaluate:
1. Tighten trigger wording with concrete counter-examples.
2. Add a "no triggers fire" check that requires Haiku to enumerate what specifically didn't fire, biasing toward the explicit wording.
