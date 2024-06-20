from datetime import datetime, timedelta, timezone
import jwt
from pydantic import BaseModel

SECRET_KEY = "c9e4fb232f67c14d6d85b84ada2e9ee785cd37a4e0a39fc745bdb75bd8e8379b"
ALGORITHM = "HS256"
EXPIRE_DAYS = 7

def gen_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token):
    token_data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id: int = token_data.get("user_id")
    name: str = token_data.get("name")
    email: str = token_data.get("email")
    user_data = {
			"id": user_id,
			"name": name,
			"email": email
		}
    return user_data
