import pytest
import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from datetime import datetime

from PhotoShare.app.models.user import User
from PhotoShare.app.repositories.users import create_user, get_user_by_email, set_user_confirmation, user_login, \
    refresh_token


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("PhotoShop.app.repositories.users", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


