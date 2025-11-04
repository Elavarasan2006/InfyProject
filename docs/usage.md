# Usage & Examples

This file gives short examples for common developer tasks: running the server, using the API, and training the model.

## Run the server

```powershell
# Activate env
.\env\Scripts\Activate.ps1
# Run
python manage.py runserver
```

## Register a new user (example body)

URL: `POST /register/`

JSON body example:

```json
{
  "name": "Alice",
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123",
  "password2": "secret123",
  "profession": "student"
}
```

## Login and use JWT

1. POST to `/login/` with `{ "email": "alice@example.com", "password": "secret123" }`.
2. On success you receive `access` and `refresh` tokens. Use `access` in `Authorization: Bearer <token>` header in subsequent requests to protected endpoints.

## Save profile (MongoDB)

`POST /profile-save/` with JSON fields such as `name`, `email`, `degree`, `major`, `cgpa`, `skills`, `experience`.

## Train & serve model (TODO)

- `predictor/train_model.py` is currently empty. Recommended approach:
  1. Implement training code to load data, train a model (scikit-learn, XGBoost, etc.), and serialize it (joblib/pickle).
  2. Save the artifact (e.g., `models/model.joblib`) and add `.gitignore` entry as needed.
  3. Add an inference view in `predictor/views.py` that loads the model on startup or lazily and returns predictions for JSON input.

## Running tests

- Add Django/DRF tests in `api/tests.py` and `predictor/tests.py`. Run them with:

```powershell
python manage.py test
```

## Debugging tips

- If you see authentication errors, ensure tokens are sent in the `Authorization` header as `Bearer <token>`.
- If MongoDB access fails, check Atlas network access (IP whitelist) and credential correctness.
