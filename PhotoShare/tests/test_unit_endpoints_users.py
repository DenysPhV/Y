import pytest
from fastapi import status

from PhotoShare.app.models.user import User, UserRole


@pytest.fixture(scope='function')
def token(client, user, session):
    client.post("/auth/signup",
                json={"username": "deadpool",
                      "email": "deadpool@example.com",
                      "password": "qwerty123456",
                      "first_name": "dead",
                      "last_name": "pool"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    if current_user is None:
        print("User not found in the database.")  # Debugging line
        raise Exception("User not found")
    # assert current_user is not None, "User not found"
    current_user.role = UserRole.Admin
    session.commit()

    response = client.post("/auth/login",
                           data={"username": "deadpool",
                                 "password": "123456789"},
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    if "access_token" in data:
        return data["access_token"]
    else:
        raise Exception("Token not found in the response")
    # return data["access_token"]


@pytest.fixture(scope="function")
def token_second(client, user, session):
    client.post("/auth/signup",
                json={"username": "deadpool",
                      "email": "deadpool@example.com",
                      "password": "123456789"})
    current_user: User = session.query(User).filter(User.email == "deadpool@example.com").first()
    if current_user is None:
        print("User not found in the database.")  # Debugging line
        raise Exception("User not found")
    # assert current_user is not None, "User not found"
    current_user.role = UserRole.Admin
    session.commit()

    response = client.post("/auth/login",
                           data={"username": "deadpool",
                                 "password": "123456789"},
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    if "access_token" in data:
        return data["access_token"]
    else:
        raise Exception("Token not found in the response")
    # return data["access_token"]


def test_read_user_me(client, token):
    response = client.get("/user/me",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    response = client.get("/user/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_user_profile_by_username(client, token, user):
    login = user['login']
    response = client.get(f"/user/user/{login}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    login = 'test_wrong_login'
    response = client.get(f"/user/user/{login}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_change_role(client, user, token):
    response = client.put("/user/change_role",
                          json={
                              "id": 1000,
                              "role": 2,
                              },
                          headers={"Authorization": f"Bearer {token}"},)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.put("/user/change_role",
                          json={
                              "id": 1,
                              "role": 2,
                              },
                          headers={"Authorization": f"Bearer {token}"},)
    assert response.status_code == status.HTTP_200_OK

    response = client.put("/user/change_role")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user(client, token):
    response = client.put("/user/update_user",
                          json={
                              "id": 12121,
                              "email": "deadpool@example.com",
                              "updated_at": "2023-05-21T16:35:59.380Z",
                              "photo_url": "string",
                              "name": "dead",
                              "password": "123456789"},
                          headers={"Authorization": f"Bearer {token}"},)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.put("/user/update_user",
                          headers={"Authorization": f"Bearer {token}"},
                          json={
                              "id": 1,
                              "email": "deadpool@example.com",
                              "updated_at": "2023-05-21T16:35:59.380Z",
                              "photo_url": "str495y2074y5804ying",
                              "name": "dead",
                              "password": "123456789"})
    assert response.status_code == status.HTTP_200_OK

    response = client.put("/user/update_user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user_by_admin(client, refresh_token):
    response = client.put("/user/update_user_by_admin",
                          json={"id": 100,
                                "username": "deadpool_2",
                                "name": "deadpool_2",
                                "email": "testpool@example.com",
                                "is_active": True,
                                "role": 1,
                                "photo_url": "",
                                "password": "test123456789",
                                "updated_at": "2023-05-21T16:35:59.380Z"},
                          headers={"Authorization": f"Bearer {refresh_token}"},)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.put("user/update_user_by_admin",
                          json={"id": 1,
                                "username": "deadpool_f",
                                "name": "dead_f",
                                "email": "testfffftest@example.com",
                                "is_active": True,
                                "role": 1,
                                "user_pic_url": "",
                                "password": "test123456789f",
                                "updated_at": "2023-05-21T16:35:59.380Z"},
                          headers={"Authorization": f"Bearer {refresh_token}"},)
    assert response.status_code == status.HTTP_200_OK
    print(response.json())

    response = client.put("/user/update_user_by_admin")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_ban_user(client, user, token):
    response = client.put(f"user/ban_user/?user_id=1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    response = client.put(f"user/ban_user/?user_id=100", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
