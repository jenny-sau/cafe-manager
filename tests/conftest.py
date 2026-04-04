import os
os.environ["SECRET_KEY"] = "test-secret-key"


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from database import get_db
import pytest


#  Create an in-memory database for testing
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
    app.state.limiter.enabled = False

@pytest.fixture(scope="function")
def db():
    """
    Creates a new database for each test.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Delete all tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client that uses the test database.
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


#--------------------------------------------------------------------

#Token for USER:
@pytest.fixture
def user_token(client):

    client.post("/auth/signup", json={
        "username": "user",
        "password": "Secret1",
        "money": "1000",
        "is_admin": False
    })

    login_response = client.post("/auth/login", json={
        "username": "user",
        "password": "Secret1"
    })

    token = login_response.json()["access_token"]
    return token

# Fixture for a secondary user:
@pytest.fixture
def second_user_token(client):
    client.post("/auth/signup", json={
        "username": "user2",
        "password": "Secret1",
        "money": "1000",
        "is_admin": False
    })

    login = client.post("/auth/login", json={
        "username": "user2",
        "password": "Secret1"
    })

    return login.json()["access_token"]


#Token ADMIN:
@pytest.fixture
def admin_token(client, db):

    client.post("/auth/signup", json={
        "username": "admin",
        "password": "Secret1",

    })
    from models import User
    user = db.query(User).filter(User.username == "admin").first()
    user.is_admin = True
    db.commit()

    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "Secret1"
    })
    token = login_response.json()["access_token"]

    return token

# Header for user
@pytest.fixture
def user_headers(user_token):
    return {
        "Authorization": f"Bearer {user_token}"
    }


# Header for ADMIN
@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }

# Generate a user ID
@pytest.fixture
def user_id(client, db):

    client.post("/auth/signup", json={
        "username": "jenny",
        "password": "Secret1",
        "is_admin": False
    })

    from models import User
    user = db.query(User).filter(User.username == "jenny").first()

    assert user is not None

    return user.id

#Create a menu (admin)
@pytest.fixture
def menu_id(client, admin_token):
    # GIVEN: I have an admin token provided by the fixture
    headers = {"Authorization": f"Bearer {admin_token}"}

    # WHEN: I call an ADMIN only endpoint
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

#Create multiple menu items (admin)
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

#Create products in the inventory
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


#Place an order
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

# Create orders for two different users:
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
    assert response.status_code == 200
    return response.json()["order_id"]
