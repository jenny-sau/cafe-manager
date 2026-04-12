#-----------------------------------------------
# Test on ORDERS
#----------------------------------------------

# Test POST /order/client
#---------------------------------------------
# Create an order OK
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

#Create an order with a product that doesn't exist -> 404
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
# The user can view their order -> 200
def test_get_an_orders_ok(client, user_token, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
            f"/orders/{order_id}",
            headers=headers
        )

    assert response.status_code == 200


# The command does not belong to the user -> 403
def test_get_an_order_not_mine_ko(client, admin_token, order_id):
    response = client.get(
        f"/orders/{order_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not your order"


# The command does not exist  -> 404
def test_get_an_unexisting_orders_ko(client, user_token):
    response = client.get(
        f"/orders/{44}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

# PATCH /orders/{order_id}/complete
#---------------------------------------------
# Successfully complete an order
def test_patch_order_complete_ok(client, user_token, menu_id, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.patch(
        f"/orders/{order_id}/complete",
        headers=headers
    )
    assert response.status_code == 200

# Order is not pending -> 404
def test_patch_order_complete_not_pending_ko(client, user_token, menu_id, order_id):
    client.patch(
        f"/orders/{order_id}/complete",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    response = client.patch(
        f"/orders/{order_id}/complete",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Order is not pending"

# Out of stock  -> 400
def test_patch_order_complete_not_enough_stock_ko(client, user_token, menu_id):
    response_order =(
        client.post(
            "/order/client",
            json={
                "items": [
                    {"menu_item_id": menu_id,
                    "quantity": 1}]
                },
                headers= {"Authorization": f"Bearer {user_token}"}
                   ))

    order_id = response_order.json()["order_id"]
    response = client.patch(
        f"/orders/{order_id}/complete",
        headers= {"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough stock"

# Not their order -> 403 (an admin is trying to complete an order created by a user)
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
# Order successfully canceled
def test_patch_order_cancel_ok(client, user_token, menu_id, order_id):
    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200


# Order is not pending -> 400
def test_patch_order_cancel_not_pending(client, user_token, menu_id, order_id):
    client.patch(
        f"/orders/{order_id}/complete",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Order is not pending"

#  Not his order -> 403
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
#An admin can see all orders
def test_admin_get_all_orders(client, admin_token, order_id, second_order_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        "/admin/orders",
        headers=headers
    )

    assert response.status_code == 200
