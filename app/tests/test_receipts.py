"""CRUD, validation and permissions on the /receipts routes."""


def receipt(sale, number="INV-00000001"):
    return {"sale_id": sale["sale_id"], "receipt_number": number}


def test_create_receipt_requires_auth(client, sale):
    response = client.post("/receipts/", json=receipt(sale))

    assert response.status_code == 401


def test_create_receipt(client, auth_headers, sale):
    response = client.post("/receipts/", json=receipt(sale), headers=auth_headers)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["receipt_number"] == "INV-00000001"
    assert body["sale_id"] == sale["sale_id"]
    assert "receipt_id" in body


def test_create_receipt_without_number_returns_422(client, auth_headers, sale):
    response = client.post(
        "/receipts/", json={"sale_id": sale["sale_id"]}, headers=auth_headers
    )

    assert response.status_code == 422


def test_create_receipt_without_sale_id_returns_422(client, auth_headers):
    response = client.post(
        "/receipts/", json={"receipt_number": "INV-00000002"}, headers=auth_headers
    )

    assert response.status_code == 422


def test_cashier_can_create_receipt(client, cashier_headers, sale):
    response = client.post("/receipts/", json=receipt(sale), headers=cashier_headers)

    assert response.status_code == 201, response.text


def test_list_receipts(client, auth_headers, sale):
    client.post("/receipts/", json=receipt(sale), headers=auth_headers)

    response = client.get("/receipts/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


def test_get_receipt_by_id(client, auth_headers, sale):
    created = client.post(
        "/receipts/", json=receipt(sale), headers=auth_headers
    ).json()

    response = client.get(
        f"/receipts/{created['receipt_id']}", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["receipt_number"] == "INV-00000001"


def test_get_missing_receipt_returns_404(client, auth_headers):
    response = client.get("/receipts/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Receipt not found"


def test_update_receipt_number(client, auth_headers, sale):
    created = client.post(
        "/receipts/", json=receipt(sale), headers=auth_headers
    ).json()

    response = client.put(
        f"/receipts/{created['receipt_id']}",
        json={"receipt_number": "INV-00009999"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["receipt_number"] == "INV-00009999"


def test_update_missing_receipt_returns_404(client, auth_headers):
    response = client.put(
        "/receipts/9999", json={"receipt_number": "INV-1"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_receipt(client, auth_headers, sale):
    created = client.post(
        "/receipts/", json=receipt(sale), headers=auth_headers
    ).json()

    response = client.delete(
        f"/receipts/{created['receipt_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/receipts/{created['receipt_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_receipt_returns_404(client, auth_headers):
    assert client.delete("/receipts/9999", headers=auth_headers).status_code == 404
