# Café Manager API

[English](#english) | [Français](#français)

---

<a name="english"></a>
## 🇬🇧 English

Backend API for a café management game built with FastAPI.

Players start with a budget, buy products, serve customers, and manage inventory. The API handles all the logic: stock verification, money calculations, and authentication.

### Why this project

I'm learning backend development and FastAPI. Instead of making yet another basic CRUD app, I added game logic to have more interesting problems to solve.

### Installation
```bash
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs on http://127.0.0.1:8000  
Interactive docs: http://127.0.0.1:8000/docs

### Quick start

1. **Create account**: `POST /auth/signup` with username, password, and starting money
2. **Login**: `POST /auth/login` to get a JWT token (valid 24h)
3. **Use token**: On Swagger, click "Authorize" and paste your token
4. **Try protected endpoints**: inventory, orders

Example signup:
```json
POST /auth/signup
{
  "username": "your_username",
  "password": "your_password",
  "money": 100.0
}
```

### Main endpoints

**Public:**
- `GET /menu` - List products
- `POST /menu` - Add product
- `PUT /menu/{id}` - Update product
- `DELETE /menu/{id}` - Delete product

**Protected (need JWT token):**
- `POST /inventory` - Create inventory item
- `GET /inventory` - View your stock
- `PUT /inventory/{id}` - Update quantities
- `POST /order/client` - Place order (stock decreases, money increases)
- `POST /order/restock` - Restock (stock increases, money decreases)

### How it works

When a player places an order:
1. API checks if enough stock
2. If yes: decreases inventory, increases player's money
3. If no: returns error

When restocking:
1. API checks if player has enough money
2. If yes: increases inventory, decreases money
3. If no: returns error

### Tech stack

- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Database (good for dev, will migrate to PostgreSQL later)
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing
- **Pydantic** - Data validation

### Project structure
```
cafe_manager/
├── main.py          # FastAPI routes
├── models.py        # Database models (User, MenuItem, Inventory, Order)
├── schemas.py       # Pydantic schemas for validation
├── database.py      # Database configuration
├── auth.py          # JWT functions + password hashing
└── cafe.db          # SQLite database (auto-generated)
```

I split everything into separate files because having it all in `main.py` was getting messy.

### What I learned

While building this, I worked on:
- FastAPI (routes, dependencies, validation)
- SQLAlchemy (ORM, relationships between tables)
- JWT authentication and password hashing
- Project structure (separating models, schemas, auth)
- Business logic (stock checks, money calculations)
- How to design an API that does more than basic CRUD

### What I want to improve

Currently functional but missing:
- Automated tests (using pytest)
- PostgreSQL instead of SQLite
- Role system (admin vs regular user)
- Pagination for large lists
- Actual game frontend
- CI/CD pipeline

Game features to add:
- Events (morning rush, promotions)
- Player stats (money earned, best-selling product)
- Achievements system
- Multiplayer leaderboard

### Testing

I've manually tested via Swagger:
- Account creation + login: works
- Invalid/expired tokens: properly rejected
- Ordering without enough stock: correct error
- Ordering without money: correct error
- Stock updates after order: works
- Protected routes without token: 403 error

Need to automate this with pytest.

### Notes

The `SECRET_KEY` in `auth.py` is hardcoded for development. In production it should be in an environment variable.

If you want to test it, easiest way is to create an account on Swagger, login, and try placing orders.

### License

MIT - do whatever you want with it

---

<a name="français"></a>
## 🇫🇷 Français

API backend pour un jeu de gestion de café développé avec FastAPI.

Le joueur démarre avec un budget, achète des produits, sert des clients et gère son stock. L'API gère toute la logique : vérification du stock, calcul de l'argent, authentification.

### Pourquoi ce projet

J'apprends le développement backend et FastAPI. Plutôt que faire un énième CRUD basique, j'ai ajouté de la logique de jeu pour avoir des problèmes plus intéressants à résoudre.

### Installation
```bash
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager
python -m venv venv
venv\Scripts\activate  # Sur Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

L'API tourne sur http://127.0.0.1:8000  
Doc interactive : http://127.0.0.1:8000/docs

### Démarrage rapide

1. **Créer un compte** : `POST /auth/signup` avec username, password et argent de départ
2. **Se connecter** : `POST /auth/login` pour recevoir un token JWT (valide 24h)
3. **Utiliser le token** : Sur Swagger, cliquer "Authorize" et coller le token
4. **Tester les endpoints protégés** : inventory, orders

Exemple d'inscription :
```json
POST /auth/signup
{
  "username": "votre_username",
  "password": "votre_password",
  "money": 100.0
}
```

### Endpoints principaux

**Publics :**
- `GET /menu` - Liste des produits
- `POST /menu` - Ajouter un produit
- `PUT /menu/{id}` - Modifier un produit
- `DELETE /menu/{id}` - Supprimer un produit

**Protégés (nécessitent un token JWT) :**
- `POST /inventory` - Créer un item d'inventaire
- `GET /inventory` - Voir son stock
- `PUT /inventory/{id}` - Modifier les quantités
- `POST /order/client` - Passer une commande (stock diminue, argent augmente)
- `POST /order/restock` - Réapprovisionner (stock augmente, argent diminue)

### Comment ça fonctionne

Quand un joueur passe une commande :
1. L'API vérifie s'il y a assez de stock
2. Si oui : diminue l'inventaire, augmente l'argent du joueur
3. Si non : renvoie une erreur

Lors d'un réapprovisionnement :
1. L'API vérifie si le joueur a assez d'argent
2. Si oui : augmente l'inventaire, diminue l'argent
3. Si non : renvoie une erreur

### Stack technique

- **FastAPI** - Framework web Python
- **SQLAlchemy** - ORM pour la base de données
- **SQLite** - Base de données (bien pour le dev, migration vers PostgreSQL prévue)
- **JWT** - Authentification par tokens
- **bcrypt** - Hash des mots de passe
- **Pydantic** - Validation des données

### Structure du projet
```
cafe_manager/
├── main.py          # Routes FastAPI
├── models.py        # Modèles de base de données (User, MenuItem, Inventory, Order)
├── schemas.py       # Schémas Pydantic pour validation
├── database.py      # Configuration base de données
├── auth.py          # Fonctions JWT + hash des passwords
└── cafe.db          # Base SQLite (générée automatiquement)
```

J'ai tout séparé dans des fichiers différents parce que tout mettre dans `main.py` devenait illisible.

### Ce que j'ai appris

En développant ce projet, j'ai travaillé sur :
- FastAPI (routes, dépendances, validation)
- SQLAlchemy (ORM, relations entre tables)
- Authentification JWT et hash des mots de passe
- Structure de projet (séparer models, schemas, auth)
- Logique métier (vérification stock, calcul argent)
- Comment concevoir une API qui fait plus que du CRUD basique

### Ce que je veux améliorer

Actuellement fonctionnel mais il manque :
- Tests automatiques (avec pytest)
- PostgreSQL à la place de SQLite
- Système de rôles (admin vs utilisateur normal)
- Pagination pour les grandes listes
- Une vraie interface de jeu
- Pipeline CI/CD

Fonctionnalités de jeu à ajouter :
- Événements (rush du matin, promotions)
- Statistiques du joueur (argent gagné, produit le plus vendu)
- Système d'achievements
- Classement multijoueur

### Tests

J'ai testé manuellement via Swagger :
- Création de compte + connexion : fonctionne
- Tokens invalides/expirés : bien rejetés
- Commander sans stock suffisant : erreur correcte
- Commander sans argent : erreur correcte
- Mise à jour du stock après commande : fonctionne
- Routes protégées sans token : erreur 403

Faut que j'automatise ça avec pytest.

### Notes

Le `SECRET_KEY` dans `auth.py` est en dur pour le développement. En production il faudrait le mettre dans une variable d'environnement.

Si tu veux tester, le plus simple c'est de créer un compte sur Swagger, te connecter, et essayer de passer des commandes.

### Licence

MIT - fais-en ce que tu veux