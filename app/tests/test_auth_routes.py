"""Registration, login and token handling on the /auth routes."""


def test_first_registration_becomes_admin(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Otieno",
            "last_name": "Odhiambo",
            "email": "otieno@example.co.ke",
            "username": "otieno",
            "password": "strongpass123",
            "role": "cashier",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["role"] == "admin"


def test_second_public_registration_is_blocked(client, admin_user):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Second",
            "last_name": "Person",
            "email": "second@example.co.ke",
            "username": "second",
            "password": "strongpass123",
        },
    )

    assert response.status_code == 403
    assert "Public registration is disabled" in response.json()["detail"]


def test_register_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Short",
            "last_name": "Pass",
            "email": "short@example.co.ke",
            "username": "shortpass",
            "password": "abc",
        },
    )

    assert response.status_code == 422


def test_register_rejects_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Bad",
            "last_name": "Email",
            "email": "not-an-email",
            "username": "bademail",
            "password": "strongpass123",
        },
    )

    assert response.status_code == 422


def test_register_rejects_unknown_role(client):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Bad",
            "last_name": "Role",
            "email": "badrole@example.co.ke",
            "username": "badrole",
            "password": "strongpass123",
            "role": "supervisor",
        },
    )

    assert response.status_code == 422


def test_login_returns_token_and_user(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": admin_user["username"], "password": admin_user["password"]},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["username"] == admin_user["username"]
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_login_with_wrong_password_returns_401(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": admin_user["username"], "password": "totallywrong"},
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_with_unknown_username_returns_401(client, admin_user):
    response = client.post(
        "/auth/login", data={"username": "ghost", "password": "testpass123"}
    )

    assert response.status_code == 401


def test_me_without_token_returns_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_with_malformed_token_returns_401(client):
    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer not.a.real.token"}
    )

    assert response.status_code == 401


def test_me_returns_the_logged_in_user(client, auth_headers, admin_user):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["username"] == admin_user["username"]
    assert response.json()["role"] == "admin"


def test_admin_can_create_staff_user(client, auth_headers):
    response = client.post(
        "/auth/users",
        json={
            "first_name": "New",
            "last_name": "Cashier",
            "email": "newcashier@example.co.ke",
            "username": "newcashier",
            "password": "strongpass123",
            "role": "cashier",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    assert response.json()["role"] == "cashier"


def test_duplicate_username_returns_409(client, auth_headers, cashier_user):
    response = client.post(
        "/auth/users",
        json={
            "first_name": "Copy",
            "last_name": "Cat",
            "email": "copycat@example.co.ke",
            "username": cashier_user["username"],
            "password": "strongpass123",
            "role": "cashier",
        },
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_cashier_cannot_create_users(client, cashier_headers):
    response = client.post(
        "/auth/users",
        json={
            "first_name": "Sneaky",
            "last_name": "User",
            "email": "sneaky@example.co.ke",
            "username": "sneaky",
            "password": "strongpass123",
            "role": "manager",
        },
        headers=cashier_headers,
    )

    assert response.status_code == 403


def test_manager_cannot_create_an_admin(client, manager_headers):
    response = client.post(
        "/auth/users",
        json={
            "first_name": "Wannabe",
            "last_name": "Admin",
            "email": "wannabe@example.co.ke",
            "username": "wannabe",
            "password": "strongpass123",
            "role": "admin",
        },
        headers=manager_headers,
    )

    assert response.status_code == 403
    assert "Managers cannot create admin accounts" in response.json()["detail"]


def test_manager_can_create_a_cashier(client, manager_headers):
    response = client.post(
        "/auth/users",
        json={
            "first_name": "Junior",
            "last_name": "Cashier",
            "email": "junior@example.co.ke",
            "username": "junior",
            "password": "strongpass123",
            "role": "cashier",
        },
        headers=manager_headers,
    )

    assert response.status_code == 201, response.text


def test_deactivated_user_cannot_log_in(client, auth_headers, cashier_user):
    deactivate = client.put(
        f"/users/{cashier_user['user_id']}",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert deactivate.status_code == 200, deactivate.text

    response = client.post(
        "/auth/login",
        data={
            "username": cashier_user["username"],
            "password": cashier_user["password"],
        },
    )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"]


def test_token_of_deactivated_user_stops_working(client, auth_headers, cashier_user):
    cashier = client.post(
        "/auth/login",
        data={
            "username": cashier_user["username"],
            "password": cashier_user["password"],
        },
    )
    headers = {"Authorization": f"Bearer {cashier.json()['access_token']}"}
    assert client.get("/auth/me", headers=headers).status_code == 200

    client.put(
        f"/users/{cashier_user['user_id']}",
        json={"is_active": False},
        headers=auth_headers,
    )

    assert client.get("/auth/me", headers=headers).status_code == 401
