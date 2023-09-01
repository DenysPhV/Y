from fastapi import status


def test_root(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] =="Welcome to root"


def test_healthchecker(client):
    response = client.get("/api/healthchecker")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Welcome to FastAPI"