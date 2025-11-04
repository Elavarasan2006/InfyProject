# Setup

This document describes how to prepare a development environment for the project.

## Prerequisites

- Python 3.9+ (use the version your project requires)
- Git (optional)
- An account with MongoDB Atlas if you want to use the same cloud DB used in `settings.py` (recommended for parity with the app)

## Environment (Windows PowerShell)

1. Clone the repo (if needed)

```powershell
git clone <repo-url>
cd <repo-folder>
```

2. Create & activate venv

```powershell
python -m venv .\env
.\env\Scripts\Activate.ps1
```

3. Install dependencies

If `requirements.txt` exists:

```powershell
pip install -r requirements.txt
```

Otherwise, install minimal dependencies used by this project:

```powershell
pip install django djangorestframework djangorestframework-simplejwt pymongo mongoengine django-cors-headers
```

4. Settings

- Edit `myproject/settings.py` to set `SECRET_KEY` and any other environment-specific settings.
- Replace the MongoDB Atlas URI with your own if required (do not commit credentials to the repo).

5. Database

This project uses SQLite (Django's default) and MongoDB Atlas:

- Run Django migrations for built-in Django models:

```powershell
python manage.py migrate
```

- MongoDB: ensure your Atlas cluster is reachable and credentials are set in `settings.py` or passed via environment variables.

6. Create superuser (for admin)

```powershell
python manage.py createsuperuser
```

7. Run the server

```powershell
python manage.py runserver
```

8. Optional: collect static files (if serving static in production)

```powershell
python manage.py collectstatic
```

## Notes

- Secrets management: use environment variables or a `.env` file with `python-dotenv` during development. Avoid committing secrets.
- To generate `requirements.txt` after installing packages locally:

```powershell
pip freeze > requirements.txt
```
