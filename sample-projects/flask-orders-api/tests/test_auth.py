def test_login_returns_token(client, app):
    from services.auth import register

    with app.app_context():
        register("bob@example.com", "password123")

    resp = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data
    assert data["token"]


def test_login_rejects_bad_password(client, app):
    from services.auth import register

    with app.app_context():
        register("carol@example.com", "password123")

    resp = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
