from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import RedirectResponse

from models import HospitalModel, BaseModel, EmailAddresses, PharmaceuticalModel, \
    ResearcherModel
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
    if org == "hospital":
        objs: List[HospitalModel] = await Storage.find(HospitalModel, {HospitalModel.status: "Unconfirmed"})
    elif org == "pharmaceutical":
        objs: List[PharmaceuticalModel] = await Storage.find(PharmaceuticalModel, {PharmaceuticalModel.status: "Unconfirmed"})
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
async def get_accounts(org: str):
    org_class = {
        "hospital": HospitalModel,
        "pharmaceutical": PharmaceuticalModel,
        "researcher": ResearcherModel,
    }.get(org)

    if org_class is None:
        raise HTTPException(status_code=400)

    clients: List[org_class] = await Storage.list(org_class)
    clients_list = list()

    if org_class == HospitalModel or org_class == PharmaceuticalModel:
        for client in clients:
            emails: List[EmailAddresses] = await Storage.find(EmailAddresses, {EmailAddresses.organization_uuid: client.uuid_registry})
            email = emails[0].email
            clients_list.append({
                "name": client.name,
                "email": email,
                "phone": client.phone,
                "status": client.status,
                "registered_at": client.registered_at,
                "country": client.address_relationships.country
            })
    elif org_class == ResearcherModel:
        for client in clients:
            emails: List[EmailAddresses] = await Storage.find(EmailAddresses, {EmailAddresses.organization_uuid: client.uuid_registry})
            email = emails[0].email
            clients_list.append({
                "name": client.first_name + client.last_name,
                "email": email,
                "registered_at": client.registered_on,
                "country": client.address_relationships.country
            })
    return clients_list
