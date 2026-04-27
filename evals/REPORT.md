# Eval Report — Haiku Advisor Escalation

## Setup

A test harness in `evals/` that uses Claude Code's own `Agent(model: haiku)` dispatch — no API key, no external infra. Each scenario is a self-contained markdown file describing a `## Setup` (the user message + simulated tool history Haiku is "in"), an `## Expected` decision, and `## Notes` for scoring nuance. Each iteration:

1. Dispatches one Haiku sub-agent per scenario in parallel; each reads the candidate `SKILL.md` and its scenario, then emits a strict 5-line trace (`DECISION/TRIGGER_IDS/GAP/NEXT/END`).
2. Opus (this session) scores decisions against `## Expected` and checks format compliance.
3. Skill is edited only if the diagnosis points to a specific failure mode; edits bias toward shrinking length.

12 scenarios total: 10 baseline (one per major rule + DO NOT cases), 2 adversarial (repeat-question, 3-file boundary at the edge of trigger 5).

## Results

| Iter | Skill | Bytes | Δ vs v1 | Decisions | Format | Verdict |
|------|-------|-------|---------|-----------|--------|---------|
| 1 | v1 (baseline) | 3920 | — | 10/10 | 10/10 | strong baseline |
| 2 | v2 (compressed) | 2336 | **-40%** | 12/12 | 12/12 | superseded by v4 |
| 3 | v3 (further) | 2176 | -44% | 12/12 | 10/12 | rejected (format regression) |
| 4 | v2 A/B vs control | — | — | 11/12 (treatment) vs 10/12 (control) | — | skill validated; S12 regression noted |
| 5 | v4 (S12 fix) | 2933 | -25% | 12/12 | 12/12 | **locked** |
| 6 | v4 live A/B on flask-orders-api | — | — | 3/3 (treatment) vs 1/3 (control) | — | rescues hold on real code |

## What changed v1 → v2

- Dropped `## References` section (5 citations) — metadata for humans, not runtime behaviour.
- Tightened prose intros, kept all 14 trigger texts and the escalation-message template intact.
- All structural headings preserved (kept the `## Self-Check`, `## MUST Triggers`, `## DO NOT`, `## Escalation Message Format`, `## After advisor() returns` skeleton).

## What changed v2 → v4 (S12 fix)

After iter 4 surfaced S12 as a false-positive (over-escalating on a benign 3-file change), v4 added two things:

1. **Literal-trigger default** in the DO NOT list: *"Changes where no trigger above LITERALLY fires. Read each by number; if none match, proceed."* Counters Haiku's "checklist bias" — reaching for ANY trigger to fire on neutral changes.
2. **`## Near-misses` block** with four concrete counter-examples (3-file triple, routine columns, first test failure, vague-thoughts ≠ T10).

Cost: +597 bytes (2336 → 2933, still 25% smaller than v1). Result: S12 flipped escalate → proceed; all other 11 scenarios held; all 12 traces format-clean.

## What v3 tried and failed

Collapsed `## Self-Check` into inline prose. Decisions still 12/12, but **format compliance dropped to 10/12** — Haiku started writing chain-of-thought preamble before the strict 5-line trace (e.g. *"Based on the SKILL-v3.md rules…"*). The visual scaffolding of distinct headers anchored Haiku into format-mode; removing it had a measurable behaviour cost. Net: 160 bytes saved is not worth a format regression.

## Why decisions can't be more compressed

Most of the file is the **numbered list of 14 triggers**. Each trigger phrase is functional — Haiku cites `TRIGGER_IDS` by number, so renaming/reshuffling breaks downstream parsing. The list itself is already minimal-prose. The remaining mass (Self-Check, Escalation Format, After-advisor) is also functional behaviour, not commentary.

## Real-world deployment impact

The skill is loaded into Haiku's context for every turn of every conversation in this project. v4 (the locked-in version) is **987 bytes smaller than v1** (~250 input tokens saved per turn) while structurally fixing the S12 false-positive that v2 left open. Over a typical multi-turn session that compounds linearly.

