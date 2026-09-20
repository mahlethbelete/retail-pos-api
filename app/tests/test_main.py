"""System routes."""


def test_read_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["message"] == "Pos API is active"


def test_docs_endpoint_accessible(client):
    assert client.get("/docs").status_code == 200


def test_openapi_schema_lists_every_router(client):
    paths = client.get("/openapi.json").json()["paths"]

    for prefix in (
        "/auth/login",
        "/users/",
        "/products/",
        "/categories/",
        "/suppliers/",
        "/customers/",
        "/sales/",
        "/sale-items/",
        "/payments/",
        "/receipts/",
    ):
        assert prefix in paths, f"{prefix} missing from the OpenAPI schema"


def test_unknown_route_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404
