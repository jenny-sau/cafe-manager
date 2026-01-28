# -----------------------------------------
# Tests des dépendances de sécurité
# -----------------------------------------

# get_current_user OK
def test_get_current_user_ok(client, user_token, menu_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/menu/{menu_id}",
        headers=headers
    )

    assert response.status_code == 200


# get_current_user sans token -> 403
def test_get_item_menu_without_token(client, menu_id):
    response = client.get(f"/menu/{menu_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


# get_current_user token invalide -> 401
def test_get_item_menu_wrong_token(client, menu_id):
    response = client.get(
        f"/menu/{menu_id}",
        headers={"Authorization": "Bearer totally.invalid.token"}
    )

    assert response.status_code == 401


# get_current_admin OK
def test_admin_ok(client, admin_token):
    response = client.post(
        "/menu",
        json={
            "name": "café",
            "purchase_price": 1.0,
            "selling_price": 1.2
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 201


# get_current_admin bloque user -> 403
def test_user_on_admin_only(client, user_token):
    response = client.post(
        "/menu",
        json={
            "name": "café",
            "purchase_price": 1.0,
            "selling_price": 1.2
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Accès refusé : Vous devez être admin"
