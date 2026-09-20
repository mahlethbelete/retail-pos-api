"""CRUD, validation and permissions on the /sales routes."""

from decimal import Decimal


def test_create_sale_requires_auth(client):
    response = client.post("/sales/", json={"user_id": 1})

    assert response.status_code == 401


def test_create_sale(client, auth_headers, admin_user, customer):
    response = client.post(
        "/sales/",
        json={
            "customer_id": customer["customer_id"],
            "user_id": admin_user["user_id"],
            "subtotal": "250.00",
            "tax_amount": "40.00",
            "total": "290.00",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert Decimal(body["total"]) == Decimal("290.00")
    assert body["customer_id"] == customer["customer_id"]
    assert "sale_id" in body


def test_sale_date_defaults_when_omitted(client, auth_headers, admin_user):
    response = client.post(
        "/sales/", json={"user_id": admin_user["user_id"]}, headers=auth_headers
    )

    assert response.status_code == 201, response.text
    assert response.json()["sale_date"] is not None


def test_create_walk_in_sale_without_customer(client, auth_headers, admin_user):
    response = client.post(
        "/sales/",
        json={"user_id": admin_user["user_id"], "total": "99.00"},
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    assert response.json()["customer_id"] is None


def test_create_sale_without_user_id_returns_422(client, auth_headers):
    response = client.post("/sales/", json={"total": "99.00"}, headers=auth_headers)

    assert response.status_code == 422


def test_create_sale_with_negative_total_returns_422(
    client, auth_headers, admin_user
):
    response = client.post(
        "/sales/",
        json={"user_id": admin_user["user_id"], "total": "-5.00"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_sale_with_bad_date_returns_422(client, auth_headers, admin_user):
    response = client.post(
        "/sales/",
        json={"user_id": admin_user["user_id"], "sale_date": "last tuesday"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_cashier_can_create_sale(client, cashier_headers, cashier_user):
    response = client.post(
        "/sales/",
        json={"user_id": cashier_user["user_id"], "total": "150.00"},
        headers=cashier_headers,
    )

    assert response.status_code == 201, response.text


def test_list_sales(client, auth_headers, sale):
    response = client.get("/sales/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["sale_id"] == sale["sale_id"]


def test_get_sale_by_id(client, auth_headers, sale):
    response = client.get(f"/sales/{sale['sale_id']}", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert Decimal(response.json()["total"]) == Decimal("139.20")


def test_get_missing_sale_returns_404(client, auth_headers):
    response = client.get("/sales/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_update_sale_total(client, auth_headers, sale):
    response = client.put(
        f"/sales/{sale['sale_id']}",
        json={"total": "200.00", "subtotal": "172.41"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert Decimal(response.json()["total"]) == Decimal("200.00")


def test_update_missing_sale_returns_404(client, auth_headers):
    response = client.put(
        "/sales/9999", json={"total": "10.00"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_sale(client, auth_headers, sale):
    response = client.delete(f"/sales/{sale['sale_id']}", headers=auth_headers)
    assert response.status_code == 204

    follow_up = client.get(f"/sales/{sale['sale_id']}", headers=auth_headers)
    assert follow_up.status_code == 404


def test_delete_missing_sale_returns_404(client, auth_headers):
    assert client.delete("/sales/9999", headers=auth_headers).status_code == 404
