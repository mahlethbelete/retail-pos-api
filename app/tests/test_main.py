def test_read_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200

    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["message"] == "Pos API is active"


def test_docs_endpoint_accessible(client):
    response = client.get("/docs")
    assert response.status_code == 200