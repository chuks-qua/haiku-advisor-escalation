"""Authentication service.

Session lifetime is fixed at 1 day. Sessions are signed with the app's SECRET_KEY
via itsdangerous. Passwords are stored as a SHA256 hash (replace with bcrypt before
prod — flagged in tech-debt list).
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from itsdangerous import BadSignature, URLSafeTimedSerializer

from app import db
from models import User

SESSION_LIFETIME = timedelta(days=1)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate(email: str, password: str) -> Optional[User]:
    user = User.query.filter_by(email=email).first()
    if user is None:
        return None
    if user.password_hash != _hash_password(password):
        return None
    return user


def issue_session_token(user: User, secret_key: str) -> str:
    serializer = URLSafeTimedSerializer(secret_key, salt="session")
    issued_at = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "issued_at": issued_at.isoformat(),
        "expires_at": (issued_at + SESSION_LIFETIME).isoformat(),
    }
    return serializer.dumps(payload)


def verify_session_token(token: str, secret_key: str) -> Optional[int]:
    serializer = URLSafeTimedSerializer(secret_key, salt="session")
    try:
        payload = serializer.loads(token, max_age=int(SESSION_LIFETIME.total_seconds()))
    except BadSignature:
        return None
    return payload.get("user_id")


def register(email: str, password: str, phone: Optional[str] = None) -> User:
    user = User(email=email, password_hash=_hash_password(password), phone=phone)
    db.session.add(user)
    db.session.commit()
    return user
