import base64
import logging
from datetime import timedelta, datetime
from typing import Union, Annotated

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from authentication.auth_bearer import JWTBearer
from authentication.auth_handler import signJWT
from fastapi_gssapi import GSSAPIAuth
# from authentication.kerberos import KerberosMiddleware, create_access_token, get_current_user, get_auth_header, \
#     authenticate_kerberos
from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from schemes.token import TokenResponse
from storage import db_instance

SECRET_KEY = "ff0d69562f59c8063554d63e190411ac7a78c1322c6cf5e864a6b7b0d9f756b7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

gssapi_auth = GSSAPIAuth("HTTP@api.drugguardian.net")

load_dotenv()

logging.config.dictConfig(get_uvicorn_logger_config())

app = FastAPI()
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

db_instance.reload()

app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])
app.include_router(account_route.router, prefix="/account", tags=["account"])


# async def kerberos_auth_dependency(request: Request):
#     try:
#         token = get_auth_header(request)
#         principal = authenticate_kerberos(token)
#         request.state.principal = principal
#     except HTTPException as e:
#         logging.error(f"Authentication failed: {e.detail}")
#         raise HTTPException(status_code=e.status_code, headers={"WWW-Authenticate": "Negotiate"}, detail=e.detail)


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


@app.get("/token", response_model=TokenResponse)
async def token(
        response: Response,
        auth: Annotated[tuple[str, Union[bytes, None]], Depends(gssapi_auth)],
):
    print("/token")
    print(auth)
    print("/token")
    if auth[1]:
        response.headers["WWW-Authenticate"] = base64.b64encode(auth[1]).decode("utf-8")

    access_token = create_access_token(
        data={"iss": "HTTP/api.drugguardian.net@MEOW", "sub": auth[0]}
    )

    access_token = signJWT(auth[0])

    return {"access_token": access_token.get("access_token"), "token_type": "bearer"}


@app.get("/token/manual", response_class=HTMLResponse)
async def manual_token_entry():
    html_content = """
    <html>
        <head>
            <title>Manual Token Entry</title>
        </head>
        <body>
            <form action="/protected" method="get">
                <label for="token">Enter Token:</label>
                <input type="text" id="token" name="token">
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


oauth2_scheme = JWTBearer()


@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Validate token (e.g., using jwt.decode or other validation methods)
    return {"message": "You have accessed a protected route!", "token": token}
