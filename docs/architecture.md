# Architecture & Components

This section outlines the high-level architecture of the project and the responsibilities of each component.

## High-level overview

- Django project (`myproject`) acts as the backend server that serves page templates and exposes API endpoints built with Django REST Framework.
- `api` app handles user accounts, registration, login (JWT), profile storage and serves frontend templates.
- `predictor` app is intended to contain ML training and inference logic. Currently, the training script file `predictor/train_model.py` is empty and should be implemented.
- Data storage:
  - SQLite (`db.sqlite3`) — used by Django ORM for built-in auth and standard Django models.
  - MongoDB Atlas — used (via `pymongo` and `mongoengine`) to store user profile documents and other collections. Connection configured in `myproject/settings.py`.

## Components

- REST API Layer
  - Built with DRF. JWT tokens are provided by `rest_framework_simplejwt`.
  - Serializers in `api/serializers.py` handle input validation for registration and user representation.

- Persistence
  - Hybrid storage: relational (SQLite) + document (MongoDB). Some models are implemented both as Django models and MongoEngine Documents — check `api/models.py` for multiple model definitions.

- Frontend
  - Server-rendered templates under `api/templates/api/` are used to render pages like index, home, profile, predict, and history. Static assets (if any) are served according to `STATIC_URL`.

- Predictor
  - The `predictor` app should expose an inference endpoint (view) that loads a trained model and returns predictions.
  - Training code should be placed in `predictor/train_model.py` and should output a serialized model file (e.g., `model.joblib` or `model.pkl`).

## Data flow (example: user registration)

1. Client POSTs to `/register/` with required fields.
2. `api.serializers.RegisterSerializer` validates and creates a `User` object and associated `Profile`.
3. Profile data is optionally stored or synced to MongoDB depending on view logic.
4. Login endpoint (`/login/`) authenticates and returns JWT tokens.

## Security considerations

- Move secrets (SECRET_KEY, MongoDB URI) out of settings and into environment variables.
- If using this in production, disable DEBUG and configure allowed hosts and secure cookie settings.

## Extensibility

- Implement `predictor/train_model.py` to produce a model artifact and create a view in `predictor/views.py` to load it for inference.
- Consider normalizing profile storage to a single source of truth (either Django ORM or MongoDB) to avoid duplication.
