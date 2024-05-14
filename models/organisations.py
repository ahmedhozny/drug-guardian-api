import uuid
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, BINARY

from models import BaseModel
from models.uuid_registry import UuidRegistry


class OrganisationsModel(BaseModel):
	__tablename__ = 'organisations'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	country = Column(String(255), nullable=False)
	full_address = Column(String(255), nullable=True)
	registered_at = Column(Float, nullable=False)
	active = Column(Integer, nullable=False)
	uuid = Column(BINARY(16), ForeignKey(UuidRegistry.uuid), nullable=False, default=uuid.uuid4)

