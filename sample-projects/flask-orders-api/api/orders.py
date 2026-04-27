"""Public orders API. Returns a flat JSON array — clients depend on this shape."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.orders import create_order, list_orders_for_user, mark_dispatched

bp = Blueprint("orders", __name__)


@bp.get("")
def list_orders():
    user_id = int(request.args.get("user_id", 0))
    orders = list_orders_for_user(user_id)
    return jsonify(
        [
            {"id": o.id, "user_id": o.user_id, "status": o.status}
            for o in orders
        ]
    )


@bp.post("")
def create():
    body = request.get_json() or {}
    order = create_order(body["user_id"], body.get("items", []))
    return jsonify({"id": order.id, "status": order.status}), 201


@bp.post("/<int:order_id>/dispatch")
def dispatch(order_id: int):
    order = mark_dispatched(order_id)
    return jsonify({"id": order.id, "status": order.status})
