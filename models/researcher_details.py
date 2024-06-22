from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Text, BINARY
from sqlalchemy.orm import relationship

from models import BaseModel, AddressModel


class ResearcherModel(BaseModel):
	__tablename__ = 'researcher'

	_id = Column(Integer, name="id", primary_key=True, autoincrement=True)
	first_name = Column(String(50), nullable=False)
	last_name = Column(String(50), nullable=False)
	phone = Column(String(32), nullable=False)
	job_title = Column(String(255), nullable=False)
	address_uuid = Column(BINARY(16), ForeignKey(AddressModel.uuid), nullable=False)
	birthday = Column(DateTime, nullable=False)
	gender = Column(Boolean, nullable=False)
	registered_on = Column(DateTime, nullable=False)
	active = Column(Boolean, nullable=False, default=False)
	notes = Column(Text, nullable=True)
	uuid_registry = Column(BINARY(16), nullable=False)

	address_relationships = relationship(AddressModel, foreign_keys=[address_uuid])
