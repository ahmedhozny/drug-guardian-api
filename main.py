import logging
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import Request
from starlette.staticfiles import StaticFiles

# from authentication.kerberos import KerberosMiddleware, create_access_token, get_current_user, get_auth_header, \
#     authenticate_kerberos
from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from schemas import SideEffectsPrediction
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


@app.post("/submit-request")
async def submit_request(
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        message: str = Form(...),
        file: UploadFile = File(...)
):
    # Process the form data here
    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
    }

    response_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "message": message,
        "file": file_info
    }

    return response_data


@app.post("/predictSynergy")
async def check_interactions(drug_1: str = Form(...), drug_2: str = Form(...)):
    return {"message": "OK"}


@app.post("/sideEffects")
async def check_side_effects(response: SideEffectsPrediction):
    return {"message": "OK"}

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
