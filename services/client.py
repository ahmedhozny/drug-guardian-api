import asyncio
import datetime
import random
import string
import uuid
from typing import List

import jwt
from fastapi import HTTPException
from pydantic.v1 import EmailStr, EmailError

import schemas
from authentication.auth_bearer import AuthBearer
from models import HospitalModel, AddressModel, UuidRegistry, AccountDetails, AccountVerification, PharmaceuticalModel, \
    AccountTypes, AccountSecurity
from models import EmailAddresses
from models import ResearcherModel
from schemas import HealthcareSignupRequest, HealthcareSignupHandle, LoginBase
from storage import Storage
from utils.email import send_email_async


def generate_password(length=12, include_uppercase=True, include_lowercase=True, include_digits=True,
                      include_special=True):
    # Define character sets
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    special_characters = string.punctuation

    # Create a pool of characters to choose from
    characters = ''
    if include_uppercase:
        characters += uppercase_letters
    if include_lowercase:
        characters += lowercase_letters
    if include_digits:
        characters += digits
    if include_special:
        characters += special_characters

    # Ensure the password length is at least as long as the number of types of characters included
    if length < (include_uppercase + include_lowercase + include_digits + include_special):
        raise ValueError("Password length is too short for the number of character types included.")

    # Generate the password
    password = ''.join(random.choice(characters) for i in range(length))

    return password

def hospital_signup_request(request_scheme: HealthcareSignupRequest):
    hospital_model = request_scheme.model_dump()
    if hospital_model.get("organization_name").strip() == "":
        raise HTTPException(400, "Hospital Name cannot be empty")
    if asyncio.run(Storage.db_instance.count(EmailAddresses, {EmailAddresses.email: request_scheme.email})) > 0:
        raise HTTPException(400, "Email already registered")
    if asyncio.run(Storage.db_instance.count(HospitalModel, {HospitalModel.phone: request_scheme.phone})) > 0:
        raise HTTPException(400, "Phone already registered")

    address_uuid = UuidRegistry.add_uuid_entry(AddressModel).uuid
    db_address = AddressModel(uuid=address_uuid, **hospital_model["address"])
    Storage.new_object(db_address)
    hospital_uuid = UuidRegistry.add_uuid_entry(HospitalModel).uuid
    db_email = EmailAddresses(
        organization_uuid=hospital_uuid,
        email=hospital_model["email"],
    )
    Storage.new_object(db_email)
    db_hosp = HospitalModel(
        name=hospital_model["organization_name"],
        phone=hospital_model["phone"],
        address_uuid=db_address.uuid,
        status="Unconfirmed",
        uuid_registry=hospital_uuid,
    )
    Storage.new_object(db_hosp)
    return {"email": db_email.email, "organization_name": db_hosp.name}


async def hospital_signup_request_handle(handle_scheme: HealthcareSignupHandle):
    res: List[EmailAddresses] = await Storage.find(EmailAddresses, {EmailAddresses.email: handle_scheme.email})
    res_email = res[0].email
    if len(res) < 1:
        raise HTTPException(400, "No hospital registered")
    res2: List[HospitalModel] = await Storage.find(HospitalModel, {HospitalModel.uuid_registry: res[0].organization_uuid})
    hosp = res2[0]
    if not handle_scheme.confirm:
        Storage.update_object(hosp, {HospitalModel.status: "Rejected"})
        return {"email": res_email, "action": "rejected"}
    else:
        Storage.update_object(hosp, {HospitalModel.status: "Confirmed"})
        encoded_jwt = jwt.encode({"sub": res_email, "iat": datetime.datetime.utcnow()}, "SeCrEt", "HS256")
        Storage.new_object(AccountVerification(uuid_registry=hosp.uuid_registry, token=encoded_jwt))

        # await send_email_async("Drugguardian Account Registration",
        #                  res_email,
        #                  f"http://api.drugguardian.net/account/verify?token={encoded_jwt}"
        #                  )
        return {"email": res_email, "action": "accepted"}


async def verification_handling(token: str):
    res: List[AccountVerification] = await Storage.find(AccountVerification, {AccountVerification.token: token})
    if len(res) < 1:
        raise HTTPException(401, "Not a valid token")
    activation = res[0]
    if activation.used:
        raise HTTPException(403, "Account already verified")
    payload = jwt.decode(token, "SeCrEt", algorithms=["HS256"])
    email = payload.get("sub")
    check_email = await Storage.find(EmailAddresses, {EmailAddresses.email: email})
    if len(check_email) == 0:
        raise HTTPException(401, "Not a valid token")
    return {"email": email, "token": token}


async def signup_handling(handle_scheme: schemas.AccountRegister):
    res = await verification_handling(handle_scheme.token)
    if handle_scheme.email != res["email"]:
        raise HTTPException(401, "Not a valid token")
    organizations: List[EmailAddresses] = await Storage.find(EmailAddresses, {EmailAddresses.email: handle_scheme.email})
    if len(organizations) < 1:
        raise HTTPException(500, "An error has occurred.")

    organization = organizations[0]
    uuid_registries: List[UuidRegistry] = await Storage.find(UuidRegistry, {UuidRegistry.uuid: organization.organization_uuid})
    if len(uuid_registries) < 1:
        raise HTTPException(500, "An error has occurred.")
    uuid_registry = uuid_registries[0]
    switcher = {
        "hospital": HospitalModel,
        "pharmaceutical": PharmaceuticalModel,
        "researcher": ResearcherModel,
    }

    org_types: List[AccountTypes] = await Storage.find(AccountTypes, {AccountTypes.name: uuid_registry.table_name})
    org_type = org_types[0]
    account = AccountDetails(
        account_type_id=org_type.id,
        organization_uuid=uuid_registry.uuid,
        principal=handle_scheme.principal + "/" + uuid_registry.table_name[0:4],
        account_status="Active"
    )

    Storage.new_object(account)

    keytab_password = generate_password()
    Storage.new_object(AccountSecurity(
        account_id=account.id,
        keytab_password=keytab_password,
        keytab_password_expiry=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        password_hashed=AuthBearer.get_password_hash(handle_scheme.password)
    ))

    return {"keytab_password": keytab_password}

async def login_handling(auth: AuthBearer, username, password) -> schemas.TokenBase:
    exception = HTTPException(401, "Incorrect username or password", {"WWW-Authenticate": "Bearer"})
    users: List[AccountDetails]
    try:
        EmailStr.validate(username)
        emails: List[EmailAddresses] = await (Storage.find(EmailAddresses, {EmailAddresses.email: username}))
        if len(emails) == 0:
            raise exception
        email = emails[0]
        users = await Storage.find(AccountDetails, {AccountDetails.organization_uuid: email.organization_uuid})

    except EmailError:
        users = await (Storage.find(AccountDetails, {AccountDetails.principal: username}))

    if users is None or len(users) < 1:
        raise exception

    user = users[0]

    res = await auth.authenticate_user(LoginBase(account_id=user.id, email=email.email, password=password))
    return res
