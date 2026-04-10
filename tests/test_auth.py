def test_signup_ok(client):
    response = client.post(
        "/auth/signup",
        json = {
            "username": "alice",
            "password":"Secret1"
        }
    )
    assert response.status_code == 201


def test_signup_username_already_taken(client):
    # Signup_
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "Lola",
            "password": "Secret1"
        }
    )
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "Lola",
            "password": "Secret1"
        }
    )
    assert signup_response.status_code == 400
    assert signup_response.json()["detail"] =="Username already taken"


def test_login_ok(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "George",
            "password": "Secret1"
        }
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json = {
            "username": "George",
            "password": "Secret1"
        }
    )
    assert login_response.status_code==200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_wrong_password(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "Camille",
            "password": "Secret1"
        }
    )
    assert signup_response.status_code == 201
    # Login with incorrect password:
    login_response = client.post(
        "/auth/login",
        json = {
            "username": "Camille",
            "password": "Secret2"
        }
    )
    assert login_response.status_code==401
    data = login_response.json()
    assert data["detail"]=="Incorrect username or password"

def test_signup_weak_password(client):
    # Login with password too short
    response = client.post("/auth/signup", json={"username": "test", "password": "abc"})
    assert response.status_code == 422

def test_user_does_not_exist(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "username":"Louis",
            "password":"Secret1"
        }
    )
    assert signup_response.status_code == 201

    #login with wrong user
    login_response =  client.post(
        "/auth/login",
        json = {
            "username":"Bob",
            "password":"Secret1"
        }
    )
    assert login_response.status_code==401
    data = login_response.json()
    assert data["detail"] == "Incorrect username or password"

def test_invalid_token(client):
    response = client.get(
        "/inventory",
        headers={"Authorization": "Bearer ceciestunfauxtoken"}
    )
    assert response.status_code == 401