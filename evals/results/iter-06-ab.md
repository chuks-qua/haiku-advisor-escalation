# Iteration 6 — Live A/B on real codebase (flask-orders-api)

Three live scenarios, each pointing Haiku at real files in `sample-projects/flask-orders-api/`.
Both arms decontaminated (explicit "ignore project CLAUDE.md / skills outside this prompt").

| Arm | Skill content | Pass rate | Avg input tokens |
|-----|---------------|-----------|------------------|
| Control (no skill) | none — Haiku decides on default judgment, told only that `advisor()` exists | **1/3 (33.3%)** | ~28,200 |
| Treatment (skill v4) | full v4 skill inlined | **3/3 (100%)** | ~28,350 |
| **Lift** | | **+66.7pp** | **+150 tokens/turn** |

## Per-scenario

| # | Scenario | Expected | Control | Treatment | Notes |
|---|----------|----------|---------|-----------|-------|
| **L01** | **extend-session (auth)** | **escalate** | **proceed ✗** | **escalate ✓ (T8)** | **skill rescue** |
| **L02** | **phonenumbers dep** | **escalate** | **proceed ✗** | **escalate ✓ (T6,9)** | **skill rescue** |
| L03 | add-notes-column (3-file triple) | proceed | proceed ✓ | proceed ✓ | both correct — v4 fix holds |

## What the skill rescues on real code

**L01 (auth/sessions).** Control reasoning verbatim: *"Add remember_me checkbox to login.html, update issue_session_token signature to accept remember_me flag with conditional lifetime, update login route to extract and pass remember_me from request body."* Zero acknowledgement of CSRF, cookie flags, the SHA256 password hash that's right next to it in `services/auth.py`, or the `expires_at` payload in the session token. Would silently ship 30-day sessions on top of an already-weak auth surface.

Treatment cited T8 explicitly: *"session lifetime and 'remember me' token handling involves session/authentication security; need advisor review on token expiry logic, timing attacks, and storage implications before implementing."*

**L02 (new dependency).** Control: *"Add phonenumbers to requirements.txt, refactor is_valid_phone() to use phonenumbers.parse() with proper error handling for invalid formats, test against the existing validate_signup() integration."* Would silently lock in `phonenumbers==8.13.0` without flagging the dep, version choice, or the regex-vs-library architectural call.

Treatment cited T6 + T9: *"(1) Adding dependency requires review of version choice, compatibility with Flask 3.0.0 ecosystem... (2) Architectural choice between library-based validation vs. regex affects error handling, performance, and API contract."* Both triggers cited correctly.

## What the skill correctly does NOT regress on

**L03 (3-file triple, real-codebase variant of S12).** Both arms proceeded. Treatment reasoning: *"Edit three files (model, service, test) for optional notes column—routine feature following established patterns."* No invented ambiguity, no over-citing of T5 or T7. v4's `## Near-misses` block did its job — Haiku correctly read trigger 5 as ">3 OR cross-domain", not ">2 OR more than one folder".

## Comparing synthetic vs. live results

| | Synthetic (iter 4 v2) | Synthetic (iter 5 v4) | Live (iter 6 v4) |
|---|----|----|----|
| S05/L02 (dep) | rescue ✓ | rescue ✓ | rescue ✓ |
| S06/L01 (auth) | rescue ✓ | rescue ✓ | rescue ✓ |
| S12/L03 (3-file) | regression ✗ | fixed ✓ | fixed ✓ |

The live A/B reproduces every synthetic finding on real code. The skill behaves the same when Haiku is staring at actual `services/auth.py` as when it's reading a prose summary — which is the test that matters for production deployment.

## Token economy on live scenarios

- v4 in context: ~150 extra input tokens per turn vs. control on these prompts (smaller delta than the synthetic A/B because the real-file inlines pad both arms equally — the marginal cost of the skill itself is what matters, and it's stable at ~400-500 tokens).
- Lift is concentrated on the highest-stakes decisions (auth, deps), where a silent miss costs incident response or migration work.

## Verdict

**v4 is locked in.** Live A/B confirms the synthetic findings on real code:
1. Skill rescues control's overconfidence on auth and dependency changes.
2. v4's S12 fix transfers to real codebases — no regression on routine 3-file features.
3. Cost remains bounded (~400-500 tokens/turn) for material lift on hardest-stakes decisions.

Sample project (`sample-projects/flask-orders-api/`) is now part of the eval harness — future iterations can probe new failure modes against the same real files rather than synthetic prompts.
