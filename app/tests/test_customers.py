"""CRUD, validation and permissions on the /customers routes.

Cashiers are allowed to manage customers because they register walk in
shoppers at the till.
"""


def test_create_customer_requires_auth(client):
    response = client.post(
        "/customers/", json={"first_name": "Njeri", "last_name": "Mwangi"}
    )

    assert response.status_code == 401


def test_create_customer(client, auth_headers):
    response = client.post(
        "/customers/",
        json={
            "first_name": "Njeri",
            "last_name": "Mwangi",
            "email": "njeri@example.co.ke",
            "phone": "0700111222",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["first_name"] == "Njeri"
    assert "customer_id" in body


def test_create_customer_without_last_name_returns_422(client, auth_headers):
    response = client.post(
        "/customers/", json={"first_name": "Solo"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_cashier_can_create_customer(client, cashier_headers):
    response = client.post(
        "/customers/",
        json={"first_name": "Walk", "last_name": "In"},
        headers=cashier_headers,
    )

    assert response.status_code == 201, response.text


def test_list_customers(client, auth_headers, customer):
    response = client.get("/customers/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["customer_id"] == customer["customer_id"]


def test_get_customer_by_id(client, auth_headers, customer):
    response = client.get(
        f"/customers/{customer['customer_id']}", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["last_name"] == customer["last_name"]


def test_get_missing_customer_returns_404(client, auth_headers):
    response = client.get("/customers/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_update_customer_phone(client, auth_headers, customer):
    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={"phone": "0788999000"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["phone"] == "0788999000"
    assert response.json()["first_name"] == customer["first_name"]


def test_update_missing_customer_returns_404(client, auth_headers):
    response = client.put(
        "/customers/9999", json={"phone": "0700000000"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_customer(client, auth_headers, customer):
    response = client.delete(
        f"/customers/{customer['customer_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/customers/{customer['customer_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_customer_returns_404(client, auth_headers):
    assert client.delete("/customers/9999", headers=auth_headers).status_code == 404
