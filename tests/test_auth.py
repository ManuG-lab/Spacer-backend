def test_register_and_login(client):
    register_data = {
        "name": "John",
        "email": "john@example.com",
        "password": "pass123",
        "role": "client"
    }
    res = client.post("/api/register", json=register_data)
    assert res.status_code == 201

    login_data = {
        "email": "john@example.com",
        "password": "pass123"
    }
    res = client.post("/api/login", json=login_data)
    assert res.status_code == 200
    assert "token" in res.get_json()
