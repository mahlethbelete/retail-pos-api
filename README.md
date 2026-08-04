**POS System API**
A REST API for a Point of Sale (POS) system built with FastAPI, SQLAlchemy, and PostgreSQL. Supports full CRUD for all core POS entities with foreign key relationships enforced between them.

**Entities**
/categories /suppliers /products /customers /users /sales /sale-items /payments /receipts
Each supports GET /, GET /{id}, POST /, PUT /{id}, DELETE /{id}.

**Features**
Full CRUD (Create, Read, Update, Delete) for every entity
PostgreSQL database with SQLAlchemy ORM models
Request/response validation with Pydantic schemas
Proper HTTP status codes, including 404 Not Found for missing records and 422 for invalid data
Foreign key constraints and SQLAlchemy relationships between related entities
Layered architecture: routers → services → repositories → models
Interactive API docs via Swagger UI and ReDoc
