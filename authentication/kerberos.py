from typing import Optional
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from gssapi import SecurityContext, NameType
from base64 import b64decode
from authentication.schemes import Login as LoginScheme
from spnego import server

service_principal = "HTTP/<your_server_hostname>@<your_realm>"  # Replace with your details
spnego_server = server(service=service_principal, protocol="negotiate")


async def kerberos_auth(request: Request):
    try:
        # Extract and validate Kerberos token from Authorization header
        token = request.headers.get("Authorization", None)
        if not token or not token.startswith("Negotiate "):
            raise HTTPException(401, detail="Unauthorized")
        user = spnego_server.unwrap(token.split()[1])  # Validate token
        return user  # Return the authenticated user
    except Exception as e:
        raise HTTPException(401, detail=str(e))


class KerberosAuth(HTTPBearer):
    def __init__(self):
        super().__init__()

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)
        if credentials:
            # Validate the Kerberos token
            try:
                # Decode the base64 encoded token
                token_bytes = b64decode(credentials.credentials)
                # Create a new security context
                ctx = SecurityContext(name_type=NameType.kerberos_v5_principal)
                # Accept the incoming Kerberos token
                ctx.accept(token_bytes)
                if ctx.complete:
                    return credentials
            except Exception as e:
                print("Error during Kerberos authentication:", e)
        raise HTTPException(status_code=401, detail="Invalid Kerberos credentials")
