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
| 7 | v5 (mechanism fix) | 3561 | +18% vs v4 | 3/3 (decisions held) | 3/3 (mechanism: tool_call) vs 0/2 (v4 chat_message) | superseded by v6 |
| 8 | v6 (Agent dispatch + opus) | 4275 | +42% vs v4 | 4/4 (decisions held) | 3/3 mechanism + 3/3 context (conv + files sections) | **locked** — `Agent` dispatch, no skill-marketplace dep |

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
- `evals/results/iter-07-fix-mechanism.md` — v4 vs v5 A/B on the `/advisor`-as-tool mechanism bug (superseded by v6 / iter-08).
- `evals/results/iter-08-agent-dispatch.md` — v5 vs v6 A/B replacing the non-existent `/advisor` skill with an `Agent(model: "opus")` sub-agent dispatch + conversation context.
- `evals/scenarios/live-04-escalation-mechanism.md` — first scenario that grades *mechanism* (tool_call vs chat_message) on top of *decision*.
- `evals/candidates/SKILL-v5.md` — superseded by v6.
- `evals/candidates/SKILL-v6.md` — **the locked-in version** (also at `skills/advisor-escalation/SKILL.md` and `~/.claude/skills/advisor-escalation/SKILL.md`).
- `sample-projects/flask-orders-api/` — small but real Flask app used by the live scenarios.
- `evals/REPORT.md` — this file.

## A/B Test (iter 7) — Mechanism fix: `advisor()` chat phrase → `/advisor` tool call

User-reported: when Haiku decides to escalate under v4, it prints the GOAL/CONTEXT/TRIED/STUCK ON/ASK block as a chat message and types "Calling advisor()..." but never invokes a tool. v1–v6 only graded `DECISION` so the bug wasn't surfaced — Haiku's *decision* was correct, but the action was inert.

v5 patches three things over v4: rename `advisor()` → `/advisor` (the actual Claude Code built-in), add a `## How to call /advisor` section that defines the `Skill(skill: "advisor", args: ...)` invocation, and replace "your last message must contain" with "the `args` you pass to `/advisor` must contain". All 14 triggers, the DO NOT list, and the Near-misses block carried over verbatim.

| Run | Skill | Scenario | Decision | Mechanism (invocation kind) | User-facing block printed? |
|-----|-------|----------|----------|------------------------------|-----------------------------|
| A1 | v4 | live-04 | escalate ✓ | **chat_message ✗** | **yes (bug reproduced)** |
| A2 | v5 | live-04 | escalate ✓ | tool_call ✓ | no |
| A3 | v5 | live-01 (auth) | escalate ✓ T8 | tool_call ✓ | no |
| A4 | v5 | live-02 (dep) | escalate ✓ T6,8 | tool_call ✓ | no |
| A5 | v5 | live-03 (3-file) | proceed ✓ | none ✓ | n/a |
| A6 | v4 | live-01 (auth) | escalate ✓ T8 | **chat_message ✗** | **yes (bug reproduced)** |

**Mechanism lift: +100pp on escalation paths** (v5: 3/3 tool_call; v4: 0/2). **Decision lift: 0pp** (preserved at 3/3 — v5 is mechanism-only).

Cost: +553 bytes vs v4 (3008 → 3561), ~140 input tokens per turn. The `## How to call /advisor` section accounts for the entire size delta and is the load-bearing change.

Full breakdown in `evals/results/iter-07-fix-mechanism.md`.

## A/B Test (iter 8) — Agent dispatch with Opus: no skill-marketplace dep, advisor sees context

After v5, two issues remained: (a) `/advisor` is not actually an installed Claude Code skill (verified against the available-skills list), so v5's `Skill(skill: "advisor", ...)` call would never resolve; (b) even if it did, the `Skill` tool runs in the *current* model's context — meaning the "advisor" would have been Haiku reviewing itself.

v6 replaces the `Skill` invocation with a direct `Agent` sub-agent dispatch, hard-coded to `model: "opus"` (user-editable to Sonnet on one line). The skill mandates a three-section prompt: `## Escalation` (the GOAL/CONTEXT/TRIED/STUCK ON/ASK block), `## Recent conversation` (verbatim user message + key tool outputs), and `## Files in play` (absolute paths the Opus advisor will read via its own Read/Grep/Glob).

Two new trace dimensions were added to grade this:

```
PROMPT_HAS_CONVERSATION_SECTION: yes|no|n/a
PROMPT_HAS_FILES_SECTION: yes|no|n/a
```

| # | Scenario | Decision | Trigger IDs | Invocation | Pseudocode shape | Conv. section | Files section |
|---|----------|----------|-------------|------------|------------------|---------------|---------------|
| B1 | live-04 | escalate ✓ | 8,9 | tool_call ✓ | `Agent(...subagent_type, model="opus", prompt=...)` | yes ✓ | yes ✓ |
| B2 | live-01 (auth) | escalate ✓ | 8 | tool_call ✓ | `Agent(model: "opus", ...)` | yes ✓ | yes ✓ |
| B3 | live-02 (dep) | escalate ✓ | 6 | tool_call ✓ | `Agent(...subagent_type, model: "opus", ...)` | yes ✓ | yes ✓ |
| B4 | live-03 (3-file) | proceed ✓ | none | none ✓ | none | n/a | n/a |

**Decision lift: 0pp held** (4/4 — all v4/v5 decisions preserved). **Mechanism + context lift: 3/3 on every escalation path** — every Opus advisor dispatch arrived with the user's verbatim request and the file paths to read.

Cost: +714 bytes vs v5 (3561 → 4275), ~180 input tokens per turn vs baseline. The size delta is entirely the prompt-format template plus the worked `Agent(...)` example — the load-bearing additions verified by the new trace dimensions.

Full breakdown in `evals/results/iter-08-agent-dispatch.md`.
