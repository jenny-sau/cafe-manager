#-----------------------------------------------
# Tester le métier de l'inventaire
#----------------------------------------------

# Test GET /inventory
#---------------------------------------------
#Test GET /inventory - user peut voir son inventaire
def test_get_inventory_ok (client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        "/inventory",
        headers = headers
    )

    assert response.status_code == 200

# Test GET /inventory/{item_id}
#---------------------------------------------
# Test GET /inventory/{item_id} - user peut voir un item de l'inventaire
def test_get_an_item_in_inventory_ok (client, user_token, inventory_item_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/inventory/{inventory_item_id}",
        headers = headers
    )

    assert response.status_code == 200

# Test GET /inventory/{item_id} - item inexistant - Impossible de consulter item de l'inventaire
def test_get_an_unexisting_item_inventory_ko(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/inventory/{44}",
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

# Test DELETE /admin/inventory/{item_id}
def test_delete_an_item_inventory_ok(client, admin_token, inventory_item_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/inventory/{inventory_item_id}",
        headers=headers
    )

    assert response.status_code == 200
#---------------------------------------------
# Test DELETE /admin/inventory/{item_id} - item inexistant - Impossible de supprimer item de l'inventaire
def test_delete_an_unexisting_item_inventory_ko(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/inventory/{44}",
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory item not found"