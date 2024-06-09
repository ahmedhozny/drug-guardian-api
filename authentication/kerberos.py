import base64

from gssapi import exceptions
from datetime import datetime, timedelta
import jwt

import gssapi
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_auth_header(request: Request):
    auth_header = request.headers.get('Authorization')
    logger.debug(f"Authorization header: {auth_header}")
    if not auth_header or not auth_header.startswith('Negotiate '):
        logger.error("Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return auth_header[len('Negotiate '):]


def authenticate_kerberos(token: str):
    try:
        # Decode the base64 encoded token
        token = base64.b64decode(token)

        # Initialize the security context
        server_ctx = gssapi.SecurityContext(usage='accept')

        # Step through the GSSAPI handshake
        server_ctx.step(token)

        if not server_ctx.complete:
            logger.error("Incomplete Kerberos authentication")
            raise HTTPException(status_code=401, detail="Incomplete Kerberos authentication")

        # Extract the principal of the authenticated user
        principal = str(server_ctx.initiator_name)
        logger.info(f"Authenticated principal: {principal}")

        return principal
    except gssapi.exceptions.GSSError as e:
        logger.error(f"Kerberos authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Kerberos authentication failed") from e


class KerberosMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/protected"):
            print()
            print("[{}]".format(request.headers))
            print()
            try:
                token = get_auth_header(request)
                principal = authenticate_kerberos(token)
                request.state.principal = principal
            except HTTPException as e:
                logging.error(f"Authentication failed: {e.detail}")
                return JSONResponse(status_code=e.status_code, content={"detail": e.detail},
                                    headers={"WWW-Authenticate": "Negotiate"})
        response = await call_next(request)
        return response


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
