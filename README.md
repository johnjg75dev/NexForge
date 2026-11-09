# NeuralForge (in active development)

This repository begins the full NeuralForge implementation. The current executable slice includes local registration/login, password hashing, server-side sessions, owner-scoped projects, explicit viewer/editor sharing, an initial administrator role with persistent global settings, project CRUD, UTF-8 CSV profiling, and CPU MLP training for supported tabular/text classification and regression paths. It remains early development and is not hardened for public multi-tenant production deployment. It is **not yet the complete product** described in `../NeuralForge_Implementation_Spec.md`; training, pipelines, evaluation, deployment, collaboration, cloud services, and the other specified modules remain to be implemented. No fake training or results are shown.

## Run locally

Requires Python 3.11 or newer; runtime uses only the Python standard library.

```bash
cd neuralforge
python -m neuralforge --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`. On first launch, register the first account; it becomes the local administrator. Subsequent registrations create regular users. The administrator can turn off new registrations. Persistent data defaults to `~/.neuralforge`; use `--data-dir ./local-data` to choose another directory. The server binds to loopback by default. Sessions use HttpOnly, SameSite=Strict cookies; passwords use PBKDF2-HMAC-SHA256; failed sign-ins are throttled with a persisted temporary lockout; users can change passwords, which revokes all current sessions. Do not bind to a public interface: TLS termination, secure-cookie configuration, CSRF/origin policy, rate limiting, password reset, email verification, account lockout, robust migrations, and formal security review are still needed before public production deployment.

## Tests

```bash
cd neuralforge
python -m pip install -e '.[test]'
python -m pytest -q
```

## Current API

- `GET /api/health`
- `POST /api/auth/register` and `POST /api/auth/login` with `{ "username": "...", "password": "..." }`; server issues an HttpOnly session cookie.
- `POST /api/auth/logout`; `GET /api/auth/me`.
- `POST /api/projects/{id}/share` (owner only) with `{ "username": "...", "role": "viewer|editor" }`.
- `GET/PATCH /api/admin/config` (first registered user / admin only; supports application name, registration toggle, upload limit, default task).
- `GET /api/projects`
- `POST /api/projects` with JSON `{ "name": "Example", "task_type": "tabular_classification", "description": "" }`
- `PATCH /api/projects/{id}` with JSON `{ "name": "New name" }`
- `DELETE /api/projects/{id}`
- `POST /api/projects/{id}/datasets?filename=data.csv` with raw UTF-8 CSV request body
- `GET /api/projects/{id}/datasets`
- `POST /api/projects/{id}/train` with JSON `{ "dataset_id": "...", "target_column": "label", "config": {"epochs": 100, "hidden_layers": [64, 32], "seed": 42, "text_column": "review"} }`
- `GET /api/projects/{id}/runs`
- `GET /api/runs/{run_id}` (poll run state/result)

Supported task identifiers currently accepted at project creation: `tabular_classification`, `tabular_regression`, `text_classification`. Training is currently CPU-only with scikit-learn MLP, one deterministic 80/20 holdout, and basic imputation/scaling/one-hot or TF-IDF preprocessing. It does not yet offer dedicated test-set management, full pipeline editing, live per-epoch metrics, model-serving inference, or the broader framework/model integrations in the product spec. CSV profile typing is heuristic, not a semantic schema guarantee. Uploaded source files are stored under the configured NeuralForge data directory using generated names.

## Architecture

`domain/` holds OO entities/value objects, `application/` owns use cases and ports, `adapters/` implements SQLite persistence, `http/` is the transport adapter, and `web/` contains the local browser UI. The implementation will grow through complete vertical workflows while preserving the larger full-product specification.
