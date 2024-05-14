import asyncio
import time

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from gssapi import SecurityContext

from routes import drugs_route, account_route, download_route
from authentication.kerberos import KerberosAuth

from fastapi import FastAPI, Depends, HTTPException, Request
import gssapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from storage import db_instance


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

kerberos_auth = KerberosAuth()

db_instance.reload()

app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])


@app.get("/http")
async def gssapi_authenticate(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Negotiate "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        token = auth_header.split(" ")[1]
        context = gssapi.SecurityContext(creds=None, usage='accept')
        context.step(gssapi.base64_to_bytes(token))
        principal = context.initiator_name
        # Now you can authenticate 'principal' against your user database or LDAP
        # For demo purposes, we'll just print it
        print("Authenticated principal:", principal)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = {"message": "success", "principal": principal}
    return response

@app.get("/protected")
async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(kerberos_auth)):
    return {"message": "You are authorized!"}


@app.get("/")
def health():
    return {"message": "API is up and running!"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("favicon.ico")
