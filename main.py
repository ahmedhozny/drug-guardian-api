import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from authentication.http import get_auth_header, authenticate_kerberos
from authentication.kerberos import KerberosMiddleware, create_access_token, get_current_user
from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from schemes.token import TokenResponse
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

app.add_middleware(KerberosMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")

db_instance.reload()

app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])


async def kerberos_auth_dependency(request: Request):
    try:
        token = get_auth_header(request)
        principal = authenticate_kerberos(token)
        request.state.principal = principal
    except HTTPException as e:
        logging.error(f"Authentication failed: {e.detail}")
        raise HTTPException(status_code=e.status_code, headers={"WWW-Authenticate": "Negotiate"}, detail=e.detail)


@app.get("/protected", dependencies=[Depends(get_current_user)])
async def protected_route(request: Request):
    principal = request.state.principal
    return {"message": f"Hello, {principal}"}


@app.get("/")
def health():
    return {"message": "API is up and running!"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("favicon.ico")


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return get_openapi(
        title="FastAPI Kerberos Auth",
        version="1.0.0",
        description="API with Kerberos authentication",
        routes=app.routes,
    )


@app.post("/token", response_model=TokenResponse, dependencies=[Depends(kerberos_auth_dependency)])
async def generate_token(request: Request):
    principal = request.state.principal
    access_token = create_access_token(data={"sub": principal})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/docs1", include_in_schema=False)
async def custom_swagger_ui_html():
    return HTMLResponse(content=open("static/custom_swagger.html").read())