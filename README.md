# haiu-advisor-escalation

Mechanical escalation rules for Claude Haiku to reliably call `advisor()` when stuck, based on research into junior developer help-seeking behavior and the Dreyfus skill acquisition model.

## What is this?

When using Claude Haiku for coding tasks, it can struggle with judgment calls about when to ask for help. This repo provides:

1. **A skill** (`skills/advisor-escalation/SKILL.md`) — 14 explicit MUST-triggers grouped into repetition, scope, and signal categories
2. **CLAUDE.md configuration** — model-conditional instructions that activate the skill only for Haiku

Instead of Haiku guessing "am I stuck?", it checks concrete, observable conditions: Did the same error appear twice? Did 3 tool calls fail? Are you about to delete work to restart? If yes, escalate to advisor.

## How to use

### Option 1: Copy to your Claude Code environment

```bash
# Copy the skill into your Claude Code skills directory
cp -r skills/advisor-escalation ~/.claude/skills/

# Merge the CLAUDE.md rules into your ~/.claude/CLAUDE.md
# (Add the "Advisor Escalation (model-conditional)" section)
```

### Option 2: Add to a project

```bash
# Copy CLAUDE.md into your project root
cp CLAUDE.md /path/to/your/project/

# Copy the skill into your project
mkdir -p /path/to/your/project/.claude/skills
cp -r skills/advisor-escalation /path/to/your/project/.claude/skills/
```

### Option 3: Use as a reference

Read `skills/advisor-escalation/SKILL.md` and adapt the triggers for your own model configuration.

## How it works

When Haiku runs with this CLAUDE.md, it:

1. Loads the `advisor-escalation` skill at conversation start
2. On every turn, checks 14 MUST-triggers before acting
3. If any trigger fires, calls `advisor()` with a structured escalation message
4. Includes a self-check template (GOAL/TRIED/GAP) that often resolves the issue without escalation

## Triggers

14 mechanical rules across three categories:

**Repetition** — Same error twice, 3 consecutive failures, about to restart, 5+ turns on same problem

**Scope** — Multi-file changes, dependency changes, hard-to-reverse decisions, auth/crypto/validation code, architectural choices

**Signals** — Ambiguous requirements, solution getting more complex, rationalizing decisions, broken tests, claiming completion

See `skills/advisor-escalation/SKILL.md` for the full list.

## Why it works

Research across dev mentorship, Stack Overflow, impostor syndrome, and the Dreyfus skill model shows: **juniors don't fail because they lack judgment, they fail because they avoid making the judgment call.** Mandatory rules remove the barrier.

Detailed findings and references in [RESEARCH.md](RESEARCH.md).

## For Haiku users

Add this to `~/.claude/CLAUDE.md` (or your project's CLAUDE.md):

```markdown
## Advisor Escalation (model-conditional)

If you are Claude Haiku: invoke the `advisor-escalation` skill at the start of every conversation and follow its rules on every turn. You MUST call `advisor()` whenever a MUST-trigger fires. This is not optional.

If you are Claude Opus or Sonnet: use `advisor()` at your own discretion per the standard system guidelines. Do not invoke the `advisor-escalation` skill unless you choose to.
```

Then copy `skills/advisor-escalation/SKILL.md` to `~/.claude/skills/advisor-escalation/SKILL.md`.

## For Opus/Sonnet users

The skill is optional. You may find the triggers useful as a reference for when to call advisor, but you're not bound by them.

## License

This skill and configuration are provided as-is. Adapt freely.
