import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from authentication.http import get_auth_header, authenticate_kerberos
from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from storage import db_instance

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

db_instance.reload()

app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])


async def kerberos_auth_dependency(request: Request):
    try:
        print(request.headers)
        token = get_auth_header(request)
        principal = authenticate_kerberos(token)
        request.state.principal = principal
    except HTTPException as e:
        logging.error(f"Authentication failed: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail}, headers={"WWW-Authenticate": "Negotiate"})


@app.get("/protected", dependencies=[Depends(kerberos_auth_dependency)])
async def protected_route(request: Request):
    principal = request.state.principal
    return {"message": f"Hello, {principal}"}


@app.get("/")
def health():
    return {"message": "API is up and running!"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("favicon.ico")
