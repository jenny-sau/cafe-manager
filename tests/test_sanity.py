from fastapi.testclient import TestClient
from main import app


def test_health(client):
    """Test que l'endpoint /health fonctionne."""
    #GIVEN: On crée un client de test
    client = TestClient(app)

    #WHEN: On appelle GET /health
    response = client.get("/health")

    #THEN: on vérifie que ça réponse 200 et statut ok
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}