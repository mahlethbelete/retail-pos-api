def seed_refs(client, auth_headers):
    category = client.post(
        "/categories/",
        json={"name": "Drinks", "description": "Cold drinks"},
        headers=auth_headers,
    )
    assert category.status_code == 201, category.text

    supplier = client.post(
        "/suppliers/",
        json={"name": "Acme", "phone": "0912345678", "email": "acme@example.com"},
        headers=auth_headers,
    )
    assert supplier.status_code == 201, supplier.text

    return category.json()["category_id"], supplier.json()["supplier_id"]


def test_create_product_requires_auth(client):
    response = client.post("/products/", json={"name": "Coke"})
    assert response.status_code == 401


def test_create_product_success(client, auth_headers):
    category_id, supplier_id = seed_refs(client, auth_headers)

    response = client.post(
        "/products/",
        json={
            "name": "Coca cola",
            "unit_price": "25.00",
            "quantity_in_stock": 50,
            "category_id": category_id,
            "supplier_id": supplier_id,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    assert response.json()["name"] == "Coca cola"
    assert "product_id" in response.json()


def test_create_product_without_name_returns_422(client, auth_headers):
    category_id, supplier_id = seed_refs(client, auth_headers)

    response = client.post(
        "/products/",
        json={
            "unit_price": "25.00",
            "quantity_in_stock": 50,
            "category_id": category_id,
            "supplier_id": supplier_id,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_cashier_cannot_create_product(client, cashier_headers, auth_headers):
    category_id, supplier_id = seed_refs(client, auth_headers)

    response = client.post(
        "/products/",
        json={
            "name": "Fanta",
            "unit_price": "20.00",
            "quantity_in_stock": 10,
            "category_id": category_id,
            "supplier_id": supplier_id,
        },
        headers=cashier_headers,
    )

    assert response.status_code == 403


def test_update_product(client, auth_headers):
    category_id, supplier_id = seed_refs(client, auth_headers)

    created = client.post(
        "/products/",
        json={
            "name": "Coca cola",
            "unit_price": "25.00",
            "quantity_in_stock": 50,
            "category_id": category_id,
            "supplier_id": supplier_id,
        },
        headers=auth_headers,
    )
    product_id = created.json()["product_id"]

    response = client.put(
        f"/products/{product_id}",
        json={"name": "Coca cola 500ml", "quantity_in_stock": 40},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Coca cola 500ml"
    assert response.json()["quantity_in_stock"] == 40


def test_get_product_not_found(client, auth_headers):
    response = client.get("/products/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"