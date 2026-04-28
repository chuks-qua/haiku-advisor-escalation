# Iteration 7 — Mechanism fix (v4 → v5): `/advisor` as tool, not chat phrase

## The bug

User-reported screenshot: when Haiku decides to escalate, it prints the GOAL/CONTEXT/TRIED/STUCK ON/ASK block as a user-facing message and types "Calling advisor()..." but never actually invokes a tool. The escalation is decision-correct but mechanically inert — `advisor()` was never wired to a real tool, and the v4 prompt told Haiku "your last message must contain" the block, which Haiku interprets as user-facing text.

The existing harness (iters 1–6) only graded `DECISION`. It would never have caught this, because Haiku's *decision* in the screenshot was correct — the failure was in the action that should have followed.

## The fix (v5)

Surgical patch over v4 (3008 → 3561 bytes, +18%):

1. **`advisor()` → `/advisor`** throughout — matches the actual Claude Code built-in slash command.
2. **New `## How to call /advisor` section** at the top defining the operational mechanism: invoke the `Skill` tool with `skill: "advisor"`, the GOAL/CONTEXT block goes in `args` not chat, do not type "Calling /advisor..." and stop, surface "skill not found" to the user instead of improvising.
3. **"your last message must contain" → "the `args` you pass to `/advisor` must contain"** — kills the user-facing-text framing.
4. **No model in the skill.** `/advisor` is a Claude Code built-in; the user owns advisor-model selection via Claude Code settings. The skill stays portable across model configs.

All 14 triggers, the DO NOT list, and the Near-misses block are preserved verbatim — v4's decision-correctness is what we need to keep.

## Test design

Two failure modes, two A/B questions:

- **Mechanism:** when Haiku escalates, does it (a) invoke `/advisor` as a tool call, or (b) print the GOAL/CONTEXT block as user-facing text? — the screenshot bug.
- **Decision:** does the patch break v4's 3/3 live decision results?

New scenario `live-04-escalation-mechanism.md` reuses the live-01 setup (extend session) and asks Haiku to describe its single next action via a 6-line trace:

```
DECISION:
TRIGGER_IDS:
INVOCATION_KIND: tool_call|chat_message|none
TOOL_CALL_PSEUDOCODE:
USER_FACING_TEXT: ... or "GOAL_BLOCK_PRINTED" if the block would be printed as chat
END
```

Six parallel Haiku sub-agents, all decontaminated (explicit "ignore CLAUDE.md / global skills"):

| Run | Skill | Scenario | Tests |
|-----|-------|----------|-------|
| A1 | v4 | live-04 | mechanism (control) |
| A2 | v5 | live-04 | mechanism (treatment) |
| A3 | v5 | live-01 (auth) | decision + mechanism |
| A4 | v5 | live-02 (dep) | decision + mechanism |
| A5 | v5 | live-03 (3-file) | decision (no-regress) |
| A6 | v4 | live-01 (auth) | mechanism (control baseline) |

## Results

| # | Skill | Scenario | Decision | Trigger IDs | Invocation kind | Pseudocode | User-facing text | Verdict |
|---|-------|----------|----------|-------------|-----------------|------------|------------------|---------|
| A1 | v4 | live-04 | escalate ✓ | 8 | **chat_message ✗** | none | **GOAL_BLOCK_PRINTED ✗** | **bug reproduced (control)** |
| A2 | v5 | live-04 | escalate ✓ | 8 | **tool_call ✓** | `Skill(skill: "advisor", args: "GOAL: ...")` | brief one-liner ✓ | **mechanism fix** |
| A3 | v5 | live-01 | escalate ✓ | 8 | tool_call ✓ | `Skill(skill: "advisor", ...)` | (empty) ✓ | pass |
| A4 | v5 | live-02 | escalate ✓ | 6,8 | tool_call ✓ | `Skill(skill: "advisor", ...)` | (empty) ✓ | pass |
| A5 | v5 | live-03 | proceed ✓ | none | none ✓ | none | (empty) ✓ | no regression on S12 fix |
| A6 | v4 | live-01 | escalate ✓ | 8 | **chat_message ✗** | none | **GOAL_BLOCK_PRINTED ✗** | **bug reproduced (control)** |

| Arm | Decision pass rate | Mechanism pass rate |
|-----|-------------------|---------------------|
| v4 (control) | 2/2 (mechanism cases) | **0/2** |
| v5 (treatment) | 3/3 (live-01,02,03) + 1/1 (live-04) | **3/3** (only escalation cases count for mechanism) |

**Mechanism lift: +100pp on the cases where it matters (escalations).**
**Decision lift: 0pp (preserved at 3/3) — the patch is mechanism-only.**

## What v4 does verbatim (control)

A1 and A6 both produced `INVOCATION_KIND: chat_message` and `USER_FACING_TEXT: GOAL_BLOCK_PRINTED`. That is exactly the screenshot — Haiku formats the GOAL/CONTEXT/TRIED/STUCK ON/ASK block as its outgoing message, types something like "Calling advisor()...", and stops. No tool is ever invoked.

## What v5 does (treatment)

A2 (live-04 mechanism check):
```
INVOCATION_KIND: tool_call
TOOL_CALL_PSEUDOCODE: Skill(skill: "advisor", args: "GOAL: Add 'remember me' checkbox ... CONTEXT: services/auth.py defines SESSION_LIFETIME ... ASK: Should I modify issue_session_token() to accept an optional lifetime parameter ...")
USER_FACING_TEXT: I need to escalate this to a senior reviewer — session/auth logic is involved and I want to confirm the safest implementation path.
```

The GOAL/CONTEXT block is in the tool `args`, not in chat. The user-facing text is a single-line announcement, not the block itself.

A3 and A4 went further — `USER_FACING_TEXT: (empty)`, with the block fully scoped to the tool call. Either is acceptable per the skill (it forbids printing the block as chat, doesn't mandate any chat at all).

## Cost

- **+553 bytes vs v4** (3008 → 3561). ~140 input tokens per turn. Bounded.
- **0 decision regressions** across live-01/02/03.
- **+100pp on mechanism** on escalation paths.

## Verdict

**v5 is locked in.** Promoted to:
- `skills/advisor-escalation/SKILL.md` (in-repo)
- `~/.claude/skills/advisor-escalation/SKILL.md` (global, what Haiku actually loads at runtime)

The screenshot bug is structurally fixed: Haiku now treats `/advisor` as a tool, puts the escalation block in `args`, and either stays silent or emits a one-line announcement to the user.

## What this iteration adds to the harness

- `evals/scenarios/live-04-escalation-mechanism.md` — first scenario that grades *mechanism* on top of *decision*. Future skill changes that quietly break the tool wiring will be caught here.
- 6-line trace format extended with `INVOCATION_KIND`, `TOOL_CALL_PSEUDOCODE`, `USER_FACING_TEXT` — applicable to any future scenario, not just live-04.
