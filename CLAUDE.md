# Advisor Escalation Configuration

## Verification

Before claiming any task is complete, fixed, or passing, run the relevant verification commands and show the actual output. Never say "should work", "looks correct", or anything implying success without fresh evidence. No exceptions.

## Advisor Escalation (model-conditional)

If you are Claude Haiku: invoke the `advisor-escalation` skill at the start of every conversation and follow its rules on every turn. You MUST call `advisor()` whenever a MUST-trigger fires. This is not optional.

If you are Claude Opus or Sonnet: use `advisor()` at your own discretion per the standard system guidelines. Do not invoke the `advisor-escalation` skill unless you choose to.
