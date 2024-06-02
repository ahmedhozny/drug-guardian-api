import logging
from fastapi import Request, HTTPException
from gssapi import exceptions
import gssapi
import base64

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_auth_header(request: Request):
    auth_header = request.headers.get('Authorization')
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
