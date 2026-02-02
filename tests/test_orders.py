#-----------------------------------------------
# Tester le métier des commandes
#----------------------------------------------
from tests.conftest import user_token


# Test POST /order/client
#---------------------------------------------
#Test POST /order/client - Créer une commande OK
def test_post_order_ok(client, user_token, menu_id):
    response = client.post(
        "/order/client",
        json={
            "items": [
                {
                    "menu_item_id": menu_id,
                    "quantity": 1
                }
            ]
        },
        headers=  {"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200

#Test POST /order/client - Créer une commande avec produit inexistant -> 404
def test_post_order_unexisting_item_ko(client, user_token):
    response = client.post(
    "/order/client",
    json = {
        "items": [
            {
                "menu_item_id": 44,
                "quantity": 1
            }
        ]
    },
    headers = {"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

# GET /orders/{order_id}
#---------------------------------------------
# Test GET /orders/{order_id} - User peut voir sa commande
def test_get_an_orders_ok(client, user_token, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
            f"/orders/{order_id}",
            headers=headers
        )

    assert response.status_code == 200


# Test GET /orders/{order_id} - La commande n'appartient pas au user -> 403
def test_get_an_order_not_mine_ko(client, admin_token, order_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        f"/orders/{order_id}",
        headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not your order"


# Test GET /orders/{order_id} - La commande est inexistante -> 404
def test_get_an_unexisting_orders_ko(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/orders/{44}",
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

# PATCH /orders/{order_id}/complete
#---------------------------------------------
# Test PATCH /orders/{order_id}/complete - Compléter une commande avec succès
def test_patch_order_complete_ok(client, user_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )
    assert response.status_code == 200

# TestPATCH /orders/{order_id}/complete - Commande n'est pas pending -> 404
def test_patch_order_complete_not_pending_ko(client, user_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )

    response = client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Order is not pending"

# Test PATCH /orders/{order_id}/complete - Stock insuffisant -> 400
def test_patch_order_complete_not_enough_stock_ko(client, user_token, menu_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response_order =(
        client.post(
            "/order/client",
            json={
                "items": [
                    {"menu_item_id": menu_id,
                    "quantity": 1}]
                },
                headers=headers
                   ))

    order_id = response_order.json()["order_id"]

    response = client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough stock"

# Test PATCH /orders/{order_id}/complete - Pas sa commande -> 403 (un admin essaie de compléter commande créer par user)
def test_patch_order_complet_not_mine(client, admin_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not your order"

# PATCH /orders/{order_id}/cancel
#---------------------------------------------
# PATCH /orders/{order_id}/cancel - Commande annulée avec succès
def test_patch_order_cancel_ok(client, user_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert response.status_code == 200


# PATCH /orders/{order_id}/cancel - Commande n'est pas pending -> 400
def test_patch_order_cancel_not_pending(client, user_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )

    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Order is not pending"

# PATCH  /orders/{order_id}/cancel - Pas sa commande -> 403
def test_patch_order_cancel_not_mine(client, admin_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not your order"

# Test GET /admin/orders
#---------------------------------------------
#Test GET /admin/orders - Un admin voit toutes les commandes
def test_admin_get_all_orders(client, admin_token, order_id, second_order_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        "/admin/orders",
        headers=headers
    )

    assert response.status_code == 200
