"""CRUD, validation and permissions on the /products routes."""

from decimal import Decimal


def test_create_product_requires_auth(client):
    response = client.post("/products/", json={"name": "Coca Cola 500ml"})

    assert response.status_code == 401


def test_create_product(client, auth_headers, category, supplier):
    response = client.post(
        "/products/",
        json={
            "name": "Fanta Orange 500ml",
            "description": "Chilled soft drink",
            "unit_price": "60.00",
            "cost_price": "45.00",
            "quantity_in_stock": 80,
            "reorder_level": 15,
            "category_id": category["category_id"],
            "supplier_id": supplier["supplier_id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Fanta Orange 500ml"
    assert Decimal(body["unit_price"]) == Decimal("60.00")
    assert body["quantity_in_stock"] == 80
    assert "product_id" in body


def test_create_product_without_supplier(client, auth_headers, category):
    response = client.post(
        "/products/",
        json={
            "name": "House Brand Sugar 1kg",
            "unit_price": "180.00",
            "quantity_in_stock": 40,
            "category_id": category["category_id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    assert response.json()["supplier_id"] is None


def test_create_product_without_name_returns_422(client, auth_headers, category):
    response = client.post(
        "/products/",
        json={
            "unit_price": "60.00",
            "quantity_in_stock": 10,
            "category_id": category["category_id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_product_without_price_returns_422(client, auth_headers, category):
    response = client.post(
        "/products/",
        json={
            "name": "No Price Item",
            "quantity_in_stock": 10,
            "category_id": category["category_id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_product_with_non_numeric_price_returns_422(
    client, auth_headers, category
):
    response = client.post(
        "/products/",
        json={
            "name": "Broken Price",
            "unit_price": "very expensive",
            "quantity_in_stock": 10,
            "category_id": category["category_id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_product_with_too_many_decimals_returns_422(
    client, auth_headers, category
):
    response = client.post(
        "/products/",
        json={
            "name": "Over Precise",
            "unit_price": "60.12345",
            "quantity_in_stock": 10,
            "category_id": category["category_id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_cashier_cannot_create_product(client, cashier_headers, category):
    response = client.post(
        "/products/",
        json={
            "name": "Blocked Item",
            "unit_price": "10.00",
            "quantity_in_stock": 5,
            "category_id": category["category_id"],
        },
        headers=cashier_headers,
    )

    assert response.status_code == 403


def test_manager_can_create_product(client, manager_headers, category):
    response = client.post(
        "/products/",
        json={
            "name": "Manager Item",
            "unit_price": "10.00",
            "quantity_in_stock": 5,
            "category_id": category["category_id"],
        },
        headers=manager_headers,
    )

    assert response.status_code == 201, response.text


def test_list_products(client, auth_headers, product):
    response = client.get("/products/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["product_id"] == product["product_id"]


def test_cashier_can_read_products(client, cashier_headers, product):
    response = client.get("/products/", headers=cashier_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_product_by_id(client, auth_headers, product):
    response = client.get(f"/products/{product['product_id']}", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["name"] == product["name"]


def test_get_missing_product_returns_404(client, auth_headers):
    response = client.get("/products/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product(client, auth_headers, product):
    response = client.put(
        f"/products/{product['product_id']}",
        json={"name": "Coca Cola 1L", "quantity_in_stock": 45},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Coca Cola 1L"
    assert response.json()["quantity_in_stock"] == 45
    assert Decimal(response.json()["unit_price"]) == Decimal("60.00")


def test_update_product_price(client, auth_headers, product):
    response = client.put(
        f"/products/{product['product_id']}",
        json={"unit_price": "75.50"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert Decimal(response.json()["unit_price"]) == Decimal("75.50")


def test_update_missing_product_returns_404(client, auth_headers):
    response = client.put(
        "/products/9999", json={"name": "Ghost"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_update_product_with_bad_stock_type_returns_422(client, auth_headers, product):
    response = client.put(
        f"/products/{product['product_id']}",
        json={"quantity_in_stock": "plenty"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_cashier_cannot_update_product(client, cashier_headers, product):
    response = client.put(
        f"/products/{product['product_id']}",
        json={"unit_price": "1.00"},
        headers=cashier_headers,
    )

    assert response.status_code == 403


def test_delete_product(client, auth_headers, product):
    response = client.delete(
        f"/products/{product['product_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/products/{product['product_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_product_returns_404(client, auth_headers):
    assert client.delete("/products/9999", headers=auth_headers).status_code == 404


def test_cashier_cannot_delete_product(client, cashier_headers, product):
    response = client.delete(
        f"/products/{product['product_id']}", headers=cashier_headers
    )

    assert response.status_code == 403
