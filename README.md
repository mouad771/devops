# 🎓 Plateforme de gestion d'étudiants

[![CI/CD](https://github.com/mouad771/devops/actions/workflows/ci.yml/badge.svg)](https://github.com/mouad771/devops/actions/workflows/ci.yml)

Mini-projet du module **DevOps** : application web de gestion d'étudiants
accompagnée d'une chaîne complète d'intégration et de déploiement continus
(CI/CD).

L'application permet l'**inscription**, la **consultation** et la **mise à jour**
des fiches étudiants (CRUD), la **gestion des notes** et l'**export des relevés**
(CSV / PDF), avec une **authentification par rôle** (administrateur / enseignant /
étudiant).

---

## 🧱 Stack technique

| Couche            | Technologie                                  |
| ----------------- | -------------------------------------------- |
| API / Backend     | Python 3.12, FastAPI                         |
| Base de données   | PostgreSQL (SQLite par défaut en local/tests)|
| ORM               | SQLAlchemy 2.0                               |
| Authentification  | JWT (OAuth2 password flow), bcrypt           |
| Frontend          | HTML / CSS / JavaScript (vanilla)            |
| Tests             | pytest                                        |
| Lint              | ruff                                          |
| Conteneurisation  | Docker (multi-stage), docker-compose         |
| CI/CD             | GitHub Actions → GitHub Container Registry    |
| Orchestration     | Kubernetes (bonus, dossier `k8s/`)           |

---

## 🚀 Démarrage rapide avec Docker

L'application se lance en **une seule commande** (application + base de données) :

```bash
docker compose up --build
```

- Interface web : <http://localhost:8000>
- Documentation interactive de l'API (Swagger) : <http://localhost:8000/docs>
- Sonde de santé : <http://localhost:8000/health>

**Compte administrateur par défaut** : `admin@ecole.ma` / `admin1234`
(modifiable via les variables `ADMIN_EMAIL` / `ADMIN_PASSWORD`).

---

## 💻 Démarrage en local (sans Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # configuration externe
uvicorn app.main:app --reload
```

Par défaut, l'application utilise une base **SQLite** locale, aucune installation
de base de données n'est donc nécessaire pour démarrer.

---

## ⚙️ Configuration

Toute la configuration est externalisée via des variables d'environnement
(voir [`.env.example`](.env.example)) :

| Variable                      | Description                              | Défaut                         |
| ----------------------------- | ---------------------------------------- | ------------------------------ |
| `DATABASE_URL`                | URL de connexion à la base               | `sqlite:///./gestion_etudiants.db` |
| `SECRET_KEY`                  | Clé de signature des JWT                  | `change-me-in-production`       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité du token               | `60`                           |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Compte admin initial (seed)           | `admin@ecole.ma` / `admin1234`  |

---

## 🔐 Rôles et permissions

| Action                          | Admin | Enseignant | Étudiant         |
| ------------------------------- | :---: | :--------: | :--------------: |
| Créer / modifier / supprimer un étudiant | ✅ | ❌ | ❌ |
| Lister / consulter les étudiants | ✅ | ✅ | ❌ |
| Saisir des notes                 | ✅ | ✅ | ❌ |
| Créer des cours                  | ✅ | ❌ | ❌ |
| Consulter son propre relevé      | ✅ | ✅ | ✅ (le sien) |
| Gérer les utilisateurs           | ✅ | ❌ | ❌ |

---

## 📡 Principaux points d'API

| Méthode | Endpoint                                  | Description                          |
| ------- | ----------------------------------------- | ------------------------------------ |
| `POST`  | `/api/auth/login`                         | Connexion, retourne un JWT           |
| `GET`   | `/api/auth/me`                            | Profil de l'utilisateur courant      |
| `POST`  | `/api/auth/users`                         | Créer un utilisateur (admin)         |
| `GET`   | `/api/students`                           | Lister les étudiants                 |
| `POST`  | `/api/students`                           | Créer un étudiant (admin)            |
| `PUT`   | `/api/students/{id}`                      | Modifier un étudiant (admin)         |
| `DELETE`| `/api/students/{id}`                      | Supprimer un étudiant (admin)        |
| `POST`  | `/api/courses`                            | Créer un cours (admin)               |
| `POST`  | `/api/students/{id}/grades`               | Saisir / mettre à jour une note      |
| `GET`   | `/api/students/{id}/transcript`           | Relevé de notes (JSON)               |
| `GET`   | `/api/students/{id}/transcript.csv`       | Export du relevé en CSV              |
| `GET`   | `/api/students/{id}/transcript.pdf`       | Export du relevé en PDF              |

---

## ✅ Tests et qualité

```bash
ruff check .          # analyse statique (lint)
pytest                # tests automatisés
pytest --cov=app      # tests + couverture
```

---

## 🔄 Workflow Git

- `main` : branche de production (protégée, image publiée automatiquement).
- `develop` : branche d'intégration.
- `feature/*` : branches de fonctionnalités, fusionnées via Pull Request.

Les messages de commit suivent la convention **Conventional Commits**
(`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`…).

---

## 🐳 Image Docker

L'image est publiée automatiquement sur **GitHub Container Registry** lorsque le
pipeline réussit sur `main` :

```bash
docker pull ghcr.io/mouad771/devops:latest
```

---

## ☸️ Déploiement Kubernetes (bonus)

Les manifestes se trouvent dans le dossier [`k8s/`](k8s/) (ConfigMap, Secret,
PostgreSQL, Deployment, Service). Déploiement sur Minikube :

```bash
# Adapter l'image dans k8s/deployment.yaml (ghcr.io/mouad771/devops:latest)
kubectl apply -f k8s/
kubectl get pods
minikube service gestion-etudiants
```

---

## 📁 Structure du projet

```
.
├── app/                  # Code de l'application FastAPI
│   ├── routers/          # Routes (auth, students, grades, transcripts)
│   ├── models.py         # Modèles ORM
│   ├── schemas.py        # Schémas Pydantic
│   ├── security.py       # JWT, hachage, contrôle des rôles
│   └── crud.py           # Opérations base de données
├── static/               # Frontend (HTML/CSS/JS)
├── tests/                # Tests pytest
├── k8s/                  # Manifestes Kubernetes (bonus)
├── .github/workflows/    # Pipeline CI/CD
├── Dockerfile            # Build multi-stage
├── docker-compose.yml    # Stack complète (app + PostgreSQL)
└── requirements.txt      # Dépendances
```
