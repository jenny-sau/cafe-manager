[🇫🇷 Français](README.md) | 🇬🇧 English

# Café Manager API

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

A backend REST API for a café management game, simulating real business workflows: inventory management, customer orders, financial transactions, and player progression.

**Tech stack:** FastAPI · PostgreSQL · SQLAlchemy · JWT · Docker · Pytest

---

## Overview

Café Manager is a management game where players start with a budget, buy products, serve customers, and grow their café.

**Example gameplay flow:**

```
Initial budget: €100
  ↓
Buy 20 coffees (€30) → Stock: 20 coffees, Money: €70
  ↓
Customer orders 3 coffees → Stock: 17 coffees, Money: €79
  ↓
Level up, new products unlocked

```
### Structured Swagger UI
![Swagger overview](./screenshots/swagger-overview.png)

### Business workflow example
![Order workflow](./screenshots/swagger-order-example.png)

### Why this project?

This project was built as a personal learning project to strengthen backend development skills:

- Designing a complete REST API from scratch

- Implementing real business logic (transactions, validations, state machines)

- Understanding modern backend architecture (auth, database, testing)

---

## Features

### For players
- **Authentication** : Signup, login, JWT-based auth (24h expiration)
- **Restocking** : Buy products to manage inventory
- **Inventory** : View current stock
- **Customer** : Serve or cancel customer requests

- **Statistics** : Track profits, level, and history

### For admins
- **Menu management** : Create, update, delete products
- **User management** : Full CRUD
- **Global statistics** : Game-wide overview

---

## Installation

### Requirements
- Python 3.11+
- Docker & Docker Compose

### Steps
```bash
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
docker compose up -d

uvicorn main:app --reload
```

** API available at :** http://127.0.0.1:8000  
**Swagger docs:** http://127.0.0.1:8000/docs

---

## Quick start

### 1. Create an account
```bash
POST /auth/signup
```
```json
{
  "username": "maria",
  "password": "secret123",
  "money": 100.0,
  "is_admin": true,
}
> Creating an admin account allows you to test all features.
```

### 2. Login
```bash
POST /auth/login
```
```json
{
  "username": "maria",
  "password": "secret123"
}
```

**Response :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the token

In Swagger UI: (http://127.0.0.1:8000/docs) :
1. Click **"Authorize"** 
2. Paste the JWT token
3. Access all protected endpoints

### 4. Test a complete workflow
```bash
# See the menu
GET /menu

# Buy 10 coffees
POST /order/restock
{
  "item_id": 1,
  "quantity": 10
}

# Check your inventory
GET /inventory

# A customer order arrives
POST /order/client
{
  "item_id": 1,
  "quantity": 2
}

# Serving the customer
PATCH /order/{order_id}/complete
```

---

## How it works

### Restocking workflow
```
Player wants to buy 10 coffees (€1.50/unit)
          ↓
API checks available funds (€15 required)

          ↓
    YES                 NO
     ↓                   ↓
Stock +10          400 error
Money -€15      "Insufficient funds"
Action logged
```

### Customer order workflow
```
Customer orders 2 coffees (sale price: €3 per unit)
          ↓
Order created (status: PENDING)
          ↓
Player serves the order
          ↓
API checks stock availability
          ↓
    YES                NO
     ↓                  ↓
Stock -2          400 error
Money +€6         "Insufficient stock"
Status: COMPLETED

```

### Order lifecycle

Orders follow a strict state machine:
```
PENDING → COMPLETED   (stock decremented, money credited)
   ↓
CANCELLED            (no effect on stock or money)

```

**Forbidden transitions:**
- `COMPLETED → PENDING`
- `CANCELLED → COMPLETED`

---

## Architecture

### Database models

| Table | Description |
|-------|-------------|
| **User** | Players and administrators |
| **MenuItem** | Products available in the café |
| **Inventory** | Player stock |
| **Order** | Orders with status (pending/completed/cancelled) |
| **GameLog** | Full action history |
| **PlayerProgress** | Player level and statistics |

### Main endpoints

#### Authentication (public)

```
POST   /auth/signup    Create an account
POST   /auth/login     Log in (JWT)
```

#### Menu
```
GET    /menu           List available products
POST   /menu           Create a product (admin)
PUT    /menu/{id}      Update a product (admin)
DELETE /menu/{id}      Delete a product (admin)
```

#### Inventory & Orders (authenticated)
```
POST   /order/restock         Buy inventory stock
GET    /inventory             View inventory
POST   /order/client          Create a customer order
PATCH  /order/{id}/complete   Complete an order
PATCH  /order/{id}/cancel     Cancel an order

```

#### Statistics
```
GET    /game/history    Personal action history
GET    /game/stats      Personal statistics
GET    /admin/stats     Global statistics (admin)
```

---

## Skills demonstrated

### Backend & API
- REST API architecture with **FastAPI** (routes, dependencies, automatic validation)
- Dependency injection for authentication
- Auto-generated documentation (OpenAPI / Swagger)

### Database
- Relational data modeling with **SQLAlchemy** (one-to-many relationships, foreign keys)
- Schema migrations using **Alembic**
- Atomic transactions (stock and money updated together or not at all)

### Security
- **JWT** authentication with expiration (24h)
- Password hashing using **bcrypt**
- Role-based access control (RBAC: admin vs player)

### Business logic
- State machine for order processing (controlled transitions)
- Business rule validations (sufficient stock, available funds)
- Automated calculations (profits, costs)

### DevOps & Testing
- PostgreSQL containerization with **Docker**
- Automated testing with **pytest** (authentication, permissions, business logic)
- Separate environments for development (5432) and testing (5433)


---

## Tests

Automated tests using **pytest** cover:

### Authentication
- User signup and data validation
- Duplicate handling (username already exists)
- Login and JWT generation
- Error cases: invalid credentials, missing or expired token

### Permissions
- Authorized access for authenticated users
- Blocking unauthenticated access (401)
- Admin route restrictions (403 for players)

### Business logic
- Restocking workflow (balance verification)
- Inventory management (increments and decrements)
- Customer orders (full workflow: PENDING → COMPLETED)
- Error cases: insufficient stock, insufficient funds

**All tests are currently passing ✅**
```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

---
## Configuration

### Used ports

| Service | Port | Description |
|--------|------|-------------|
| PostgreSQL (dev) | 5432 | Main database |
| PostgreSQL (test) | 5433 | Database used for pytest |
| FastAPI | 8000 | API |

**Important:** No PostgreSQL instance should be running natively on Windows. Everything is handled via Docker.

### Security

**Security note:** The `SECRET_KEY` in `auth.py` is currently hardcoded for development purposes.

**In production, use environment variables:**
```bash
# Method 1: Direct export
export SECRET_KEY="your-ultra-secure-32-character-key"

# Method 2: .env file
# .env
SECRET_KEY=your-ultra-secure-key
DATABASE_URL=postgresql://user:pass@host/db
