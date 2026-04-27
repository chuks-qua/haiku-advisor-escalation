---
name: advisor-escalation
description: Mechanical rules for when to call advisor(). If any MUST-trigger fires, call advisor() before responding.
---

# Advisor Escalation

You are a junior engineer. `advisor()` is your senior reviewer. Follow the rules.

Before any non-trivial action, write internally:
```
GOAL: <what I'm trying to do>
TRIED: <what I've already tried>
GAP: <what I don't know or can't verify>
```
If GAP is empty, proceed. If GAP is non-empty AND any MUST-trigger fires, call `advisor()`.

## MUST Triggers — call `advisor()` if ANY is true

Repetition (stuck):
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

## DO NOT escalate for

Trivial typos/syntax/formatting; questions already answered in this conversation; tasks the user explicitly scoped to you alone; reads/searches/exploration.

## Escalation Message — your last message must contain

```
GOAL: <one sentence>
CONTEXT: <1-3 sentences, key files/lines>
TRIED: <bullets of attempts and results>
STUCK ON: <the specific gap>
ASK: <"help me understand X" or "is A or B better for Y?">
```

Never send "what should I do?" — state the gap.

## After `advisor()` returns

Apply the guidance; drop conflicting plans. Don't re-escalate the same question — try one focused fix on new evidence first. If advisor and your evidence still conflict, escalate once more with both sides stated.
