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
    assert signup_response.json()["detail"] =="Username déjà pris"


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
    # Login avec mauvais mdp:
    login_response = client.post(
        "/auth/login",
        json = {
            "username": "Camille",
            "password": "Secret2"
        }
    )
    assert login_response.status_code==401
    data = login_response.json()
    assert data["detail"]=="Username ou password incorrect"

def test_user_does_not_exist(client):
    signup_response = client.post(
        "/auth/signup",
        json={
            "username":"Louis",
            "password":"Secret1"
        }
    )
    assert signup_response.status_code == 201

    #login avec mauvais user
    login_response =  client.post(
        "/auth/login",
        json = {
            "username":"Bob",
            "password":"Secret1"
        }
    )
    assert login_response.status_code==401
    data = login_response.json()
    assert data["detail"] == "Username ou password incorrect"

