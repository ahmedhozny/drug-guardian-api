import uuid

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from schemes.organisations import OrganisationBase


class AccountDataBase(BaseModel):
	first_name: str
	last_name: str
	email: EmailStr
	phone: str
	job_title: str
	address: str
	birthday: datetime
	gender: bool
	registered_on: datetime
	active: bool = False
	notes: Optional[str] = None
	organisation_id: int


class AccountDataCreate(AccountDataBase):
	pass


class AccountDataUpdate(AccountDataBase):
	pass


class AccountDataInDB(AccountDataBase):
	id: int

	class Config:
		orm_mode = True


class AccountData(AccountDataInDB):
	organisation: OrganisationBase
