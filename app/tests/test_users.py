"""CRUD and permission rules on the /users routes."""


def test_list_users_requires_auth(client):
    assert client.get("/users/").status_code == 401


def test_admin_lists_users(client, auth_headers, cashier_user):
    response = client.get("/users/", headers=auth_headers)

    assert response.status_code == 200, response.text
    usernames = [user["username"] for user in response.json()]
    assert "testadmin" in usernames
    assert cashier_user["username"] in usernames


def test_cashier_cannot_list_users(client, cashier_headers):
    assert client.get("/users/", headers=cashier_headers).status_code == 403


def test_get_user_by_id(client, auth_headers, cashier_user):
    response = client.get(f"/users/{cashier_user['user_id']}", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["username"] == cashier_user["username"]


def test_get_missing_user_returns_404(client, auth_headers):
    response = client.get("/users/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user_via_users_route(client, auth_headers):
    response = client.post(
        "/users/",
        json={
            "first_name": "Achieng",
            "last_name": "Omollo",
            "email": "achieng@example.co.ke",
            "username": "achieng",
            "password": "strongpass123",
            "role": "manager",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    assert response.json()["role"] == "manager"
    assert response.json()["is_active"] is True


def test_create_user_with_duplicate_username_returns_409(
    client, auth_headers, cashier_user
):
    response = client.post(
        "/users/",
        json={
            "first_name": "Another",
            "last_name": "Person",
            "email": "another@example.co.ke",
            "username": cashier_user["username"],
            "password": "strongpass123",
        },
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_create_user_missing_required_field_returns_422(client, auth_headers):
    response = client.post(
        "/users/",
        json={"username": "incomplete", "password": "strongpass123"},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_update_user_details(client, auth_headers, cashier_user):
    response = client.put(
        f"/users/{cashier_user['user_id']}",
        json={"first_name": "Renamed", "role": "manager"},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["first_name"] == "Renamed"
    assert response.json()["role"] == "manager"


def test_update_user_password_allows_new_login(client, auth_headers, cashier_user):
    response = client.put(
        f"/users/{cashier_user['user_id']}",
        json={"password": "brandnewpass456"},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text

    old = client.post(
        "/auth/login",
        data={
            "username": cashier_user["username"],
            "password": cashier_user["password"],
        },
    )
    new = client.post(
        "/auth/login",
        data={"username": cashier_user["username"], "password": "brandnewpass456"},
    )

    assert old.status_code == 401
    assert new.status_code == 200


def test_update_missing_user_returns_404(client, auth_headers):
    response = client.put(
        "/users/9999", json={"first_name": "Ghost"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_update_to_taken_username_returns_409(
    client, auth_headers, cashier_user, manager_user
):
    response = client.put(
        f"/users/{cashier_user['user_id']}",
        json={"username": manager_user["username"]},
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_manager_cannot_modify_an_admin(client, manager_headers, admin_user):
    response = client.put(
        f"/users/{admin_user['user_id']}",
        json={"first_name": "Hacked"},
        headers=manager_headers,
    )

    assert response.status_code == 403
    assert "Managers cannot modify admin accounts" in response.json()["detail"]


def test_manager_cannot_promote_to_admin(client, manager_headers, cashier_user):
    response = client.put(
        f"/users/{cashier_user['user_id']}",
        json={"role": "admin"},
        headers=manager_headers,
    )

    assert response.status_code == 403
    assert "Managers cannot promote users to admin" in response.json()["detail"]


def test_admin_deletes_a_user(client, auth_headers, cashier_user):
    response = client.delete(
        f"/users/{cashier_user['user_id']}", headers=auth_headers
    )
    assert response.status_code == 204

    follow_up = client.get(
        f"/users/{cashier_user['user_id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404


def test_admin_cannot_delete_own_account(client, auth_headers, admin_user):
    response = client.delete(f"/users/{admin_user['user_id']}", headers=auth_headers)

    assert response.status_code == 400
    assert "cannot delete your own account" in response.json()["detail"]


def test_manager_cannot_delete_users(client, manager_headers, cashier_user):
    response = client.delete(
        f"/users/{cashier_user['user_id']}", headers=manager_headers
    )

    assert response.status_code == 403


def test_delete_missing_user_returns_404(client, auth_headers):
    assert client.delete("/users/9999", headers=auth_headers).status_code == 404
