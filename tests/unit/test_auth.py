from datetime import UTC, datetime, timedelta

import jwt
import pytest

from src.core.config import settings
from src.core.jwt import ALGORITHM, create_access_token, decode_access_token
from src.core.security import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_create_and_decode_access_token() -> None:
    token = create_access_token(42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_expired_access_token() -> None:
    expire = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "1", "exp": expire},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
