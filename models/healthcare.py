from sqlalchemy import Column, String, Text, Integer, Float

from models import BaseModel


class HealthcareModel(BaseModel):
	__tablename__ = 'healthcare_organization'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	country = Column(String(255), nullable=False)
	full_address = Column(String(255), nullable=True)
	registered_at = Column(Float, nullable=False)
	active = Column(Integer, nullable=False)
