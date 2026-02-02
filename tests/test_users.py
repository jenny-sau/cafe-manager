#-----------------------------------------------------
# Tester le métier sur les users
#-----------------------------------------------------

# Test GET /users
# -----------------------------------------------------
# Test GET /users - Un admin peut lister les users
def test_get_users_ok(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        "/users",
        headers = headers
    )

    assert response.status_code == 200

# Test GET /users/{user_id}
#-----------------------------------------------------
# Test GET - Un admin peut lire un user
def test_get_users_with_user_id_ok(client, admin_token, user_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        f"/users/{user_id}",
        headers=headers
    )

    assert response.status_code == 200

# Test GET - Si user inexistant - Impossible de le lire
def test_get_users_no_existing_user_ko(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        f"/users/{400}",
        headers=headers
    )

    assert response.status_code == 404

# Test PUT /users/{user_id}
#----------------------------------------------------
# PUT /users/{user_id} - admin peut modifier
def test_put_users_ok(client, admin_token, user_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.put(
        f"/users/{user_id}",
        json ={"username": "Jenifer"},
        headers = headers
    )
    assert response.status_code == 200

# PUT /users/{user_id} - Si user inexistant - Impossible de le modifier
def test_put_user_non_existing_user_ko (client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.put(
        f"/users/{44}",
        json={"username": "Jenifer"},
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# DELETE /users/{user_id}
# --------------------------------------------------
# DELETE /users/{user_id} - Un admin peut supprimer un user
def test_delete_a_user_ok (client, admin_token, user_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/users/{user_id}",
        headers = headers
    )

    assert response.status_code == 200
