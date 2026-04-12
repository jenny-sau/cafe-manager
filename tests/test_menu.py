#-------------------------------------------------------------
#Test MENU
#----------------------------------------------

# Test POST /menu
#----------------------------------------------
# An ADMIN can create a menu item
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
# An user user can view an item
def test_get_item_menu_ok(client, user_token, menu_id):
    response = client.get(
        f"/menu/{menu_id}",
        headers = {"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200


# Item does not exist, so it cannot be read
def test_get_item_menu_ko(client, user_token):
    response = client.get(
        f"/menu/{444}",
        headers = {"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"


# Test GET /menu
#---------------------------------------------
# An USER can view the list of menu items
def test_get_list_menu(client, user_token, menu_ids):
    response = client.get(
        "/menu",
        headers = {"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200


# Test PUT /menu/{menu_id}
# ----------------------------------------
# An administrator can update the menu
def test_update_menu_ok(client, admin_token, menu_id):
    response = client.put(
        f"/menu/{menu_id}",
        json={
            "name": "café updated",
            "purchase_price": 1.50,
            "selling_price": 1.80
        },
        headers = {"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# Test - DELETE /menu/{menu_id}
#----------------------------------
# An administrator can remove a product from the menu
def test_delete_menu_ok(client, admin_token, menu_id):
    response = client.delete(
        f"/menu/{menu_id}",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

# The item does not exist, so it cannot be deleted
def test_delete_menu_non_existing_item(client, admin_token):
    response = client.delete(
        f"/menu/{44}",
        headers = {"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

