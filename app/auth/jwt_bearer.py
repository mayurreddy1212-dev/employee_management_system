from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from app.auth.jwt_handler import decode_token

class JWTBearer(HTTPBearer):
    def __init__(self, roles: list = None, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.roles = roles or []

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)

        if credentials:
            token = credentials.credentials
            payload = decode_token(token)

            if payload is None:
                raise HTTPException(status_code=403, detail="Invalid or expired token")

            # Role protection
            if self.roles and payload.get("role") not in self.roles:
                raise HTTPException(status_code=403, detail="Not allowed")

            return payload
        else:
            raise HTTPException(status_code=403, detail="Token missing")
