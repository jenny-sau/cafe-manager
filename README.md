# Café Manager API

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

Une API REST de gestion de café simulant l'expérience complète d'un commerce : approvisionnement, gestion de stock, service client et progression du joueur.

**Stack technique :** FastAPI · PostgreSQL · SQLAlchemy · JWT · Docker · Pytest

---

## Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Comment ça marche](#comment-ça-marche)
- [Architecture](#architecture)
- [Compétences développées](#compétences-développées)
- [Tests](#tests)
- [Roadmap](#roadmap)

---

## Aperçu

Café Manager est un jeu de gestion où le joueur démarre avec un budget, achète des produits, sert des clients et fait évoluer son café.

**Exemple de partie :**
```
Budget initial : 100€
  ↓
Achat de 20 cafés (30€) → Stock : 20 cafés, Argent : 70€
  ↓
Client commande 3 cafés → Stock : 17 cafés, Argent : 79€
  ↓
Niveau augmente, nouveaux produits débloqués 
```

### Pourquoi ce projet ?

Projet d'apprentissage personnel pour maîtriser le développement backend :
- Construire une API REST complète depuis le début
- Implémenter une logique métier (transactions, validations, états)
- Comprendre l'architecture d'une application moderne (auth, DB, tests)

---

## Fonctionnalités

### Pour les joueurs
- **Authentification** : Inscription, connexion, JWT (24h)
- **Réapprovisionnement** : Acheter des produits pour son stock
- **Inventaire** : Consulter son stock 
- **Commandes clients** : Servir ou annuler les demandes
- **Statistiques** : Suivre ses bénéfices, niveau, historique

### Pour les admins
- **Gestion du menu** : Ajouter/modifier/supprimer des produits
- **Gestion des utilisateurs** : CRUD complet
- **Stats globales** : Vue d'ensemble du jeu

---

## Installation

### Prérequis
- Python 3.11+
- Docker & Docker Compose

### Étapes
```bash
# 1. Cloner le projet
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager

# 2. Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer PostgreSQL (Docker)
docker compose up -d

# 5. Lancer l'API
uvicorn main:app --reload
```

** API disponible sur :** http://127.0.0.1:8000  
**Documentation interactive :** http://127.0.0.1:8000/docs

---

## Démarrage rapide

### 1. Créer un compte
```bash
POST /auth/signup
```
```json
{
  "username": "maria",
  "password": "secret123",
  "money": 100.0
}
```

### 2. Se connecter
```bash
POST /auth/login
```
```json
{
  "username": "maria",
  "password": "secret123"
}
```

**Réponse :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Utiliser le token

Dans Swagger UI (http://127.0.0.1:8000/docs) :
1. Cliquer sur le bouton **"Authorize"** 
2. Coller le token récupéré
3. Tous les endpoints protégés sont maintenant accessibles !

### 4. Tester un workflow complet
```bash
# Voir le menu
GET /menu

# Acheter 10 cafés
POST /order/restock
{
  "item_id": 1,
  "quantity": 10
}

# Vérifier son inventaire
GET /inventory

# Une commande client arrive
POST /order/client
{
  "item_id": 1,
  "quantity": 2
}

# Servir le client
PATCH /order/{order_id}/complete
```

---

## Comment ça marche

### Workflow : Réapprovisionnement
```
Joueur veut acheter 10 cafés à 1.50€/unité
          ↓
API vérifie : a-t-il 15€ ?
          ↓
    OUI                 NON
     ↓                   ↓
Stock +10          Erreur 400
Argent -15€        "Fonds insuffisants"
Action loggée
```

### Workflow : Commande client
```
Client commande 2 cafés (prix vente : 3€/unité)
          ↓
Commande créée (status: PENDING)
          ↓
Joueur clique "Servir"
          ↓
API vérifie : 2 cafés en stock ?
          ↓
    OUI                 NON
     ↓                   ↓
Stock -2           Erreur 400
Argent +6€         "Stock insuffisant"
Status: COMPLETED
```

### Cycle de vie des commandes

Les commandes suivent un système d'états strict :
```
PENDING → COMPLETED  (stock décrémenté, argent crédité)
   ↓
CANCELLED (aucun effet sur stock/argent)
```

**Transitions interdites :**
- `COMPLETED → PENDING`
- `CANCELLED → COMPLETED`

---

## Architecture

### Models (Base de données)

| Table | Description                                        |
|-------|----------------------------------------------------|
| **User** | Joueurs et administrateurs                         |
| **MenuItem** | Produits au menu (café, croissant...)              |
| **Inventory** | Stock actuel de chaque joueur                      |
| **Order** | Commandes avec statut (pending/completed/cancelled) |
| **GameLog** | Historique complet des actions                     |
| **PlayerProgress** | Niveau et statistiques des joueurs                 |

### Endpoints principaux

#### Authentification (publique)
```
POST   /auth/signup    Créer un compte
POST   /auth/login     Se connecter (JWT)
```

#### Menu
```
GET    /menu           Lister les produits
POST   /menu           Ajouter un produit (admin)
PUT    /menu/{id}      Modifier un produit (admin)
DELETE /menu/{id}      Supprimer un produit (admin)
```

#### Inventaire & Commandes (authentifié)
```
POST   /order/restock         Acheter du stock
GET    /inventory             Consulter son inventaire
POST   /order/client          Nouvelle commande client
PATCH  /order/{id}/complete   Servir le client
PATCH  /order/{id}/cancel     Annuler la commande
```

#### Statistiques
```
GET    /game/history    Historique personnel
GET    /game/stats      Statistiques personnelles
GET    /admin/stats     Stats globales (admin)
```

---

## Compétences développées

### Backend & API
- Architecture REST avec **FastAPI** (routes, dépendances, validation automatique)
- Injection de dépendances pour l'authentification
- Documentation auto-générée (OpenAPI/Swagger)

### Base de données
- Modélisation relationnelle avec **SQLAlchemy** (relations One-to-Many, Foreign Keys)
- Migrations de schéma avec **Alembic**
- Transactions atomiques (stock + argent modifiés ensemble ou pas du tout)

### Sécurité
- Authentification **JWT** avec expiration (24h)
- Hash des mots de passe avec **bcrypt**
- Gestion des rôles (RBAC : admin vs joueur)

### Logique métier
- Machine à états pour les commandes (transitions contrôlées)
- Validations métier (stock suffisant, fonds disponibles)
- Calculs automatiques (bénéfices, coûts)

### DevOps & Tests
- Conteneurisation avec **Docker** (PostgreSQL)
- Tests automatisés avec **pytest** (auth, permissions, logique)
- Gestion de deux environnements (dev:5432, test:5433)

---

## Tests

Tests automatisés avec **pytest** couvrant :

### Authentification
- Inscription (signup) et validation des données
- Gestion des doublons (username déjà pris)
- Connexion (login) et génération du JWT
- Cas d'erreur : identifiants invalides, token manquant/expiré

### Permissions
- Accès autorisé pour utilisateurs authentifiés
- Blocage des utilisateurs non authentifiés (401)
- Restriction des routes admin (403 pour les joueurs)

### Logique métier
- Réapprovisionnement (vérification du solde)
- Gestion de l'inventaire (incréments/décréments)
- Commandes clients (workflow complet PENDING → COMPLETED)
- Cas d'erreur : stock insuffisant, fonds insuffisants

**Tous les tests passent actuellement ✅**
```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=app tests/
```

---

## Configuration

### Ports utilisés

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL (dev) | 5432 | Base de données principale |
| PostgreSQL (test) | 5433 | Base de données pour pytest |
| FastAPI | 8000 | API |

**Important :** Aucun PostgreSQL ne doit tourner nativement sur Windows. Tout est géré via Docker.

### Sécurité

**Note de sécurité :** La `SECRET_KEY` dans `auth.py` est actuellement écrite en dur pour le développement.

**En production, utiliser des variables d'environnement :**
```bash
# Méthode 1 : Export direct
export SECRET_KEY="votre-clé-ultra-sécurisée-de-32-caractères"

# Méthode 2 : Fichier .env
# .env
SECRET_KEY=votre-clé-ultra-sécurisée
DATABASE_URL=postgresql://user:pass@host/db
```

Puis charger avec `python-dotenv` :
```python
from dotenv import load_dotenv
load_dotenv()
```



---

**Questions ?** N'hésite pas à ouvrir une issue ou à me contacter: jenny.saucy@outlook.com :)