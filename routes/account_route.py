from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import RedirectResponse

import models
import schemas
from authentication.auth_bearer import AuthBearer
from models import HospitalModel, BaseModel, EmailAddresses
from services.client import hospital_signup_request, hospital_signup_request_handle, verification_handling, \
    signup_handling
from storage import Storage

router = APIRouter()


@router.post("/healthcare", status_code=status.HTTP_201_CREATED)
async def create_healthcare(hosp=Depends(hospital_signup_request)):
    return hosp


@router.get("/pending")
async def get_pending(org: str):
    objs: List[BaseModel]
    if org == "hosp":
        objs: List[HospitalModel] = await Storage.find(HospitalModel, {HospitalModel.status: "Unconfirmed"})
    else:
        raise HTTPException(400, "Bad Request")

    res = []
    for obj in objs:
        db_emails: List[EmailAddresses] = await Storage.find(EmailAddresses, {EmailAddresses.organization_uuid: obj.uuid_registry})
        if len(db_emails) < 1:
            continue
        to_dict = obj.to_dict()
        to_dict["email"] = db_emails[0].email
        res.append(to_dict)

    return res


@router.post("/pending", status_code=status.HTTP_201_CREATED)
async def update_pending(res=Depends(hospital_signup_request_handle)):
    return res


@router.get("/verify")
async def get_verify(res=Depends(verification_handling)):
    email = res["email"]
    token = res["token"]
    return RedirectResponse(f"./register_step?email={email}&token={token}", status.HTTP_302_FOUND)


@router.get("/register_step", status_code=status.HTTP_200_OK)
async def get_registration(email: str, token: str):
    payload = await verification_handling(token)
    if email != payload["email"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email and token mismatch")
    return "OK"


@router.post("/register_step", status_code=status.HTTP_201_CREATED)
async def post_registration(res=Depends(signup_handling)):
    return {"keytab": res["keytab_password"]}



@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login():
    pass


@router.get("/accounts/")
async def get_accounts():
    clients = Storage.get_db_instance().filter(models.AccountDetails).all()
    return clients
