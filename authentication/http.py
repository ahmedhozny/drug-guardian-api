from fastapi import Request, HTTPException, Depends
from gssapi import exceptions
import gssapi
import base64


def get_auth_header(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Negotiate '):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return auth_header[len('Negotiate '):]


def authenticate_kerberos(token: str):
    try:
        # Decode the base64 encoded token
        token = base64.b64decode(token)

        # Initialize the security context
        server_name = gssapi.Name('HTTP@kerberos.drugguardian.net', name_type=gssapi.NameType.hostbased_service)
        server_ctx = gssapi.SecurityContext(usage='accept', name=server_name)

        # Step through the GSSAPI handshake
        server_ctx.step(token)

        if not server_ctx.complete:
            raise HTTPException(status_code=401, detail="Incomplete Kerberos authentication")

        # Extract the principal of the authenticated user
        principal = str(server_ctx.initiator_name)

        return principal
    except gssapi.exceptions.GSSError as e:
        raise HTTPException(status_code=401, detail="Kerberos authentication failed") from e
