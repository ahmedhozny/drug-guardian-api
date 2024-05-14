from fastapi import APIRouter

import models
import schemes
from schemes import AccountDataCreate
from storage import db_instance

router = APIRouter()


@router.get("/accounts/")
async def get_accounts():
	clients = db_instance.filter(models.AccountDataModel).all()
	return clients


@router.post("/accounts/")
async def create_account(account_details: AccountDataCreate):
	return {"message": "Account created"}
