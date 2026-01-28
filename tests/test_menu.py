#-------------------------------------------------------------
#Tester le métier du menu
#----------------------------------------------

# Test POST /menu
#----------------------------------------------
# POST /menu - Un ADMIN peut créer un item au menu
def test_create_ok(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        "/menu",
        json={
            "name": "café",
            "purchase_price": 1.0,
            "selling_price": 1.2
        },
        headers=headers,
    )

    assert response.status_code == 201


# POST /menu - Un user ne peut pas créer un item au menu
def test_create_non_admin(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post(
        "/menu",
        json={
            "name": "café",
            "purchase_price": 1.0,
            "selling_price": 1.2
        },
        headers=headers
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Accès refusé : Vous devez être admin"

# POST /menu - Sans token -> Impossible de créer un item au menu
def test_create_menu_without_token(client):
    response = client.post(
        "/menu",
        json= {
            "name": "café",
            "purchase_price": "1",
            "selling_price": "1.2"
        }
    )

    assert response.status_code ==403
    data = response.json()
    assert data["detail"] == "Not authenticated"

# POST /menu - Token invalide, impossible de créer un item au menu
def test_create_menu_wrong_token(client, admin_token):
    token = "totally.invalid.token"

    response = client.post(
        "/menu",
        json={
            "name": "latte",
            "purchase_price": 1.0,
            "selling_price": 1.2
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401

# Test (GET /menu/{menu_id})
#--------------------------------------------------------------------
# GET /menu/{menu_id} - Un USER connecté peut lire un item
def test_get_item_menu_ok(client, user_token, menu_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/menu/{menu_id}",
        headers=headers
    )

    assert response.status_code == 200


# GET /menu/{menu_id} - Sans token impossible de lire un item au menu
def test_get_item_menu_without_token(client, menu_id):

    response = client.get(
        f"/menu/{menu_id}",
    )

    assert response.status_code ==403
    data = response.json()
    assert data["detail"] == "Not authenticated"


# GET /menu/{menu_id} - Token invalide, impossible de lire un item au menu
def test_get_item_menu_wrong_token(client, user_token, menu_id):
    token = "totally.invalid.token"

    response = client.get(
        f"/menu/{menu_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 401


# GET /menu/{menu_id} - Item INEXISTANT -> impossible de le lire
def test_get_item_menu_ko(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        f"/menu/{444}",
        headers=headers
    )

    assert response.status_code == 404


# Test GET /menu
#---------------------------------------------
# Test GET /menu - Un USER connecté peut lire la liste des items au menu
def test_get_list_menu(client, user_token, menu_ids):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/menu", headers=headers)

    assert response.status_code == 200


# Test GET /menu - Sans TOKEN, impossible de lire la liste des produits au menu
#-------------------------------------
def test_get_list_menu_no_token(client, menu_ids):
    response = client.get("/menu")

    assert response.status_code == 403

# Test GET /menu - Token invalide impossible de lire la liste des produits au menu
def test_get_list_menu_wrong_token(client, menu_ids):
    token = "totally.invalid.token"

    response = client.get(
        "/menu",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401

# Test PUT /menu/{menu_id}
# ----------------------------------------
# Test PUT /menu/{menu_id} - Un admin peut modifier le menu
def test_delete_menu_ok(client, admin_token, menu_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        f"/menu/{menu_id}",
        headers=headers
    )

    assert response.status_code == 200

# Test - DELETE /menu/{menu_id}
#----------------------------------
# Test - DELETE /menu/{menu_id} - Un admin peut supprimer un produit au menu
def test_delete_menu_ko(client, admin_token, menu_id):
    headers =  {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/menu/{menu_id}",
        headers = headers
    )

    assert response.status_code == 200

# Test - DELETE /menu/{menu_id} - Item inexistant impossible de modifier le menu-
def test_delete_menu_ok(client, admin_token):
    headers =  {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/menu/{44}",
        headers = headers
    )

    assert response.status_code == 404

# Item inexistant -> Impossible de le supprimer
def test_delete_menu_ko(client, admin_token):
    headers =  {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(
        f"/menu/{44}",
        headers = headers
    )

    assert response.status_code == 404

