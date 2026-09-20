"""CRUD, validation and permissions on the /sale-items routes."""

from decimal import Decimal


def line(sale, product, quantity=2, unit_price="60.00"):
    return {
        "sale_id": sale["sale_id"],
        "product_id": product["product_id"],
        "quantity": quantity,
        "unit_price": unit_price,
    }


def test_create_sale_item_requires_auth(client, sale, product):
    response = client.post("/sale-items/", json=line(sale, product))

    assert response.status_code == 401


def test_create_sale_item(client, auth_headers, sale, product):
    response = client.post(
        "/sale-items/", json=line(sale, product, 3), headers=auth_headers
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["sale_id"] == sale["sale_id"]
    assert body["product_id"] == product["product_id"]
    assert body["quantity"] == 3
    assert "sale_item_id" in body


def test_line_total_is_calculated_when_omitted(client, auth_headers, sale, product):
    response = client.post(
        "/sale-items/",
        json=line(sale, product, quantity=3, unit_price="60.00"),
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    assert Decimal(response.json()["line_total"]) == Decimal("180.00")


def test_explicit_line_total_is_kept(client, auth_headers, sale, product):
    payload = line(sale, product, quantity=2, unit_price="60.00")
    payload["line_total"] = "100.00"

    response = client.post("/sale-items/", json=payload, headers=auth_headers)

    assert response.status_code == 201, response.text
    assert Decimal(response.json()["line_total"]) == Decimal("100.00")


def test_create_sale_item_without_quantity_returns_422(
    client, auth_headers, sale, product
):
    response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["sale_id"],
            "product_id": product["product_id"],
            "unit_price": "60.00",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_sale_item_without_unit_price_returns_422(
    client, auth_headers, sale, product
):
    response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["sale_id"],
            "product_id": product["product_id"],
            "quantity": 2,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_sale_item_with_zero_quantity_returns_422(
    client, auth_headers, sale, product
):
    response = client.post(
        "/sale-items/", json=line(sale, product, quantity=0), headers=auth_headers
    )

    assert response.status_code == 422


def test_create_sale_item_with_bad_quantity_type_returns_422(
    client, auth_headers, sale, product
):
    response = client.post(
        "/sale-items/", json=line(sale, product, quantity="two"), headers=auth_headers
    )

    assert response.status_code == 422


def test_cashier_can_create_sale_item(client, cashier_headers, sale, product):
    response = client.post(
        "/sale-items/", json=line(sale, product), headers=cashier_headers
    )

    assert response.status_code == 201, response.text


def test_list_sale_items(client, auth_headers, sale, product):
    client.post("/sale-items/", json=line(sale, product), headers=auth_headers)

    response = client.get("/sale-items/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


def test_get_sale_item_by_id(client, auth_headers, sale, product):
    created = client.post(
        "/sale-items/", json=line(sale, product, 4), headers=auth_headers
    ).json()

    response = client.get(
        f"/sale-items/{created['sale_item_id']}", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity"] == 4


def test_get_missing_sale_item_returns_404(client, auth_headers):
    response = client.get("/sale-items/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale item not found"


def test_update_quantity_recalculates_line_total(client, auth_headers, sale, product):
    created = client.post(
        "/sale-items/", json=line(sale, product, 2), headers=auth_headers
    ).json()

    response = client.put(
        f"/sale-items/{created['sale_item_id']}",
        json={"quantity": 5},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity"] == 5
    assert Decimal(response.json()["line_total"]) == Decimal("300.00")


def test_update_missing_sale_item_returns_404(client, auth_headers):
    response = client.put(
        "/sale-items/9999", json={"quantity": 1}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_sale_item(client, auth_headers, sale, product):
    created = client.post(
        "/sale-items/", json=line(sale, product), headers=auth_headers
    ).json()

    response = client.delete(
        f"/sale-items/{created['sale_item_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/sale-items/{created['sale_item_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_sale_item_returns_404(client, auth_headers):
    assert client.delete("/sale-items/9999", headers=auth_headers).status_code == 404
