import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

# from authentication.kerberos import KerberosMiddleware, create_access_token, get_current_user, get_auth_header, \
#     authenticate_kerberos
from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from storage import Storage

load_dotenv()

logging.config.dictConfig(get_uvicorn_logger_config())

app = FastAPI()

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
