import io
import datetime

import pytest
import qrcode

from PIL import Image as PILImage
from fastapi import status

from PhotoShare.app.models.photo import Photo
from PhotoShare.app.models.user import User, UserRole


@pytest.fixture(scope='module')
def token(client, user, session):
    response = client.post("auth/signup",
                           json={"username": "deadpool",
                                 "email": "deadpool@example.com",
                                 "password_checksum": "123456789",
                                 "first_name": "dead",
                                 "last_name": "pool"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    if current_user is not None:
        current_user.role = UserRole.Admin
        session.commit()
    else:
        raise Exception("User not found")
    response = client.post("auth/login", data={
        "username": "deadpool@example.com",
        "password": "123456789"}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope='module')
def token_moder(client, user_moder, session):
    response = client.post("auth/signup", json={"login": "dead2pool", "email": "dead2pool@example.com",
                                                     "password_checksum": "123456789"})
    current_user: User = session.query(User).filter(User.email == user_moder.get('email')).first()
    if current_user is not None:
        current_user.role = UserRole.Admin
        session.commit()
    else:
        raise Exception("User not found")
    response = client.post("auth/login", data={
        "username": "dead2pool@example.com",
        "password": "123456789"}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope='module')
def token_user(client, user_user, session):
    response = client.post("auth/signup", json={"login": "dead1pool", "email": "dead1pool@example.com",
                                                     "password_checksum": "123456789"})
    response = client.post("auth/login", data={
        "username": "dead1pool@example.com",
        "password": "123456789"}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope='module')
def photo(client, user, session):
    response = client.post("auth/signup", json={"login": "deadpool", "email": "deadpool@example.com",
                                                     "password_checksum": "123456789"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    photo = session.query(Photo).filter(Photo.id == 1).first()
    if photo is None:
        photo = Photo(
            id=1,
            photo_url="https://res.cloudinary.com/dy9mhswnt/image/upload/c_fill,g_faces,h_500,r_max,w_500"
                      "/v1/photoshare/473db2aa2c097073b2e971767d76f543960ce141f4acf4671e82369de8526e9e",
            user_id=current_user.id,
            created_at=datetime.datetime.now(),
            description="test_photo_test_photo_test_photo_test_photo"
        )
        session.add(photo)
        session.commit()
        session.refresh(photo)
    return photo


@pytest.fixture(scope='module')
def photo_moder(client, user_moder, session):
    response = client.post("auth/signup", json={"login": "dead2pool", "email": "dead2pool@example.com",
                                                     "password_checksum": "123456789"})
    current_user: User = session.query(User).filter(User.email == user_moder.get('email')).first()
    photo = session.query(Photo).filter(Photo.id == 2).first()
    if photo is None:
        photo = Photo(
            id=2,
            photo_url="https://res.cloudinary.com/dy9mhswnt/image/upload/c_fill,g_faces,h_500,r_max,w_500"
                      "/v1/photoshare/223db2aa2c097073b2e971767d76f543960ce141f4acf4671e82369de8526e9e",
            user_id=current_user.id,
            created_at=datetime.datetime.now(),
            description="test_photo_test_photo_test_photo_test_photo"
        )
        session.add(photo)
        session.commit()
        session.refresh(photo)
    return photo


@pytest.fixture(scope='module')
def photo_user(client, user_user, session):
    response = client.post("auth/signup", json={"login": "dead1pool", "email": "dead1pool@example.com",
                                                     "password_checksum": "123456789"})
    current_user: User = session.query(User).filter(User.email == user_user.get('email')).first()
    photo = session.query(Photo).filter(Photo.id == 3).first()
    if photo is None:
        photo = Photo(
            id=3,
            photo_url="https://res.cloudinary.com/dy9mhswnt/image/upload/c_fill,g_faces,h_500,r_max,w_500"
                      "/v1/photoshare/333db2aa2c097073b2e971767d76f543960ce141f4acf4671e82369de8526e9e",
            user_id=current_user.id,
            created_at=datetime.datetime.now(),
            description="test_image_test_image_test_image_test_image"
        )
        session.add(photo)
        session.commit()
        session.refresh(photo)
    return photo


def test_create_transformation_photo_by_admin(client, token, photo):
    response = client.post("photos/transformation", json={"id": 1, "transformation": "standard"},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post("photos/transformation", json={"id": 1, "transformation": "standard"},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_409_CONFLICT
    response = client.post("photos/transformation", json={"id": 100, "transformation": "standard"},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.post("photos/transformation", json={"id": 100, "transformation": "test"},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_transformation_image_by_moder(client, token_moder, photo_moder):
    response = client.post("photos/transformation", json={"id": 2, "transformation": "standard"},
                           headers={"Authorization": f"Bearer {token_moder}"})
    assert response.status_code == status.HTTP_201_CREATED


def test_create_transformation_image_by_user(client, token_user, photo_user):
    response = client.post("photos/transformation", json={"id": 3, "transformation": "standard"},
                           headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post("photos/transformation", json={"id": 100, "transformation": "standard"},
                           headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_photos_by_admin(client, token):
    response = client.get("images/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    response = client.get("images/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_photos_by_moder(client, token_moder):
    response = client.get("images/", headers={"Authorization": f"Bearer {token_moder}"})
    assert response.status_code == status.HTTP_200_OK


def test_get_photos_by_user(client, token_user):
    response = client.get("images/", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_200_OK


def test_get_photo_by_admin(client, token, photo):
    response = client.get("photos/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    response = client.get("photos/100", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.get("photos/{image_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_photo_moder(client, token_moder, photo_moder):
    response = client.get("photos/2", headers={"Authorization": f"Bearer {token_moder}"})
    assert response.status_code == status.HTTP_200_OK


def test_get_photo_by_user(client, token_user, photo_user):
    response = client.get("photos/3", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_200_OK
    response = client.get("photos/100", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.get("photos/{image_id}", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_description_photo_by_admin(client, token, photo):
    response = client.patch("photos/description/1", json={
        "description": "description_description_description",
        "tags_text": "python"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["description"] == "description_description_description"
    response = client.patch("photos/description/100", json={
        "description": "description_description_description",
        "tags_text": "python"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.patch("photos/description/{image_id}", json={"descri": "n"},
                            headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_description_photo_by_user(client, token_user, photo_user):
    response = client.patch("photos/description/3", json={
        "description": "description_description_description",
        "tags_text": "python"}, headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["description"] == "description_description_description"
    response = client.patch("photos/description/100", json={
        "description": "description_description_description",
        "tags_text": "python"}, headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.patch("photos/description/{image_id}", json={"descri": "n"},
                            headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_remove_photo_by_admin(client, token, photo):
    response = client.delete("photos/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.delete("photos/100", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.delete("photos/{photo_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_remove_photo_by_moder(client, token_moder, photo_moder):
    response = client.delete("photos/2", headers={"Authorization": f"Bearer {token_moder}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = client.delete("photos/100", headers={"Authorization": f"Bearer {token_moder}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = client.delete("photos/{photo_id}", headers={"Authorization": f"Bearer {token_moder}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_photo_by_user(client, token_user, photo_user):
    response = client.delete("photo/3", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = client.delete("photo/100", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response = client.delete("photo/{photo_id}", headers={"Authorization": f"Bearer {token_user}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_photo(client, token):
    image_file = io.BytesIO()
    image = PILImage.new('RGB', size=(100, 100), color=(255, 0, 0))
    image.save(image_file, 'jpeg')
    image_file.seek(0)
    response = client.post(
        "photos",
        data={"description": "test_image_test_image_test_image_test_image",
              "tags_text": "#python",
              },
        files={"image_file": ("test.jpg", image_file, "image/jpeg")}
        ,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["description"] == "test_image_test_image_test_image_test_image"
    assert "id" in data
    image_file = io.BytesIO()
    image = PILImage.new('RGB', size=(100, 100), color=(255, 110, 0))
    image.save(image_file, 'jpeg')
    image_file.seek(0)

    response = client.post(
        "photos",
        data={"description": "sma",
              "tags_text": "#python",
              },
        files={"image_file": ("test.jpg", image_file, "image/jpeg")}
        ,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_generate_qrcode(client, token):
    response = client.post("/generate_qrcode/100", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4,
    )
    qr.add_data("test")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output = io.BytesIO()
    img.save(output)
    output.seek(0)
    response = client.post("/generate_qrcode/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_201_CREATED
