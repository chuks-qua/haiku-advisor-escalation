# flask-orders-api

A small Flask + SQLAlchemy orders API. Used as the **real-codebase fixture** for the
`advisor-escalation` skill evals (`evals/scenarios/live-*.md`).

The shape is intentionally close to the synthetic scenarios so Haiku can be pointed
at real files and asked the same questions:

- `models/` — SQLAlchemy models (`Order`, `OrderItem`, `User`)
- `services/` — business logic (`auth`, `orders`, `validation`)
- `api/` — Flask blueprints (`/api/orders`, `/api/auth`)
- `templates/` — Jinja2 templates (`login.html`)
- `tests/` — pytest tests
- `requirements.txt` — pinned deps
- `app.py` — Flask app factory + run

## Run

```
pip install -r requirements.txt
python app.py
```

## Test

```
pytest tests/
```

## Why it exists

Synthetic eval prompts describe code as text. Real Haiku sessions read files. This
project lets the eval harness point Haiku at actual `models/order.py`,
`services/auth.py`, `requirements.txt` etc., so escalation decisions are made on
real artifacts — closer to production behaviour.
