#-----------------------------------------------------
# Tester on USERS
#-----------------------------------------------------

# Test GET /users
# -----------------------------------------------------
# An administrator can list the users
def test_get_users_ok(client, admin_token):
    response = client.get(
        "/users",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

# Test GET /users/{user_id}
#-----------------------------------------------------
# An admin can view a user
def test_get_users_with_user_id_ok(client, admin_token, user_id):
    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200

# User does not exist -> Cannot read it
def test_get_users_no_existing_user_ko(client, admin_token):
    response = client.get(
        f"/users/{400}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404

# Test PUT /users/{user_id}
#----------------------------------------------------
# An admin can update
def test_put_users_ok(client, admin_token, user_id):
    response = client.put(
        f"/users/{user_id}",
        json ={"username": "Jenifer"},
        headers = {"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

# User does not exist -> Impossible to update
def test_put_user_non_existing_user_ko (client, admin_token):
    response = client.put(
        f"/users/{44}",
        json={"username": "Jenifer"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# DELETE /users/{user_id}
# --------------------------------------------------
# An admin can delete a user
def test_delete_a_user_ok (client, admin_token, user_id):
    response = client.delete(
        f"/users/{user_id}",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200

# Cannot delete a non existing user
def test_delete_non_existing_user_ko(client, admin_token):
    response = client.delete(
        f"/users/{44}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
