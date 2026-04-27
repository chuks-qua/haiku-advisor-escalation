def test_create_and_list_order(client, app):
    from services.auth import register
    from services.orders import create_order

    with app.app_context():
        user = register("alice@example.com", "password123")
        order = create_order(
            user.id,
            [{"sku": "WIDGET-1", "unit_price_cents": 999}],
        )
        assert order.id is not None
        assert order.status == "PENDING"

    resp = client.get(f"/api/orders?user_id={user.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["status"] == "PENDING"
