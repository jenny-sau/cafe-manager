# GET /game/stats
#---------------------------------------------

#An admin can view the game stats
def test_get_admin_game_stats(client, admin_token, order_id):
    response = client.get(
        "/game/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200

#A user can view their gaming history
def test_get_game_history(client, user_token, order_id):
    response = client.get(
        "/game/history",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200

#A user can view their stats
def test_get_game_stats(client, user_token, order_id):
    response = client.get(
        "/game/stats",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200

def test_get_game_stats_empty(client, user_token):
    response = client.get(
        "/game/stats",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200