import time
import jwt

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

def create_token(data: dict, expires_in=3600):
    payload = data.copy()
    payload["exp"] = time.time() + expires_in
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
