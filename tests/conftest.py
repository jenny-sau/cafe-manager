import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from database import get_db
from decimal import Decimal

# Créer une base de données en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

@pytest.fixture(autouse=True)
def disable_rate_limiter():
    app.state.limiter.enabled =False
@pytest.fixture(scope="function")
def db():
    """
    Crée une base de données fraîche pour chaque test.
    """
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)

    # Créer une session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Supprimer toutes les tables après le test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Crée un client de test qui utilise la DB de test.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


#---------------------------------------------------
# FIXTURE D'AUTH
#---------------------------------------------------
#Token utilisateur simple:
@pytest.fixture
def user_token(client):

    client.post("/auth/signup", json={
        "username": "user",
        "password": "secret",
        "money": "1000",
        "is_admin": False
    })

    login_response = client.post("/auth/login", json={
        "username": "user",
        "password": "secret"
    })

    token = login_response.json()["access_token"]
    return token

# Fixture pour un seconde user:
@pytest.fixture
def second_user_token(client):
    client.post("/auth/signup", json={
        "username": "user2",
        "password": "secret",
        "money": "1000",
        "is_admin": False
    })

    login = client.post("/auth/login", json={
        "username": "user2",
        "password": "secret"
    })

    return login.json()["access_token"]


#Token utilisateur ADMIN:
@pytest.fixture
def admin_token(client):

    client.post("/auth/signup", json={
        "username": "admin",
        "password": "secret",
        "is_admin": True
    })

    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "secret"
    })
    token = login_response.json()["access_token"]

    return token

# Header pour ADMIN
@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }

# Header pour user simple
@pytest.fixture
def user_headers(user_token):
    return {
        "Authorization": f"Bearer {user_token}"
    }

#Générer un id user
@pytest.fixture
def user_id(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Signup
    client.post("/auth/signup", json={
        "username": "jenny",
        "password": "secret",
        "is_admin": False
    })

    # Récupération du user (via route admin)
    response = client.get(
        "/users/1",  # ou une route /users?username=jenny si tu l’as
        headers=headers
    )

    assert response.status_code == 200
    return response.json()["id"]


#Créer un menu (admin)
@pytest.fixture
def menu_id(client, admin_token):
    # GIVEN: J'ai un token admin fourni par la fixture
    headers = {"Authorization": f"Bearer {admin_token}"}

    # WHEN: j'appelle une route admin
    response = client.post(
        "/menu",
        json={
            "name": "café",
            "purchase_price": "1.00",
            "selling_price": "1.20"
        },
        headers=headers,
    )

    # THEN: ça doit marcher
    assert response.status_code == 201
    menu_id= response.json()["id"]
    return menu_id

#Créer plusieurs item au menu(admin)
@pytest.fixture()
def menu_ids(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    ids = []

    for name in ["café", "latte", "espresso"]:
        response = client.post(
            "/menu",
            json={
                "name": name,
                "purchase_price": "1.0",
                "selling_price": "1.2"
            },
            headers=headers
        )
        assert response.status_code == 201
        ids.append(response.json()["id"])
    return ids

#Créer des produits dans l'inventaire
@pytest.fixture()
def inventory_item_id(client, user_token, menu_id):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post(
        "/order/restock",
        json = {
            "menu_item_id": menu_id,
            "quantity": 1
        },
        headers = headers
    )
    assert response.status_code == 200

    inventory_item_id = response.json()["id"]
    return inventory_item_id


#Créer une commande
@pytest.fixture()
def order_id (client, user_token, menu_id, inventory_item_id):
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
        headers = {"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    order_id = response.json()["order_id"]
    return order_id

# Créer des commandes pour 2 users différents:
@pytest.fixture
def second_order_id(client, second_user_token, menu_id, inventory_item_id):
    response = client.post(
        "/order/client",
        json={
            "items": [
                {"menu_item_id": menu_id, "quantity": 1}
            ]
        },
        headers = {"Authorization": f"Bearer {second_user_token}"}
    )

    return response.json()["order_id"]
