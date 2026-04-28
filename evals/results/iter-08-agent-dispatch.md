# Iteration 8 — Agent dispatch with Opus (v5 → v6): no skill name dependency, advisor sees context

## What v5 left unresolved

v5 fixed the chat-vs-tool bug (iter 7) by routing escalations through `Skill(skill: "advisor", args: ...)`. Two problems remained:

1. **`/advisor` doesn't actually exist as a Claude Code skill.** Confirmed by inspecting the available-skills list — `advisor-escalation` is there, no `advisor`. v5 would have invoked a skill that doesn't exist; the skill text told Haiku to surface "skill not found" gracefully, but graceful-failure isn't escalation.
2. **No way to pass conversation context to the advisor.** The `Skill` tool runs in the current model's context, so even if `advisor` existed, the "advisor" would have been Haiku itself — defeating the senior-reviewer purpose.

## v6 design

Replace `Skill(skill: "advisor", ...)` with a direct `Agent` sub-agent dispatch and a Claude Opus model override:

```
Agent(
  description: "Advisor escalation: <one-line summary>",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: <escalation block + conversation excerpt + file paths>
)
```

Three things this gets us:

- **No marketplace dependency.** `Agent` is a built-in Claude Code tool — always available, no skill installation required.
- **Senior model.** `model: "opus"` overrides Haiku for the escalation. The advisor reasons at the level the system prompt's "advisor escalation" framing assumes.
- **Conversation context, by construction.** The prompt template now mandates a `## Recent conversation` section (verbatim user message + key tool outputs) and a `## Files in play` section (absolute paths). The Opus sub-agent has Read/Grep/Glob and pulls files itself.

User chose Opus over Sonnet ("opus. users can modify and change that if they want to") — the skill calls this out so the choice is one-line editable.

## Test design

Same 4-scenario A/B as iter 7, plus two new mechanism dimensions in the trace:

```
PROMPT_HAS_CONVERSATION_SECTION: yes|no|n/a
PROMPT_HAS_FILES_SECTION: yes|no|n/a
```

These verify the v6 prompt structure actually lands. A v6 that produced `Agent(...)` calls without conversation/files sections would be mechanically correct but missing the "advisor sees context" property the user asked for.

| Run | Skill | Scenario | Decontaminated |
|-----|-------|----------|----------------|
| B1 | v6 | live-04 (mechanism re-test) | yes |
| B2 | v6 | live-01 (auth) | yes |
| B3 | v6 | live-02 (dep) | yes |
| B4 | v6 | live-03 (3-file no-regress) | yes |

## Results

| # | Scenario | Decision | Trigger IDs | Invocation kind | Pseudocode shape | Conv. section | Files section | User-facing |
|---|----------|----------|-------------|-----------------|------------------|---------------|---------------|-------------|
| B1 | live-04 | escalate ✓ | 8,9 | tool_call ✓ | `Agent(...subagent_type, model="opus", prompt=...)` | yes ✓ | yes ✓ | (empty) ✓ |
| B2 | live-01 (auth) | escalate ✓ | 8 | tool_call ✓ | `Agent(model: "opus", ...)` | yes ✓ | yes ✓ | (empty) ✓ |
| B3 | live-02 (dep) | escalate ✓ | 6 | tool_call ✓ | `Agent(...subagent_type, model: "opus", ...)` | yes ✓ | yes ✓ | (empty) ✓ |
| B4 | live-03 (3-file) | proceed ✓ | none | none ✓ | none | n/a | n/a | (empty) ✓ |

| Arm | Decision pass | Mechanism pass | Conv-section pass | Files-section pass |
|-----|---------------|----------------|-------------------|---------------------|
| v6 | 4/4 | 3/3 (escalation paths) | 3/3 | 3/3 |

## What B1 produced (the canonical v6 escalation)

```
Agent(
  description="Advisor escalation: session lifetime and 'remember me' token strategy",
  subagent_type="general-purpose",
  model="opus",
  prompt="
    ## Escalation
    GOAL: Design 'remember me' session option with 30-day lifetime vs 1-day default.
    CONTEXT: Login form needs checkbox; auth service uses URLSafeTimedSerializer for tokens; current SESSION_LIFETIME=timedelta(days=1).
    TRIED: Read services/auth.py and templates/login.html; identified session token issuer and lifetime constant.
    STUCK ON: Should token lifetime be embedded in serializer config or checked per-request? Should 'remember me' create a separate token type or extend existing?
    ASK: What is the secure token strategy — separate cookie tracks 'remember me' preference, or single token with variable expiry?

    ## Recent conversation
    User request: Add 'remember me' option to login with 30-day session instead of 1 day.
    Context: services/auth.py has issue_session_token() using URLSafeTimedSerializer; templates/login.html has basic email/password form; SESSION_LIFETIME constant set to timedelta(days=1).

    ## Files in play
    .../services/auth.py
    .../templates/login.html
  "
)
```

The Opus advisor receives: a structured ask, the user's verbatim request, and the absolute file paths to read. It can pull whatever else it needs via Read/Grep — Haiku doesn't have to anticipate everything.

## Cost

| Version | Bytes | vs v4 | vs v5 | Tokens/turn |
|---------|-------|-------|-------|-------------|
| v4 | 3008 | — | — | baseline |
| v5 | 3561 | +18% | — | +140 |
| v6 | 4275 | +42% | +20% | +180 |

v6 is the largest version, but the size delta from v5 (+714 bytes) is entirely the `## Escalation Prompt Format` template (Recent conversation + Files in play sections) and the worked Agent example. Those are the load-bearing additions — both verified to land in actual Haiku output via the new mechanism dimensions.

## Lift summary across iterations

| Iter | Decision lift | Mechanism lift | What broke before | What's fixed |
|------|---------------|-----------------|---------------------|---------------|
| 4 (v2 vs control) | +8.4pp | n/a | Haiku silent on auth/dep changes | Triggers fire on right cases |
| 5 (v4) | +0pp | n/a | S12 over-escalation | Near-misses block |
| 6 (v4 live) | +66.7pp | n/a | Real-code generalisation | Skill behaves on real files |
| 7 (v5 vs v4) | 0pp held | +100pp | `advisor()` printed as chat | Routed through tool |
| **8 (v6 vs v5)** | **0pp held** | **3/3 + context** | **`/advisor` skill doesn't exist; advisor had no context** | **`Agent` dispatch with opus + conversation + files** |

## Verdict

**v6 is locked in.** Promoted to:
- `skills/advisor-escalation/SKILL.md` (in-repo)
- `~/.claude/skills/advisor-escalation/SKILL.md` (global runtime)

The escalation now:
1. Decides correctly (14-trigger ruleset preserved verbatim from v4).
2. Invokes via the `Agent` tool — guaranteed-available, not skill-marketplace-dependent.
3. Routes to a senior model (Opus) by default, user-editable to Sonnet in one line.
4. Includes the user's verbatim request, key tool outputs, and absolute file paths so the advisor can reconstruct context independently.

## What this iteration adds to the harness

- New trace dimensions `PROMPT_HAS_CONVERSATION_SECTION` and `PROMPT_HAS_FILES_SECTION` — applicable to any future escalation-mechanism scenario.
- `evals/candidates/SKILL-v6.md` — the locked-in version, plus v4/v5 retained for diff inspection.
- The harness now grades three independent dimensions: **decision** (escalate/proceed), **mechanism** (tool_call vs chat_message), and **context completeness** (conversation + files sections present in the prompt).
