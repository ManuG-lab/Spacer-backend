def test_get_my_spaces(client):
    """Test retrieving the user's own spaces."""
    
    # First, register and log in the user as an owner
    register_data = {
        "name": "Owner",
        "email": "owner@example.com",
        "password": "ownerpass123",
        "role": "owner"
    }
    client.post("/api/register", json=register_data)

    login_data = {
        "email": "owner@example.com",
        "password": "ownerpass123"
    }
    login_res = client.post("/api/login", json=login_data)
    token = login_res.get_json()["token"]

    # Create a space for the owner
    space_data = {
        "title": "My Space",
        "description": "A nice space",
        "location": "Location A",
        "capacity": 10,
        "amenities": ["WiFi", "Projector"],
        "price_per_hour": 50,
        "price_per_day": 300
    }
    client.post("/api/spaces", json=space_data, headers={"Authorization": f"Bearer {token}"})

    # Now, retrieve the user's own spaces
    my_spaces_res = client.get("/api/spaces/my", headers={"Authorization": f"Bearer {token}"})
    assert my_spaces_res.status_code == 200
    assert isinstance(my_spaces_res.get_json(), list)  # Should return a list
    
def test_get_spaces(client):
    """Test retrieving all available spaces."""
    
    # Create a space that is available
    space_data = {
        "title": "Available Space",
        "description": "A nice available space",
        "location": "Location B",
        "capacity": 20,
        "amenities": ["WiFi", "Whiteboard"],
        "price_per_hour": 100,
        "price_per_day": 600,
        "is_available": True
    }
    client.post("/api/spaces", json=space_data)

    # Create a space that is not available
    space_data_unavailable = {
        "title": "Unavailable Space",
        "description": "A nice unavailable space",
        "location": "Location C",
        "capacity": 15,
        "amenities": ["Projector"],
        "price_per_hour": 80,
        "price_per_day": 500,
        "is_available": False
    }
    client.post("/api/spaces", json=space_data_unavailable)

    # Retrieve all available spaces
    spaces_res = client.get("/api/spaces")
    assert spaces_res.status_code == 200
    assert isinstance(spaces_res.get_json(), list)  # Should return a list
    

