import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from authentication.http import get_auth_header, authenticate_kerberos
from logger import uvicorn_logger, log_middleware, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from storage import db_instance

load_dotenv()

logging.config.dictConfig(get_uvicorn_logger_config())

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
uvicorn_logger.info("Starting API..")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

db_instance.reload()

app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])


@app.middleware("http")
async def kerberos_auth_middleware(request: Request, call_next):
    try:
        token = get_auth_header(request)
        principal = authenticate_kerberos(token)
        request.state.principal = principal
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    response = await call_next(request)
    return response


@app.get("/protected")
async def protected_route(request: Request):
    principal = request.state.principal
    return {"message": f"Hello, {principal}"}


@app.get("/")
def health():
    return {"message": "API is up and running!"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("favicon.ico")
