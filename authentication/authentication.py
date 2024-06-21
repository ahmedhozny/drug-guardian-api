from typing import Union, Tuple, Annotated

from fastapi import HTTPException, Header, Depends
from fastapi.requests import Request
from fastapi import status

from gssapi.names import Name
from gssapi.sec_contexts import SecurityContext
from passlib.context import CryptContext

from authentication.auth_bearer import AuthBearer
from authentication.auth_kerberos import AuthKerberos


class Authentication:
    def __init__(self, spn: Union[str, Name, None] = None):
        self.kerberos_auth = AuthKerberos(spn)
        self.bearer_auth = AuthBearer()

    async def __call__(
        self, authorization: Annotated[Union[str, None], Header()] = None, token: str = Depends(AuthBearer.oauth2_scheme)
    ):
        try:
            username, gssresp = self.kerberos_auth(authorization)
            return {"username": username, "gss_response": gssresp}
        except HTTPException as kerberos_exc:
            if kerberos_exc.status_code == status.HTTP_401_UNAUTHORIZED:
                try:
                    token = await self.bearer_auth(token)
                    return {"token": token}
                except HTTPException as bearer_exc:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                        headers={"WWW-Authenticate": "Negotiate, Bearer"},
                    )
            raise kerberos_exc

    def is_authenticated_with_kerberos(self, authorization: Annotated[Union[str, None], Header()] = None) -> bool:
        try:
            username, _ = self.kerberos_auth(authorization)
            return True
        except HTTPException:
            return False
