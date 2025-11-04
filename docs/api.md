# API Reference

This document lists the main API endpoints found in `api/urls.py` and the expected behavior based on `api/views.py` and `api/serializers.py`.

> Note: The project wires these endpoints at project root in `myproject/urls.py` (verify if a prefix is used). Below, paths are shown as they appear in `api/urls.py`.

## Pages (GET, server-rendered)

- `GET /` → `index` (renders `api/index.html`)
- `GET /home/` → `home` (renders `api/home.html`)
- `GET /profile-page/` → `profile_page` (renders `api/profile.html`)
- `GET /predict-page/` → `predict_page` (renders `api/predict.html`)
- `GET /history-page/` → `history_page` (renders `api/history.html`)
- `GET /forgot-password-page/` → `forgot_password_page` (renders `api/forgot_password.html`)

## Auth & User

- `POST /register/` → `RegisterView` (DRF CreateAPIView)
  - Payload: { name, username (optional), email, password, password2, profession (optional) }
  - Validations: password==password2, email required.
  - Success: creates a `User` and a `Profile`.

- `POST /login/` → `LoginView`
  - Payload: { email, password }
  - Returns: `access` and `refresh` JWT tokens plus basic user info on success.

- `POST /logout/` → `LogoutView` (requires auth)
  - Returns a success message.

- `GET /profile/` → `ProfileView` (requires auth)
  - Returns authenticated user's serialized info (uses `UserSerializer`).

## Profile persistence (MongoDB-backed)

- `POST /profile-save/` → `ProfileSaveView`
  - Payload: profile fields like username, email, degree, major, cgpa, skills, certifications, industry_preference, experience
  - Inserts or updates profile in MongoDB collection `users`.

- `GET /profile-get/<str:email>/` → `ProfileGetView`
  - Fetches profile by email from MongoDB and returns JSON (converts `_id` to string).

## Forgot password

- `POST /forgot-password/` → `ForgotPasswordView`
  - Payload: { email, new_password (optional) }
  - If `new_password` supplied and user exists, updates Django user's password.
  - Otherwise, returns a message (current implementation just returns a message about sending instructions).

## Usage examples (PowerShell + curl)

Obtain token

```powershell
# Login
curl -Method POST -Uri "http://127.0.0.1:8000/login/" -Body (@{email='user@example.com'; password='secret'} | ConvertTo-Json) -ContentType 'application/json'
```

Access protected endpoint (example `GET /profile/`)

```powershell
curl -Method GET -Uri "http://127.0.0.1:8000/profile/" -Headers @{ "Authorization" = "Bearer <access_token>" }
```

## Notes & caveats

- Some views mix Django ORM and direct MongoDB usage; behavior may vary depending on which model (Django vs MongoEngine) is authoritative.
- Validate API routes with `python manage.py runserver` and test each endpoint using Postman or curl.
