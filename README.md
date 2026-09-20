# POS Backend API

A point of sale backend for a small Kenyan retail shop, built with FastAPI,
SQLAlchemy and PostgreSQL.

![Tests](https://github.com/OWNER/REPO/actions/workflows/tests.yml/badge.svg)

## Features

- JWT authentication with OAuth2 password flow
- Three roles: `admin`, `manager`, `cashier`, enforced per route
- Products, categories and suppliers (managers and admins only for writes)
- Customers, sales, sale items, payments and receipts (all staff)
- Layered structure: routers, services, repositories, models, schemas

## Project layout

```
pos/
  app/
    core/           security helpers (password hashing, JWT)
    models/         SQLAlchemy ORM models
    schemas/        Pydantic request and response models
    repositories/   database access
    services/       business rules
    routers/        HTTP endpoints
    tests/          pytest suite
    dependencies.py auth and role dependencies
    database.py     engine and session
    main.py         app factory and router registration
  .github/workflows/tests.yml
  pytest.ini
  requirements.txt
```

## Setup

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set a real `JWT_SECRET`. Generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Running the API

```bash
fastapi dev app/main.py
```

Open http://127.0.0.1:8000/docs

The first `POST /auth/register` creates the store administrator. Public
registration is disabled after that, so every later account is created by an
admin or a manager through `POST /auth/users`.

## Running the tests

From the project root:

```bash
pytest
```

Useful variations:

```bash
pytest -v                          # one line per test
pytest app/tests/test_products.py  # a single file
pytest -k "cashier"                # everything matching a keyword
pytest -x                          # stop at the first failure
```

The suite runs against an in memory SQLite database. `app/tests/conftest.py`
sets `DATABASE_URL=sqlite://` before the app is imported and overrides the
`get_db` dependency, so your PostgreSQL development database is never touched
and no extra services are needed.

Tables are created before each test and dropped afterwards, so every test
starts from an empty database.

### Test coverage

| File | Covers |
| --- | --- |
| `test_main.py` | root route, docs, OpenAPI schema, unknown routes |
| `test_security.py` | password hashing, JWT encode and decode |
| `test_auth_service.py` | authentication service in isolation |
| `test_auth_routes.py` | register, login, `/auth/me`, token rejection |
| `test_users.py` | user CRUD and the admin versus manager rules |
| `test_categories.py` | category CRUD, validation, role guards |
| `test_suppliers.py` | supplier CRUD, validation, role guards |
| `test_products.py` | product CRUD, price validation, role guards |
| `test_customers.py` | customer CRUD and validation |
| `test_sales.py` | sale CRUD and validation |
| `test_sale_items.py` | sale item CRUD and line total calculation |
| `test_payments.py` | payment CRUD, split payments, validation |
| `test_receipts.py` | receipt CRUD and validation |

Each area covers the success path, validation errors (422), missing resources
(404), unauthenticated access (401) and insufficient role (403).

## Continuous integration

`.github/workflows/tests.yml` runs on every push and on every pull request. It
checks out the repository, sets up Python, installs the dependencies and runs
the full suite. The job fails if any test fails.
