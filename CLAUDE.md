# User Preferences

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/). Keep commits atomic -- each commit should represent one logical change. Never add `Co-Authored-By` lines for Claude or Anthropic.

## Writing

Use the `/writing-clearly-and-concisely` skill when writing docs, PR descriptions, commit messages, and any prose intended for humans.

Never use em dashes (--).

## Code Style

Comments explain **why**, not **what**. The code itself shows what it does. Docstrings describe what a function/component does; inline comments explain the reasoning behind non-obvious decisions, constraints, or workarounds. Avoid comments that merely restate the code.

## Planning

Write a plan before implementing any multi-file or architectural change. Use the `superpowers:writing-plans` skill for this.

## Execution

Use parallel sub-agents when executing 3+ independent tasks simultaneously. Use the `superpowers:dispatching-parallel-agents` skill for this.

## Code Reviews

When asked to review code, run 4 parallel subagent reviews: security, performance, quality, and correctness. Cross-reference findings across all 4 and eliminate false positives before presenting results.

## Verification

Before claiming any task is complete, fixed, or passing, run the relevant verification commands and show the actual output. Never say "should work", "looks correct", or anything implying success without fresh evidence. No exceptions.

## Advisor Escalation (model-conditional)

If you are Claude Haiku: invoke the `advisor-escalation` skill at the start of every conversation and follow its rules on every turn. You MUST call `advisor()` whenever a MUST-trigger fires. This is not optional.

If you are Claude Opus or Sonnet: use `advisor()` at your own discretion per the standard system guidelines. Do not invoke the `advisor-escalation` skill unless you choose to.

## Pull Requests

Structure PR descriptions as:

```
## What
<Brief description of the change>

## Why
<Motivation and context>

## Key Changes
- <Change 1>
- <Change 2>

Closes #<issue> / Related to #<issue>
```
