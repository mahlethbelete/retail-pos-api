"""CRUD, validation and permissions on the /categories routes."""


def test_create_category_requires_auth(client):
    response = client.post("/categories/", json={"name": "Snacks"})

    assert response.status_code == 401


def test_create_category(client, auth_headers):
    response = client.post(
        "/categories/",
        json={"name": "Snacks", "description": "Crisps and biscuits"},
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Snacks"
    assert body["description"] == "Crisps and biscuits"
    assert "category_id" in body


def test_create_category_without_name_returns_422(client, auth_headers):
    response = client.post(
        "/categories/", json={"description": "No name given"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_create_category_with_wrong_type_returns_422(client, auth_headers):
    response = client.post(
        "/categories/", json={"name": {"not": "a string"}}, headers=auth_headers
    )

    assert response.status_code == 422


def test_cashier_cannot_create_category(client, cashier_headers):
    response = client.post(
        "/categories/", json={"name": "Blocked"}, headers=cashier_headers
    )

    assert response.status_code == 403


def test_manager_can_create_category(client, manager_headers):
    response = client.post(
        "/categories/", json={"name": "Dairy"}, headers=manager_headers
    )

    assert response.status_code == 201, response.text


def test_list_categories(client, auth_headers, category):
    response = client.get("/categories/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == category["name"]


def test_list_categories_is_empty_at_first(client, auth_headers):
    response = client.get("/categories/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_cashier_can_read_categories(client, cashier_headers, category):
    response = client.get("/categories/", headers=cashier_headers)

    assert response.status_code == 200


def test_get_category_by_id(client, auth_headers, category):
    response = client.get(
        f"/categories/{category['category_id']}", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["category_id"] == category["category_id"]


def test_get_missing_category_returns_404(client, auth_headers):
    response = client.get("/categories/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_partial_update_keeps_other_fields(client, auth_headers, category):
    response = client.put(
        f"/categories/{category['category_id']}",
        json={"name": "Cold Beverages"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Cold Beverages"
    assert response.json()["description"] == category["description"]


def test_update_missing_category_returns_404(client, auth_headers):
    response = client.put(
        "/categories/9999", json={"name": "Ghost"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_cashier_cannot_update_category(client, cashier_headers, category):
    response = client.put(
        f"/categories/{category['category_id']}",
        json={"name": "Blocked"},
        headers=cashier_headers,
    )

    assert response.status_code == 403


def test_delete_category(client, auth_headers, category):
    response = client.delete(
        f"/categories/{category['category_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/categories/{category['category_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_category_returns_404(client, auth_headers):
    assert client.delete("/categories/9999", headers=auth_headers).status_code == 404


def test_cashier_cannot_delete_category(client, cashier_headers, category):
    response = client.delete(
        f"/categories/{category['category_id']}", headers=cashier_headers
    )

    assert response.status_code == 403
