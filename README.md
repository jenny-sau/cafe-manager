# Café Manager API

<a name="français"></a>
## Français

Une API backend pour un jeu de gestion de café que j'ai développée avec FastAPI.

Le principe : le joueur commence avec un budget, achète des produits, sert des clients et doit gérer son stock. L'API s'occupe de toute la logique derrière : authentification, vérifications du stock, calculs des coûts et bénéfices.

### Pourquoi ce projet ?

J'ai créé Café Manager pour apprendre FastAPI de manière concrète.

Objectifs techniques :
- Créer une API REST complète avec FastAPI
- Comprendre comment fonctionne HTTP et REST
- Implémenter une logique métier
- Gérer l'authentification et les permissions
- Travailler avec une base de données relationnelle

### Lancer le projet
```bash
git clone https://github.com/jenny-sau/cafe-manager.git
cd cafe-manager
python -m venv venv
venv\Scripts\activate  # Sur Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

L'API tourne sur http://127.0.0.1:8000  
Documentation interactive : http://127.0.0.1:8000/docs

### Démarrage rapide

Pour tester l'API :

1. **Créer un compte** via `POST /auth/signup` avec un username, password et argent de départ
2. **Se connecter** via `POST /auth/login` pour récupérer un token JWT (valide 24h)
3. **Utiliser le token** : dans Swagger, cliquer sur "Authorize" et coller le token
4. **Tester les endpoints protégés** comme l'inventaire ou les commandes

Exemple pour s'inscrire :
```json
POST /auth/signup
{
  "username": "votre_username",
  "password": "votre_password",
  "money": 100.0
}
```

### Architecture

#### Models (Base de données)

- **User** : Les joueurs et les administrateurs du jeu
- **MenuItem** : Les produits disponibles (café, croissant...)
- **Inventory** : Le stock actuel de chaque joueur
- **Order** : Les commandes clients avec leur statut (pending, completed, cancelled)
- **GameLog** : L'historique complet de toutes les actions
- **PlayerProgress** : Les statistiques et le niveau de progression de chaque joueur

#### Endpoints principaux

**Authentification**
- `POST /auth/signup` - Créer un compte
- `POST /auth/login` - Se connecter et récupérer un JWT

**Menu** (POST/PUT/DELETE réservés aux admins)
- `GET /menu` - Voir la liste des produits
- `POST /menu` - Ajouter un produit (admin seulement)
- `PUT /menu/{id}` - Modifier un produit (admin seulement)
- `DELETE /menu/{id}` - Supprimer un produit (admin seulement)

**Inventaire & Commandes** (authentification requise)
- `POST /order/restock` - Acheter des produits (le stock augmente, l'argent diminue)
- `GET /inventory` - Consulter son stock
- `POST /order/client` - Une nouvelle commande client arrive (status: pending)
- `PATCH /order/{id}/complete` - Servir le client (le stock diminue, l'argent augmente, status: completed)
- `PATCH /order/{id}/cancel` - Annuler une commande (status: cancelled)

**Stats & Historique** (authentification requise)
- `GET /game/history` - Voir l'historique de ses actions
- `GET /game/stats` - Consulter ses statistiques (argent, niveau, bénéfices...)
- `GET /admin/stats` - Voir les stats globales du jeu (admin seulement)

## Comment ça marche
### Restock workflow

- Vérification du solde du joueur
- Décrémentation de l’argent
- Incrémentation du stock
- Action enregistrée dans l’historique

### Orders workflow

Les commandes suivent un cycle de vie basé sur un statut :

- **PENDING** : commande créée, aucun impact sur le stock ou l’argent
- **COMPLETED** : stock décrémenté, argent crédité (transaction atomique)
- **CANCELLED** : commande annulée sans effet métier

Les transitions sont strictement contrôlées :
- `PENDING → COMPLETED`
- `PENDING → CANCELLED`


### Exemple:
#### 1. Réapprovisionnement
```
Le joueur achète 10 cafés à 1.50€ l'unité
  ↓
L'API vérifie s'il a au moins 15€
  ↓
Si oui : le stock augmente de 10, l'argent diminue de 15€, l'action est loggée
Si non : erreur 400 "Pas assez d'argent"
```

#### 2. Commande client
```
Un client commande 2 cafés
  ↓
Une commande est créée avec le statut "pending"
  ↓
Le joueur clique sur "Servir"
  ↓
L'API vérifie s'il a au moins 2 cafés en stock
  ↓
Si oui : le stock diminue de 2, l'argent augmente de 6€ (prix de vente), statut passe à "completed"
Si non : erreur 400 "Stock insuffisant"
```

#### 3. Commande annulée
```
Le client part avant d'être servi
  ↓
Le joueur clique sur "Annuler"
  ↓
Le statut passe à "cancelled" (aucun changement de stock ou d'argent)
```

### Stack technique

- **FastAPI** - Framework web moderne pour Python
- **SQLAlchemy** - ORM pour gérer la base de données
- **SQLite** - Base de données pour le développement (migration vers PostgreSQL prévue)
- **JWT** - Authentification par tokens
- **bcrypt** - Hash sécurisé des mots de passe
- **Pydantic** - Validation automatique des données

### Ce que j'ai appris

En développant ce projet, j'ai vraiment travaillé sur :
- Les routes, dépendances et validation avec FastAPI
- SQLAlchemy et les relations entre tables
- L'authentification JWT et le hashage des mots de passe
- Comment structurer un projet backend (séparation models, schemas, auth)
- Implémenter une vraie logique métier avec vérifications et calculs

### Ce que je veux améliorer

Le projet est fonctionnel mais il manque encore pas mal de choses :

Features manquantes :
- Permettre plusieurs produits dans une même commande client (ex: 2 cafés + 1 croissant en une fois)
- Tests automatisés avec pytest
- Migration vers PostgreSQL
- Une vraie interface graphique pour jouer
- Pipeline CI/CD

Features de jeu à ajouter :
- Des événements aléatoires (rush du matin, promotions)
- Plus de statistiques (produit le plus vendu, argent gagné par jour...)

### Tests

Pour l'instant j'ai tout testé manuellement via Swagger :
- Création de compte et connexion : ça marche
- Tokens invalides ou expirés : bien rejetés
- Commander sans assez de stock : erreur correcte
- Commander sans assez d'argent : erreur correcte
- Mise à jour du stock après une commande : fonctionne
- Routes protégées sans token : erreur 403

Il faut que j'automatise tout ça avec pytest.

### Notes techniques

La `SECRET_KEY` dans `auth.py` est écrite en dur pour le développement. En production il faudrait absolument la mettre dans une variable d'environnement.

Pour tester, le plus simple c'est de créer un compte sur Swagger, te connecter, et essayer de passer quelques commandes pour voir comment ça réagit.