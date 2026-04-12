
# Test GET /inventory
#---------------------------------------------
#the user can view their inventory
def test_get_inventory_ok (client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        "/inventory",
        headers = headers
    )

    assert response.status_code == 200

#the user can view their inventory without a token
def test_get_inventory_no_token(client):
    response = client.get(
        "/inventory"
    )
    assert response.status_code == 403

# Test GET /inventory/{item_id}
#---------------------------------------------
# The user can view an item in the inventory.
def test_get_an_item_in_inventory_ok (client, user_token, inventory_item_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/inventory/{inventory_item_id}",
        headers = headers
    )
    assert response.status_code == 200

# the user can view an item in the inventory.
def test_get_inventory_item_not_mine(client, second_user_token, inventory_item_id):
    headers = {"Authorization": f"Bearer {second_user_token}"}
    response = client.get(f"/inventory/{inventory_item_id}", headers=headers)
    assert response.status_code == 404

# Item does not exist - Unable to view inventory item
def test_get_an_unexisting_item_inventory_ko(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/inventory/{44}",
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

# Test DELETE /admin/inventory/{item_id}
#--------------------------------------------
def test_delete_an_item_inventory_ok(client, admin_token, inventory_item_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/inventory/{inventory_item_id}",
        headers=headers
    )

    assert response.status_code == 200

# Item does not exist - Unable to delete item from inventory
def test_delete_an_unexisting_item_inventory_ko(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/inventory/{44}",
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory item not found"

