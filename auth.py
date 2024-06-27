from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
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

def get_user_id_from_token(token):
    token_data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = token_data.get("user_id")
    return user_id