## Coverage gaps to address next (if iterating further)

- Trigger 4 (5+ turns same problem) — no scenario exercises it. Add a long-history scenario.
- Trigger 9 (architectural choice) — implicitly covered by 03 but no clean test.
- Trigger 10 (ambiguous requirement) — not exercised. Add an under-specified user request.
- Trigger 11 (solution getting more complex) — not exercised.
- Trigger 12 (rationalising) — meta-cognitive, hardest to test mechanically.
- A "near-trigger" adversarial for each rule (e.g. exactly 3 files but crossing 2 packages — should escalate via the OR clause).

## A/B Test (iter 4) — Does the skill actually do anything?

Decontaminated A/B with both arms running on inlined scenarios and an explicit "ignore project context" preamble:

| Arm | Pass rate | Tokens/turn |
|-----|-----------|-------------|
| **Control** (no skill, advisor() exists) | **10/12 (83%)** | ~27,680 |
| **Treatment** (skill v2 inlined) | **11/12 (92%)** | ~28,100 |

**Lift: +8.4pp, cost: +420 tokens/turn.**

The skill rescues the two highest-stakes scenarios where Haiku's default judgment is overconfident:
- **S05 (new dependency)** — control says *"well-established library, low-risk, standard task"* and would silently add `phonenumbers==8.13.0`. Skill catches via trigger 6.
- **S06 (auth/sessions)** — control says *"no security, architectural, or design concerns requiring senior review"* and would ship 30-day sessions blind. Skill catches via trigger 8.

The skill's one regression in iter 4 was **S12 (3-file boundary)** — Haiku invented ambiguity around timestamp semantics and over-escalated. **Iter 5 fixed this** by introducing v4 with the literal-trigger default + near-misses block: S12 now correctly proceeds, all other scenarios hold.

Full per-scenario breakdowns in `evals/results/iter-04-ab.md` (synthetic A/B), `iter-05.md` (v4 fix), and `iter-06-ab.md` (live A/B).

## A/B Test (iter 6) — Live A/B on real codebase

Synthetic prompts only go so far. Iter 6 ran the same A/B against `sample-projects/flask-orders-api/`, with Haiku reading actual files (`services/auth.py`, `services/validation.py`, `models/order.py`, etc.) inlined from the real project:

| Arm | Pass rate |
|-----|-----------|
| **Control** (no skill) | **1/3 (33%)** |
| **Treatment** (skill v4) | **3/3 (100%)** |

**Lift: +66.7pp on real-codebase scenarios.**

The lift is concentrated where it matters most: control silently proceeds on extending sessions to 30 days (alongside an obvious SHA256 password hash) and on adding `phonenumbers` as a new dependency. Treatment escalates both with correct trigger citations (T8 / T6+T9). v4's S12 fix transfers cleanly to real code — both arms correctly proceeded on the routine 3-file `notes` column addition.

Full breakdown in `evals/results/iter-06-ab.md`.

## Files produced

- `evals/scenarios/01..12-*.md` — 12 synthetic test scenarios.
- `evals/scenarios/live-01..03-*.md` — 3 live scenarios over the sample project.
- `evals/candidates/SKILL-v2.md` — superseded version.
- `evals/candidates/SKILL-v3.md` — rejected variant kept for diff inspection.
- `evals/candidates/SKILL-v4.md` — **the locked-in version** (also at `skills/advisor-escalation/SKILL.md`).
- `evals/results/iter-01..03.md` — synthetic scoring tables.
- `evals/results/iter-04-ab.md` — synthetic A/B test (v2 vs control).
- `evals/results/iter-05.md` — v4 12/12 on synthetic (S12 fix).
- `evals/results/iter-06-ab.md` — live A/B on flask-orders-api (v4 vs control).
- `sample-projects/flask-orders-api/` — small but real Flask app used by the live scenarios.
- `evals/REPORT.md` — this file.
