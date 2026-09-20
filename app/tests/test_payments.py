"""CRUD, validation and permissions on the /payments routes."""

from decimal import Decimal


def payment(sale, method="mpesa", amount="139.20"):
    return {
        "sale_id": sale["sale_id"],
        "payment_method": method,
        "amount": amount,
    }


def test_create_payment_requires_auth(client, sale):
    response = client.post("/payments/", json=payment(sale))

    assert response.status_code == 401


def test_record_mpesa_payment(client, auth_headers, sale):
    response = client.post("/payments/", json=payment(sale), headers=auth_headers)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["payment_method"] == "mpesa"
    assert Decimal(body["amount"]) == Decimal("139.20")
    assert body["sale_id"] == sale["sale_id"]
    assert "payment_id" in body


def test_record_cash_payment(client, auth_headers, sale):
    response = client.post(
        "/payments/", json=payment(sale, "cash", "150.00"), headers=auth_headers
    )

    assert response.status_code == 201, response.text
    assert response.json()["payment_method"] == "cash"


def test_payment_date_defaults_when_omitted(client, auth_headers, sale):
    response = client.post("/payments/", json=payment(sale), headers=auth_headers)

    assert response.status_code == 201, response.text
    assert response.json()["payment_date"] is not None


def test_split_payments_on_one_sale(client, auth_headers, sale):
    first = client.post(
        "/payments/", json=payment(sale, "cash", "100.00"), headers=auth_headers
    )
    second = client.post(
        "/payments/", json=payment(sale, "mpesa", "39.20"), headers=auth_headers
    )

    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text

    listed = client.get("/payments/", headers=auth_headers)
    assert len(listed.json()) == 2


def test_create_payment_without_amount_returns_422(client, auth_headers, sale):
    response = client.post(
        "/payments/",
        json={"sale_id": sale["sale_id"], "payment_method": "cash"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_create_payment_with_bad_amount_returns_422(client, auth_headers, sale):
    response = client.post(
        "/payments/", json=payment(sale, "cash", "a lot"), headers=auth_headers
    )

    assert response.status_code == 422


def test_create_payment_without_sale_id_returns_422(client, auth_headers):
    response = client.post(
        "/payments/",
        json={"payment_method": "cash", "amount": "50.00"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_cashier_can_record_payment(client, cashier_headers, sale):
    response = client.post("/payments/", json=payment(sale), headers=cashier_headers)

    assert response.status_code == 201, response.text


def test_list_payments(client, auth_headers, sale):
    client.post("/payments/", json=payment(sale), headers=auth_headers)

    response = client.get("/payments/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


def test_get_payment_by_id(client, auth_headers, sale):
    created = client.post(
        "/payments/", json=payment(sale), headers=auth_headers
    ).json()

    response = client.get(
        f"/payments/{created['payment_id']}", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["payment_id"] == created["payment_id"]


def test_get_missing_payment_returns_404(client, auth_headers):
    response = client.get("/payments/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_update_payment_method(client, auth_headers, sale):
    created = client.post(
        "/payments/", json=payment(sale, "cash"), headers=auth_headers
    ).json()

    response = client.put(
        f"/payments/{created['payment_id']}",
        json={"payment_method": "card"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["payment_method"] == "card"


def test_update_missing_payment_returns_404(client, auth_headers):
    response = client.put(
        "/payments/9999", json={"amount": "10.00"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_payment(client, auth_headers, sale):
    created = client.post(
        "/payments/", json=payment(sale), headers=auth_headers
    ).json()

    response = client.delete(
        f"/payments/{created['payment_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/payments/{created['payment_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_delete_missing_payment_returns_404(client, auth_headers):
    assert client.delete("/payments/9999", headers=auth_headers).status_code == 404
