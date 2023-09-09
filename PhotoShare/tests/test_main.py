from unittest.mock import patch

from main import startup


def test_startup():
    with patch("PhotoShare.app.services.redis.RedisService.init", autospec=True) as mock_init:
        startup()
        mock_init.assert_called_once()
