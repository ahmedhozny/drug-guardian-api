import base64
import logging
from datetime import timedelta, datetime
from typing import Union, Annotated, Tuple

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends, Response, Header
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from fastapi import status
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

import schemas
from authentication.auth_handler import signJWT
from authentication.authentication import Authentication
# from authentication.kerberos import KerberosMiddleware, create_access_token, get_current_user, get_auth_header, \
#     authenticate_kerberos
from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from schemas import TokenBase
from authentication.auth_bearer import AuthBearer
from authentication.auth_kerberos import AuthKerberos

from services.client import login_handling
from storage import Storage

SECRET_KEY = "ff0d69562f59c8063554d63e190411ac7a78c1322c6cf5e864a6b7b0d9f756b7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

kerberos_auth = AuthKerberos()

load_dotenv()

logging.config.dictConfig(get_uvicorn_logger_config())

app = FastAPI()
auth_bearer = AuthBearer()
combined_auth = Authentication()
# app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
uvicorn_logger.info("Starting API..")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(KerberosMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")

Storage.get_db_instance().reload()

app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# @app.get("/protected", dependencies=[Depends(get_current_user)])
# async def protected_route(request: Request):
#     principal = request.state.principal
#     return {"message": f"Hello, {principal}"}


@app.get("/")
def health():
    return {"message": "API is up and running!"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("favicon.ico")


# @app.get("/token", response_model=TokenBase)
# async def token(
#     response: Response,
#     auth: Annotated[tuple[str, Union[bytes, None]], Depends(kerberos_auth)],
# ):
#     print("/token")
#     print(auth)
#     print("/token")
#     if auth[1]:
#         response.headers["WWW-Authenticate"] = base64.b64encode(auth[1]).decode("utf-8")
#
#     access_token = create_access_token(
#         data={"iss": "HTTP/api.drugguardian.net@MEOW", "sub": auth[0]}
#     )
#
#     access_token = signJWT(auth[0])
#
#     return {"access_token": access_token.get("access_token"), "token_type": "bearer"}

@app.post("/login", response_model=TokenBase)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        authorization: Annotated[Union[str, None], Header()] = None
):
    if combined_auth.is_authenticated_with_kerberos(authorization):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already authenticated with Kerberos"
        )

    res = await login_handling(auth_bearer, username=form_data.username, password=form_data.password)
    return {"access_token": res.access_token, "token_type": res.token_type}

@app.get("/protected-route")
async def protected_route(auth: dict = Depends(combined_auth)):
    return {"message": "You are authorized"}
