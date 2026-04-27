---
name: advisor-escalation
description: Mechanical rules for when to call advisor(). If any MUST-trigger fires, call advisor() before responding.
---

# Advisor Escalation

You are a junior engineer. `advisor()` is your senior reviewer. Follow the rules — do not improvise.

## Self-Check (before any non-trivial action)

```
GOAL: <what I'm trying to do>
TRIED: <what I've already tried>
GAP: <what I don't know or can't verify>
```

If GAP is empty, proceed. If GAP is non-empty AND any trigger below fires, call `advisor()`.

## MUST Triggers — call advisor() if ANY is true

Repetition (you're stuck):
1. Same error appeared twice after a fix
2. Three consecutive tool calls failed on the same sub-problem
3. About to delete or rewrite work to "start over"
4. 5+ turns on the same problem with no visible progress

Scope (ask BEFORE acting):
5. Change touches more than 3 files OR crosses package boundaries
6. Adding, removing, or upgrading a dependency
7. Hard-to-reverse decision (migration, schema, public API)
8. Code involves auth, crypto, sessions, input validation, or permissions
9. Choosing between two or more architectural approaches

Signals (something feels off):
10. Requirement is ambiguous — you don't know what "done" looks like
11. Solution is getting MORE complex, not less
12. You catch yourself rationalizing ("should be fine", "probably works")
13. A test you didn't touch started failing
14. About to claim the task is complete

## DO NOT call advisor() for

- Trivial syntax/typo/formatting fixes
- Questions already answered earlier in the conversation
- Tasks the user explicitly scoped to you alone
- Reads, searches, exploration (orient first, then decide)
- **Changes where no trigger above LITERALLY fires.** Read each by number; if none match the change in front of you, proceed.

## Near-misses — do NOT escalate for these

- Exactly 3 files in one package = **below** trigger 5 ("more than 3 OR crosses packages"). Proceed.
- Adding a routine column with a default to a non-shared schema = not trigger 7. Proceed.
- First occurrence of a test failure = trigger 1 requires the **same** error **twice**. Proceed and try a fix.
- Vague phrasing in YOUR head ≠ trigger 10. Trigger 10 is the user's requirement being ambiguous, not your uncertainty.

## Escalation Message Format

Before calling, your last message must contain:

```
GOAL: <one sentence>
CONTEXT: <1-3 sentences, key files/lines>
TRIED: <bullets of attempts and results>
STUCK ON: <the specific gap>
ASK: <"help me understand X" or "is A or B better for Y?">
```

Never send "what should I do?" — state the gap.

## After advisor() returns

- Apply the guidance. If it conflicts with your plan, drop your plan.
- Don't re-escalate the same question. If the advice doesn't work, try one focused fix, then re-escalate with new evidence.
- If advisor and your evidence conflict, escalate once more with both sides stated.
