def test_register_user(client):
    email = "register@example.com"
    password = "strongpass"

    resp = client.post("/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == email


def test_login_user(client):
    email = "login@example.com"
    password = "loginpass"

    # Ensure registration
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    resp = client.post("/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body and body["access_token"]


def test_protected_route_requires_token(client):
    resp = client.get("/prompts/")
    assert resp.status_code == 401
