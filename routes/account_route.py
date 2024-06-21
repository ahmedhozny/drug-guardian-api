from typing import List, Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import RedirectResponse

from authentication.auth_bearer import AuthBearer
from authentication.auth_kerberos import AuthKerberos
from authentication.authentication import Authentication
from models import HospitalModel, BaseModel, EmailAddresses, PharmaceuticalModel, \
    ResearcherModel
from schemas import TokenBase
from services.client import hospital_signup_request, hospital_signup_request_handle, verification_handling, \
    signup_handling, login_handling
from storage import Storage

router = APIRouter()

auth_bearer = AuthBearer()
kerberos_auth = AuthKerberos("HTTP/api.drugguardian.net@MEOW")
combined_auth = Authentication("HTTP/api.drugguardian.net@MEOW")

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


@router.post("/login", response_model=TokenBase)
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


@router.get("/protected-route")
async def protected_route(auth: dict = Depends(combined_auth)):
    return {"message": "You are authorized"}


@router.get("/protected_kerberos")
async def protected_kerberos(auth: Annotated[tuple[str, Union[bytes, None]], Depends(kerberos_auth)]):
    return {"message": "You are authorized"}
