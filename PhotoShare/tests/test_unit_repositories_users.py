import pytest
import unittest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from sqlalchemy.orm import Session

from PhotoShare.app.repositories.users import create_user
from PhotoShare.app.schemas.user import UserModel
from PhotoShare.app.models.user import User


# Mocking SQLAlchemy Session
class MockSession:
    def query(self, model):
        return self

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return None

    def add(self, obj):
        return None

    def commit(self):
        return None

    def refresh(self, obj):
        return None


# Mocking libgravatar.Gravatar
class MockGravatar:
    def get_image(self):
        return "mock_avatar_url"


@pytest.mark.asyncio
async def test_create_user():
    # Given
    session = MockSession()
    user_model = UserModel(email="test@example.com", password="testpassword")
    mock_get_user_by_email = AsyncMock(return_value=None)

    # When
    with patch("PhotoShare.app.repositories.users.get_user_by_email", mock_get_user_by_email):
        with patch("libgravatar.Gravatar.get_image", MockGravatar().get_image):  # MockGravatar
            from PhotoShare.app.repositories.users import create_user
            created_user = await create_user(user_model, session)

    # Then
    assert created_user.email == "test@example.com"
    assert created_user.avatar == "mock_avatar_url"
    mock_get_user_by_email.assert_called_once_with("test@example.com", session)


if __name__ == '__main__':
    unittest.main()
