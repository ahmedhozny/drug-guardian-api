import base64

from gssapi import exceptions
from datetime import datetime, timedelta
import jwt

import gssapi
import spnego
from fastapi import Request, HTTPException, Depends
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

        # Initialize the SPNEGO context
        context = spnego.server()
        response_token = context.step(token)

        if not context.complete:
            logger.error("Incomplete SPNEGO authentication")
            raise HTTPException(status_code=401, detail="Incomplete SPNEGO authentication")

        # Extract the principal of the authenticated user
        principal = context.peer_name
        logger.info(f"Authenticated principal: {principal}")

        response_header = {
            "WWW-Authenticate": "Negotiate " + base64.b64encode(response_token).decode()
        }
        return principal, response_header
    except spnego.exceptions.SpnegoError as e:
        logger.error(f"SPNEGO authentication failed: {e}")
        raise HTTPException(status_code=401, detail="SPNEGO authentication failed") from e


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

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from fastapi import Security

SECRET_KEY = "your_secret_key"  # Change this to your secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_user(token: str = Depends(security)):
    return verify_token(token)
