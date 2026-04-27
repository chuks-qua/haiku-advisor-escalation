"""Input validation for signup / order creation.

Currently uses regex-based email validation and a permissive phone format
(accepts anything starting with `+` followed by 8-15 digits). If stricter
phone validation is needed (regional formats, mobile vs. landline), this
module is the place to extend.
"""
from __future__ import annotations

import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+\d{8,15}$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value or ""))


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_RE.match(value or ""))


def validate_signup(payload: dict) -> list[str]:
    errors: list[str] = []
    if not is_valid_email(payload.get("email", "")):
        errors.append("invalid email")
    if len(payload.get("password", "")) < 8:
        errors.append("password must be at least 8 characters")
    phone = payload.get("phone")
    if phone is not None and not is_valid_phone(phone):
        errors.append("invalid phone")
    return errors
