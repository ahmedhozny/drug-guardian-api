import uuid
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Text, BINARY
from sqlalchemy.orm import relationship

from models import BaseModel
from models import OrganisationsModel
from models.uuid_registry import UuidRegistry


class AccountDataModel(BaseModel):
	__tablename__ = 'account_details'

	id = Column(Integer, primary_key=True, autoincrement=True)
	first_name = Column(String(50), nullable=False)
	last_name = Column(String(50), nullable=False)
	email = Column(String(301), nullable=False)
	phone = Column(String(32), nullable=False)
	job_title = Column(String(255), nullable=False)
	address = Column(String(255), nullable=False)
	birthday = Column(DateTime, nullable=False)
	gender = Column(Boolean, nullable=False)
	registered_on = Column(DateTime, nullable=False)
	active = Column(Boolean, nullable=False, default=False)
	notes = Column(Text, nullable=True)
	organisation_id = Column(Integer, ForeignKey(OrganisationsModel.id))
	uuid = Column(BINARY(16), ForeignKey(UuidRegistry.uuid), nullable=False, default=uuid.uuid4)

	organisation = relationship('OrganisationsModel', foreign_keys=[organisation_id])
	uuid_registry = relationship('UuidRegistry', foreign_keys=[uuid])
