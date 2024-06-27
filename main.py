import logging

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from logger import uvicorn_logger, get_uvicorn_logger_config
from routes import drugs_route, account_route, download_route
from schemas import SideEffectsPrediction
from services.other_services import check_server_health, find_lightest_instance
from storage import Storage

load_dotenv()

# Configure logging
logging.config.dictConfig(get_uvicorn_logger_config())

# Dictionary to keep track of server load
model_instances_load = {
    "http://34.34.86.5": 0,
    "http://35.204.234.100": 0
}

# Initialize FastAPI application
app = FastAPI()

uvicorn_logger.info("Starting API..")

# Add middleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database
Storage.get_db_instance().reload()

# Include route modules
app.include_router(drugs_route.router, prefix="/drugs", tags=["drugs"])
app.include_router(account_route.router, prefix="/account", tags=["account"])
app.include_router(download_route.router, prefix="/download", tags=["download"])


# @app.get("/protected", dependencies=[Depends(get_current_user)])
# async def protected_route(request: Request):
#     principal = request.state.principal
#     return {"message": f"Hello, {principal}"}


@app.get("/")
def health():
    """
    Health check endpoint.
    Returns a message indicating that the API is up and running.
    """
    return {"message": "API is up and running!"}


@app.get("/favicon.ico")
def favicon():
    """
    Endpoint to serve the favicon.
    """
    return FileResponse("favicon.ico")


import os
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

app = FastAPI()

UPLOAD_DIRECTORY = "uploads/"  # Directory where files will be stored
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Ensure the upload directory exists
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

@app.post("/submit-request")
async def submit_request(
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        message: str = Form(...),
        file: UploadFile = File(...),
        user = Depends(account_route.auth_bearer.get_current_user)
):
    """
    Endpoint to submit a request with form data and a file upload.

    Args:
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        email (str): Email of the user.
        message (str): Message from the user.
        file (UploadFile): Uploaded file.

    Returns:
        dict: A dictionary containing the submitted data and file information.
    """
    try:
        # Save the uploaded file
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

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

    return JSONResponse(content=response_data)


@app.post("/predictSynergy")
async def check_interactions(drug1_smiles: str = Form(...), drug2_smiles: str = Form(...)):
    """
    Endpoint to check drug synergy interactions.

    Args:
        drug1_smiles (str): SMILES representation of the first drug.
        drug2_smiles (str): SMILES representation of the second drug.

    Returns:
        dict: The response from the synergy prediction server.
    """
    lowest_key = find_lightest_instance(model_instances_load)
    model_instances_load[lowest_key] += 1
    res = requests.post(lowest_key + "/synergy", json={"drug1_smiles": drug1_smiles, "drug2_smiles": drug2_smiles})
    model_instances_load[lowest_key] -= 1
    if res.status_code != 200:
        raise HTTPException(res.status_code, detail=res.text)
    return res.json()


@app.post("/sideEffects")
async def check_side_effects(response: SideEffectsPrediction):
    """
    Endpoint to check side effects of drugs.

    Args:
        response (SideEffectsPrediction): The prediction response object.

    Returns:
        dict: The response from the side effects prediction server.
    """
    lowest_key = find_lightest_instance(model_instances_load)
    model_instances_load[lowest_key] += 1
    try:
        res = requests.post(lowest_key + "/side_effects", json=response.dict())
        model_instances_load[lowest_key] -= 1
        if res.status_code == 200:
            try:
                return res.json()
            except requests.exceptions.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid JSON response from server")
        else:
            raise HTTPException(status_code=res.status_code, detail=res.text)
    except requests.exceptions.RequestException as e:
        model_instances_load[lowest_key] -= 1
        raise HTTPException(status_code=500, detail=str(e))

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
