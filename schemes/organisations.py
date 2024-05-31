from pydantic import BaseModel
from typing import Optional


class OrganisationBase(BaseModel):
	name: str
	country: str
	full_address: Optional[str] = None
	registered_at: float
	active: int


class OrganisationCreate(OrganisationBase):
	pass


class OrganisationUpdate(OrganisationBase):
	pass


class OrganisationInDB(OrganisationBase):
	id: int

	class Config:
		orm_mode = True


class Organisation(OrganisationInDB):
	pass
