def test_register_and_login(client):
    register_data = {
        "name": "Joh",
        "email": "joh@example.com",
        "password": "pass123",
        "role": "client"
    }
    res = client.post("/api/register", json=register_data)
    assert res.status_code == 201

    login_data = {
        "email": "joh@example.com",
        "password": "pass123"
    }
    res = client.post("/api/login", json=login_data)
    assert res.status_code == 200
    assert "token" in res.get_json()


def test_register_duplicate_email(client):
    """Test registering with a duplicate email."""
    register_data = {
        "name": "Joh",
        "email": "joh@example.com",  # This email is already used
        "password": "pass123",
        "role": "client"
    }
    # Second registration should fail
    res = client.post("/api/register", json=register_data)
    assert res.status_code == 400  # Assuming 400 is the status code for bad request
    assert "error" in res.get_json()  # Check for error message

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        "email": "joh@example.com",  # Registered email
        "password": "wrongpassword"  # Incorrect password
    }
    res = client.post("/api/login", json=login_data)
    assert res.status_code == 401  # Expecting unauthorized status
    assert "error" in res.get_json()  # Check for error message


def test_update_user_profile(client):

    login_data = {
        "email": "joh@example.com",
        "password": "pass123"
    }
    login_res = client.post("/api/login", json=login_data)
    token = login_res.get_json()["token"]

    # Now, update the user profile
    update_data = {
        "name": "Joh Updated",
        "email": "joh_updated@example.com"
    }
    update_res = client.put("/api/profile", json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert update_res.status_code == 405

    
def test_logout(client):
    """Test logging out a user."""
    # First, register and log in the user
    register_data = {
        "name": "Mary",
        "email": "mary@example.com",
        "password": "marypass123",
        "role": "client"
    }
    client.post("/api/register", json=register_data)

    login_data = {
        "email": "mary@example.com",
        "password": "marypass123"
    }
    login_res = client.post("/api/login", json=login_data)
    token = login_res.get_json()["token"]

    # Test logout
    logout_res = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    
    # Verify logout response
    assert logout_res.status_code == 200
    assert "message" in logout_res.get_json()
    assert logout_res.get_json()["message"] == "Logged out successfully"

    
