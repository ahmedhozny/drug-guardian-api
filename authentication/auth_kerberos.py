from typing import Annotated, Union
import base64

from gssapi.creds import Credentials
from gssapi.names import Name
from gssapi.sec_contexts import SecurityContext

from fastapi import HTTPException, Header


class AuthKerberos:
    def __init__(self, spn: Union[str, Name, None] = None, keytab: str = './api_drugguardian.keytab'):
        if isinstance(spn, str):
            spn = Name(spn)

        store = {'keytab': keytab}
        self.creds = Credentials(usage="accept", name=spn, store=store)

    def __call__(
        self, authorization: Annotated[Union[str, None], Header()] = None
    ) -> tuple[str, Union[bytes, None]]:
        if not authorization or authorization.split(" ")[0] != "Negotiate":
            raise HTTPException(
                status_code=401, headers={"WWW-Authenticate": "Negotiate"}
            )
        ctx = SecurityContext(creds=self.creds)
        token = base64.b64decode(authorization.split(" ")[1])
        gssresp = ctx.step(token)
        if not ctx.complete:
            raise HTTPException(status_code=403)
        username = str(ctx.initiator_name)
        if isinstance(gssresp, bytes):
            return username, gssresp
        return username, None
