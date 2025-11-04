# InfyProject

A Django-based web application that provides user registration/authentication, profile management (stored in MongoDB Atlas), and a prediction interface (predictor app). This repo uses Django REST Framework for APIs and Simple JWT for token-based authentication.

## Features

- Django backend with REST API endpoints (registration, login, profile save/get, forgot password)
- Uses MongoDB Atlas for storing user profiles and some app data
- SQLite database is present for Django models (default development DB)
- JWT authentication (access + refresh tokens)
- Server-rendered frontend pages in `api/templates/api/` (index, home, profile, predict, history)
- Predictor app scaffold (training code file present: `predictor/train_model.py`)

## Repo layout (important files)

- `manage.py` — Django CLI wrapper
- `myproject/` — Django project settings and WSGI/ASGI
  - `myproject/settings.py` — project settings (includes MongoDB Atlas connection)
- `api/` — main app with views, models, serializers, templates, and frontend pages
  - `api/urls.py` — routes for pages and API endpoints
  - `api/views.py` — API and page views (uses Django templates and DRF views)
  - `api/models.py` — mixed Django models and MongoEngine Document models
  - `api/serializers.py` — DRF serializers (register/user serializers)
  - `api/templates/api/` — frontend templates rendered by Django
- `predictor/` — prediction/training app (contains `train_model.py` and `views.py`)

## Quickstart (Windows PowerShell)

1. Create and activate a virtual environment

```powershell
python -m venv .\env
.\env\Scripts\Activate.ps1
```

2. Install dependencies

If there is a `requirements.txt`, install from it:

```powershell
pip install -r requirements.txt
```

If `requirements.txt` is missing, install the typical dependencies used in this project:

```powershell
pip install django djangorestframework djangorestframework-simplejwt pymongo mongoengine django-cors-headers
```

3. Configure secrets

- Open `myproject/settings.py` and set `SECRET_KEY` to a secure value.
- Confirm or replace the MongoDB Atlas connection string; current file contains a connection URI — do not keep credentials in source control.

4. Apply migrations and create a superuser

```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server

```powershell
python manage.py runserver
```

6. Open the app in the browser

- Pages: `http://127.0.0.1:8000/` and the other pages defined (e.g., `/home/`, `/profile-page/`, `/predict-page/`)
- API endpoints are accessible under the same host as defined in `api/urls.py` (see `docs/api.md` for details)

## API and Auth notes

- JWT auth is configured via `rest_framework_simplejwt`; obtain tokens at the login endpoint and send `Authorization: Bearer <access_token>` on protected endpoints.
- The project uses both Django ORM (SQLite) and MongoDB (MongoEngine/pymongo). Some profile data is stored in MongoDB Atlas collections; confirm which models/collections you want to use in production.

## Training the predictor

- `predictor/train_model.py` is present but empty. Add training code there or provide a script to train and serialize a model (e.g. using scikit-learn and saving with `joblib` or `pickle`).
- After training, wire the inference endpoint in `predictor/views.py` to load the serialized model and return predictions.

## Security & cleanup

- Remove hard-coded credentials from `myproject/settings.py`. Use environment variables for `SECRET_KEY` and MongoDB connection string.
- Add `requirements.txt` with pinned dependency versions and consider adding `.env` for secrets (or use platform secrets manager).

## Next steps & contribution

See `docs/` for more detailed setup, architecture, API reference, usage examples and contribution guidelines.

---

Files added: `docs/setup.md`, `docs/architecture.md`, `docs/api.md`, `docs/usage.md`, `docs/contributing.md` — see `/docs` for details.
