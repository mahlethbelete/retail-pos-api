"""CRUD, validation and permissions on the /suppliers routes."""


def test_create_supplier_requires_auth(client):
    response = client.post("/suppliers/", json={"name": "Mombasa Foods"})

    assert response.status_code == 401


def test_create_supplier(client, auth_headers):
    response = client.post(
        "/suppliers/",
        json={
            "name": "Mombasa Foods Ltd",
            "phone": "0711222333",
            "email": "orders@mombasafoods.co.ke",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Mombasa Foods Ltd"
    assert body["phone"] == "0711222333"
    assert "supplier_id" in body


def test_create_supplier_with_only_a_name(client, auth_headers):
    response = client.post(
        "/suppliers/", json={"name": "Minimal Supplier"}, headers=auth_headers
    )

    assert response.status_code == 201, response.text
    assert response.json()["phone"] is None
    assert response.json()["email"] is None


def test_create_supplier_without_name_returns_422(client, auth_headers):
    response = client.post(
        "/suppliers/", json={"phone": "0700000000"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_cashier_cannot_create_supplier(client, cashier_headers):
    response = client.post(
        "/suppliers/", json={"name": "Blocked"}, headers=cashier_headers
    )

    assert response.status_code == 403


def test_list_suppliers(client, auth_headers, supplier):
    response = client.get("/suppliers/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == supplier["name"]


def test_get_supplier_by_id(client, auth_headers, supplier):
    response = client.get(
        f"/suppliers/{supplier['supplier_id']}", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["supplier_id"] == supplier["supplier_id"]


def test_get_missing_supplier_returns_404(client, auth_headers):
    response = client.get("/suppliers/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_update_supplier_phone(client, auth_headers, supplier):
    response = client.put(
        f"/suppliers/{supplier['supplier_id']}",
        json={"phone": "0799888777"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["phone"] == "0799888777"
    assert response.json()["name"] == supplier["name"]


def test_update_missing_supplier_returns_404(client, auth_headers):
    response = client.put(
        "/suppliers/9999", json={"name": "Ghost"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_supplier(client, auth_headers, supplier):
    response = client.delete(
        f"/suppliers/{supplier['supplier_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/suppliers/{supplier['supplier_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_supplier_returns_404(client, auth_headers):
    assert client.delete("/suppliers/9999", headers=auth_headers).status_code == 404


def test_cashier_cannot_delete_supplier(client, cashier_headers, supplier):
    response = client.delete(
        f"/suppliers/{supplier['supplier_id']}", headers=cashier_headers
    )

    assert response.status_code == 403
