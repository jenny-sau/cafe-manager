# Café Manager API

[English](#english) | [Français](#français)

---

<a name="english"></a>
## 🇬🇧 English

A REST API to manage a café with its menu, inventory, and orders. I built this project to learn FastAPI and JWT authentication.

### What I learned

While developing this API, I worked on:
- Building a REST API with FastAPI
- JWT authentication and password hashing
- Database management with SQLAlchemy
- Route protection and permission handling
- Data validation with Pydantic

### Features

- Create an account and log in
- Manage the café menu (add, edit, delete products)
- Track inventory in real-time
- Place orders (automatically decreasing stock)
- Restock inventory

### Technologies

- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM for database management
- **SQLite** - Database (easy to start with)
- **JWT** - For authentication
- **bcrypt** - To secure passwords

### Installation

Clone the project:
```bash
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager
```

Create a virtual environment and install dependencies:
```bash
python -m venv mon_env
mon_env\Scripts\activate  # On Windows
pip install -r requirements.txt
```

Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000

Interactive documentation at http://127.0.0.1:8000/docs

### How to use the API

#### Create an account
```
POST /auth/signup
```
```json
{
  "username": "your_username",
  "password": "your_password",
  "money": 100.0
}
```

#### Log in
```
POST /auth/login
```
You'll receive a JWT token valid for 24h.

#### Use the token

On Swagger (interactive docs), click the "Authorize" button and paste your token.

For your own requests, add the header:
```
Authorization: Bearer your_token
```

### Main endpoints

**Menu** (public access)
- `GET /menu` - List products
- `POST /menu` - Add a product
- `PUT /menu/{id}` - Update a product
- `DELETE /menu/{id}` - Delete a product

**Inventory** (authentication required)
- `POST /inventory` - Create an inventory item
- `GET /inventory` - View all inventory
- `PUT /inventory/{id}` - Update quantities

**Orders** (authentication required)
- `POST /order/client` - Place an order (decreases stock)
- `POST /order/restock` - Restock (increases stock)

### Code structure
```
cafe_manager/
├── main.py          # Routes and endpoints
├── models.py        # Database models
├── schemas.py       # Data validation
├── database.py      # DB configuration
├── auth.py          # Authentication management
└── cafe.db          # Database (auto-generated)
```

### What I want to improve

- Migrate to PostgreSQL for production
- Add automated tests
- Implement a role system (admin vs user)
- Add pagination on lists
- Set up CI/CD

### Tests performed

I manually tested with Swagger:
- Account creation and login
- Route protection (without token → 403 error)
- Invalid tokens properly rejected
- Stock management working correctly

### Notes

This project is part of my backend development learning journey. The default password should be changed in production, and more validations and error handling would be needed for real-world use.

---

<a name="français"></a>
## 🇫🇷 Français

Une API REST pour gérer un café avec son menu, son stock et ses commandes. J'ai construit ce projet pour apprendre FastAPI et l'authentification JWT.

### Ce que j'ai appris

En développant cette API, j'ai travaillé sur :
- La création d'une API REST avec FastAPI
- L'authentification avec JWT et le hachage de mots de passe
- La gestion d'une base de données avec SQLAlchemy
- La protection de routes et la gestion des permissions
- La validation de données avec Pydantic

### Fonctionnalités

- Créer un compte et se connecter
- Gérer le menu du café (ajouter, modifier, supprimer des produits)
- Suivre l'inventaire en temps réel
- Passer des commandes (qui diminuent automatiquement le stock)
- Réapprovisionner l'inventaire

### Technologies

- **FastAPI** - Framework web Python
- **SQLAlchemy** - ORM pour gérer la base de données
- **SQLite** - Base de données (facile pour commencer)
- **JWT** - Pour l'authentification
- **bcrypt** - Pour sécuriser les mots de passe

### Installation

Cloner le projet :
```bash
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager
```

Créer un environnement virtuel et installer les dépendances :
```bash
python -m venv mon_env
mon_env\Scripts\activate  # Sur Windows
pip install -r requirements.txt
```

Lancer l'application :
```bash
uvicorn main:app --reload
```

L'API sera disponible sur http://127.0.0.1:8000

La documentation interactive est sur http://127.0.0.1:8000/docs

### Comment utiliser l'API

#### Créer un compte
```
POST /auth/signup
```
```json
{
  "username": "votre_username",
  "password": "votre_password",
  "money": 100.0
}
```

#### Se connecter
```
POST /auth/login
```
Vous recevrez un token JWT valide 24h.

#### Utiliser le token

Sur Swagger (la doc interactive), cliquez sur le bouton "Authorize" et collez votre token.

Pour vos propres requêtes, ajoutez le header :
```
Authorization: Bearer votre_token
```

### Endpoints principaux

**Menu** (accessible à tous)
- `GET /menu` - Liste des produits
- `POST /menu` - Ajouter un produit
- `PUT /menu/{id}` - Modifier un produit
- `DELETE /menu/{id}` - Supprimer un produit

**Inventaire** (authentification requise)
- `POST /inventory` - Créer un item d'inventaire
- `GET /inventory` - Voir tout l'inventaire
- `PUT /inventory/{id}` - Modifier les quantités

**Commandes** (authentification requise)
- `POST /order/client` - Passer une commande (diminue le stock)
- `POST /order/restock` - Réapprovisionner (augmente le stock)

### Structure du code
```
cafe_manager/
├── main.py          # Routes et endpoints
├── models.py        # Modèles de la base de données
├── schemas.py       # Validation des données
├── database.py      # Configuration DB
├── auth.py          # Gestion de l'authentification
└── cafe.db          # Base de données (générée automatiquement)
```

### Ce que je veux améliorer

- Migrer vers PostgreSQL pour la production
- Ajouter des tests automatiques
- Implémenter un système de rôles (admin vs utilisateur)
- Ajouter la pagination sur les listes
- Configurer un CI/CD

### Tests effectués

J'ai testé manuellement avec Swagger :
- Création de compte et connexion
- Protection des routes (sans token → erreur 403)
- Tokens invalides bien rejetés
- Gestion du stock qui fonctionne correctement

### Notes

Ce projet fait partie de mon apprentissage du développement backend. Le mot de passe par défaut devrait être changé en production, et il faudrait ajouter plus de validations et de gestion d'erreurs pour un usage réel.