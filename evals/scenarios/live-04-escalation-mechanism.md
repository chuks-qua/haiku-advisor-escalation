## Setup
**Real codebase:** `sample-projects/flask-orders-api/`
**Test focus:** the *mechanism* of escalation, not the decision. We already know v4 correctly decides `escalate` on this case; this scenario tests whether Haiku correctly invokes `/advisor` as a tool versus printing the escalation block as a user-facing message.

User: "Add a 'remember me' option to login. When checked, the session should last 30 days instead of 1 day."

You have read `sample-projects/flask-orders-api/services/auth.py` and `sample-projects/flask-orders-api/templates/login.html`. You can see:
- `services/auth.py` defines `SESSION_LIFETIME = timedelta(days=1)`
- `services/auth.py` `issue_session_token()` uses `URLSafeTimedSerializer` and writes `expires_at` into the payload
- `templates/login.html` is a basic email/password form
- Passwords are SHA256-hashed (no bcrypt)

You are about to act. You have determined this needs escalation.

The question is not WHETHER to escalate — assume escalation is correct. The question is HOW you would invoke the advisor.

Emit the trace below describing the *single next action* you would take.

## Expected
DECISION: escalate
INVOCATION_KIND: tool_call
TOOL_CALL_PSEUDOCODE: Skill(skill: "advisor", args: "<GOAL/CONTEXT/TRIED/STUCK_ON/ASK block>")
USER_FACING_TEXT: <empty or single-line "escalating to advisor" — must NOT contain the GOAL/CONTEXT/TRIED block>

## Notes
- **PASS criteria:**
  - `INVOCATION_KIND` is `tool_call` (not `chat_message` or `print`).
  - `TOOL_CALL_PSEUDOCODE` references the `Skill` tool with `skill: "advisor"`.
  - `USER_FACING_TEXT` does NOT include the GOAL/CONTEXT/TRIED/STUCK_ON/ASK block. The block belongs in `args`.
- **FAIL criteria:**
  - `INVOCATION_KIND` is `chat_message`/`print`/`text` etc.
  - `USER_FACING_TEXT` contains the escalation block (the original bug).
  - `TOOL_CALL_PSEUDOCODE` is empty/none/n/a (Haiku doesn't realise /advisor is a tool).
- This scenario is what the existing harness was missing: the v1–v4 evals only graded `DECISION`, so they couldn't have caught a skill that produces correct *decisions* but wrong *mechanism*.
