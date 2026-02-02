#-------------------------------------------------------------
#Tester le métier du menu
#----------------------------------------------

# Test POST /menu
#----------------------------------------------
# POST /menu - Un ADMIN peut créer un item au menu
def test_create_ok(client, admin_token):
    response = client.post(
        "/menu",
        json={
            "name": "café",
            "purchase_price": 1.0,
            "selling_price": 1.2
        },
        headers = {"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201


# Test (GET /menu/{menu_id})
#--------------------------------------------------------------------
# GET /menu/{menu_id} - Un USER connecté peut lire un item
def test_get_item_menu_ok(client, user_token, menu_id):
    response = client.get(
        f"/menu/{menu_id}",
        headers = {"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200


# GET /menu/{menu_id} - Item INEXISTANT donc impossible de le lire
def test_get_item_menu_ko(client, user_token):
    response = client.get(
        f"/menu/{444}",
        headers = {"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"


# Test GET /menu
#---------------------------------------------
# Test GET /menu - Un USER connecté peut lire la liste des items au menu
def test_get_list_menu(client, user_token, menu_ids):
    response = client.get(
        "/menu",
        headers = {"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200


# Test PUT /menu/{menu_id}
# ----------------------------------------
# Test PUT /menu/{menu_id} - Un admin peut modifier le menu
def test_delete_menu_ok(client, admin_token, menu_id):
    response = client.get(
        f"/menu/{menu_id}",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200


# Test - DELETE /menu/{menu_id}
#----------------------------------
# Test - DELETE /menu/{menu_id} - Un admin peut supprimer un produit au menu
def test_delete_menu_ko(client, admin_token, menu_id):
    response = client.delete(
        f"/menu/{menu_id}",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200

# Test - DELETE /menu/{menu_id} - Item inexistant donc impossible de le supprimer
def test_delete_menu_non_existing_item(client, admin_token):
    response = client.delete(
        f"/menu/{44}",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

