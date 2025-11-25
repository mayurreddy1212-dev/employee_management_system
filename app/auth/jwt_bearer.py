from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException
from .jwt_handler import verify_token

class JWTBearer(HTTPBearer):
    def __init__(self, roles: list = None):
        super(JWTBearer, self).__init__()
        self.roles = roles or []

    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        token = auth.credentials
        payload = verify_token(token)

        if payload is None:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

        if self.roles and payload.get("role") not in self.roles:
            raise HTTPException(status_code=403, detail="Not authorized")

        return payload
