🇬🇧 English | [🇫🇷 Français](README.md)

# Café Manager API

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)

A REST API backend for a café management game, with complete business logic: restocking, inventory, customer orders, and player progression.

**Tech Stack:** FastAPI · PostgreSQL · SQLAlchemy · JWT · Docker · Pytest

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Skills Developed](#skills-developed)
- [Tests](#tests)
- [Future Improvements](#future-improvements)
- [What I Learned](#what-i-learned)
- [Configuration](#configuration)

---

## Overview

Café Manager is a management game where the player starts with a budget, buys products, serves customers, and grows their café.

**Example gameplay:**
```
Starting budget: 100€
  ↓
Buy 20 coffees (30€) → Stock: 20 coffees, Money: 70€
  ↓
Customer orders 3 coffees → Stock: 17 coffees, Money: 79€
  ↓
Level up, new products unlocked 
```

### Structured Swagger UI
![Swagger overview](screenshots/swagger-overview.png)

### Business Workflow Example
![Order workflow](screenshots/swagger-order-example.png)

### Why This Project?

Personal learning project to master backend development:
- Build a complete REST API from scratch
- Implement business logic (transactions, validations, states)
- Understand modern application architecture (auth, DB, tests)

---

## Features

### For Players
- **Authentication**: Sign up, login, JWT (24h)
- **Restocking**: Buy products for inventory
- **Inventory**: Check current stock 
- **Customer Orders**: Serve or cancel requests
- **Statistics**: Track profits, level, history

### For Admins
- **Menu Management**: Add/modify/delete products
- **User Management**: Full CRUD
- **Global Stats**: Game overview

---

## Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose

### Steps
```bash
# 1. Clone the project
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager

# 2. Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch PostgreSQL (Docker)
docker compose up -d

# 5. Launch API
uvicorn main:app --reload
```

**API available at:** http://127.0.0.1:8000  
**Interactive documentation:** http://127.0.0.1:8000/docs

---

## Quick Start

### 1. Create an Account
```bash
POST /auth/signup
```
```json
{
  "username": "maria",
  "password": "secret123",
  "money": 100.0,
  "is_admin": true
}
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

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the Token

In Swagger UI (http://127.0.0.1:8000/docs):
1. Click the **"Authorize"** button
2. Paste the token
3. All protected endpoints are now accessible!

### 4. Test a Complete Workflow
```bash
# View menu
GET /menu

# Buy 10 coffees
POST /order/restock
{
  "item_id": 1,
  "quantity": 10
}

# Check inventory
GET /inventory

# Customer order arrives
POST /order/client
{
  "item_id": 1,
  "quantity": 2
}

# Serve the customer
PATCH /order/{order_id}/complete
```

---

## How It Works

### Workflow: Restocking
```
Player wants to buy 10 coffees at 1.50€/unit
          ↓
API checks: does player have 15€?
          ↓
    YES                 NO
     ↓                   ↓
Stock +10          Error 400
Money -15€         "Insufficient funds"
Action logged
```

### Workflow: Customer Order
```
Customer orders 2 coffees (selling price: 3€/unit)
          ↓
Order created (status: PENDING)
          ↓
Player clicks "Serve"
          ↓
API checks: 2 coffees in stock?
          ↓
    YES                 NO
     ↓                   ↓
Stock -2           Error 400
Money +6€          "Insufficient stock"
Status: COMPLETED
```

### Order Lifecycle

Orders follow a status validation system:
```
PENDING → COMPLETED  (stock decremented, money credited)
   ↓
CANCELLED (no effect on stock/money)
```

**Forbidden transitions:**
- `COMPLETED → PENDING`
- `CANCELLED → COMPLETED`

These transitions are validated via guards (`if status != PENDING`) in the endpoints.

---

## Architecture

### Models (Database)

| Table | Description                                        |
|-------|----------------------------------------------------|
| **User** | Players and administrators                         |
| **MenuItem** | Menu products (coffee, croissant...)              |
| **Inventory** | Current stock for each player                      |
| **Order** | Orders with status (pending/completed/cancelled) |
| **GameLog** | Complete action history                     |
| **PlayerProgress** | Level and player statistics                 |

### Main Endpoints

#### Authentication (public)
```
POST   /auth/signup    Create account
POST   /auth/login     Login (JWT)
```

#### Menu
```
GET    /menu           List products
POST   /menu           Add product (admin)
PUT    /menu/{id}      Modify product (admin)
DELETE /menu/{id}      Delete product (admin)
```

#### Inventory & Orders (authenticated)
```
POST   /order/restock         Buy stock
GET    /inventory             Check inventory
POST   /order/client          New customer order
PATCH  /order/{id}/complete   Serve customer
PATCH  /order/{id}/cancel     Cancel order
```

#### Statistics
```
GET    /game/history    Personal history
GET    /game/stats      Personal statistics
GET    /admin/stats     Global stats (admin)
```

---

## Skills Developed

### Backend & API
- REST architecture with **FastAPI** (routes, dependencies, automatic validation)
- Dependency injection for authentication
- Auto-generated documentation (OpenAPI/Swagger)
- Data validation with **Pydantic**

### Database
- Relational modeling with **SQLAlchemy** (One-to-Many relations, Foreign Keys)
- Schema migrations with **Alembic**
- Error handling with try/except and rollback

### Security
- **JWT** authentication with expiration (24h)
- Password hashing with **bcrypt**
- Role management (admin vs player)
- Rate limiting with **slowapi** (anti-spam protection)

### Business Logic
- Status transition validation (PENDING → COMPLETED/CANCELLED)
- Business validations (sufficient stock, available funds)
- Automatic calculations (profits, costs)
- Logging system for action history

### DevOps & Tests
- Containerization with **Docker** (PostgreSQL)
- Automated tests with **pytest** (auth, permissions, logic)
- Managing two environments (dev:5432, test:5433)

---

## Tests

Automated tests with **pytest** covering:

### Authentication
- Sign up and data validation
- Handling duplicates (username already taken)
- Login and JWT generation
- Error cases: invalid credentials, missing/expired token

### Permissions
- Access for authenticated users
- Blocking unauthenticated users (401)
- Admin route restrictions (403 for players)

### Business Logic
- Restocking (balance verification)
- Inventory management (increments/decrements)
- Customer orders (complete PENDING → COMPLETED workflow)
- Error cases: insufficient stock, insufficient funds

**Current Coverage:**
- Unit tests (happy path)
- Error tests (edge cases)

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

---

## Future Improvements

### Planned Technical Improvements

- Implementation of structured logging (INFO/WARNING/ERROR levels)
- Code refactoring to reduce repetition
- Additional tests covering extreme cases and edge scenarios
- Overall maintainability improvements

---

## What I Learned

Beyond the code, this project helped me understand:

**Technical Concepts:**
- How to structure a REST API with multiple user types (admin/player)
- The importance of proper error handling to avoid database inconsistencies
- Thinking about what happens when multiple users use the API simultaneously
- How to write tests that verify not only that things work, but also that they fail correctly

**General Skills:**
- Reading technical documentation (FastAPI, SQLAlchemy, pytest)
- Analyzing my own code to identify its limitations
- Being honest about what I master vs. what I still need to learn

---

## Configuration

### Used Ports

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL (dev) | 5432 | Main database |
| PostgreSQL (test) | 5433 | Database for pytest |
| FastAPI | 8000 | API |

**Important:** No PostgreSQL should run natively on Windows. Everything is managed via Docker.

### Security

**Security Note:** The `SECRET_KEY` in `auth.py` is currently hardcoded for development.

**In production, use environment variables:**
```bash
# Method 1: Direct export
export SECRET_KEY="your-ultra-secure-32-character-key"

# Method 2: .env file
# .env
SECRET_KEY=your-ultra-secure-key
DATABASE_URL=postgresql://user:pass@host/db
```

Then load with `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

**Questions?** Feel free to open an issue or contact me: jenny.saucy@outlook.com :)