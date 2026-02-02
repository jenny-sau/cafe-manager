# GET /game/stats
#---------------------------------------------
#Test GET /admin/orders - Un admin peut voir les stats du jeu
def test_get_admin_game_stats(client, admin_token, order_id):
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(
        "/game/stats",
        headers=headers
    )

    assert response.status_code == 200

#Test GET /game/history - Un user peut consulter son historique de jeu
def test_get_game_history(client, user_token, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        "/game/history",
        headers=headers
    )

    assert response.status_code == 200

#Test GET /game/stats - Un user peut consulter ses stats
def test_get_game_stats(client, user_token, order_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get(
        "/game/stats",
        headers=headers
    )

    assert response.status_code == 200
