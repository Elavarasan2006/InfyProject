# Contributing

Thanks for considering contributing! A few small guidelines to get changes merged quickly.

- Use feature branches (e.g., `feature/add-predictor`) and open a PR to `main`.
- Keep changes small and focused; write tests for new behavior.
- Don't commit secrets (use environment variables or a `.env` file and add it to `.gitignore`).
- Add or update `requirements.txt` when adding dependencies.

Areas that need help / suggestions:

- Implement `predictor/train_model.py` and add an inference endpoint.
- Normalize profile storage (Django vs MongoDB) to avoid duplication.
- Add automated tests for authentication and profile endpoints.

If you're unsure about changes, open an issue first describing the plan.
