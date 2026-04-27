"""Orders service. Pure business logic — no Flask globals."""
from __future__ import annotations

from typing import Iterable

from app import db
from models import Order, OrderItem


def list_orders_for_user(user_id: int) -> list[Order]:
    return Order.query.filter_by(user_id=user_id).all()


def create_order(user_id: int, items: Iterable[dict]) -> Order:
    order = Order(user_id=user_id, status="PENDING")
    db.session.add(order)
    db.session.flush()
    for item in items:
        db.session.add(
            OrderItem(
                order_id=order.id,
                sku=item["sku"],
                unit_price_cents=item["unit_price_cents"],
            )
        )
    db.session.commit()
    return order


def mark_dispatched(order_id: int) -> Order:
    order = Order.query.get_or_404(order_id)
    order.status = "DISPATCHED"
    db.session.commit()
    return order
