import uuid
from sqlalchemy import Column, BINARY, Integer
from models import BaseModel


class UuidRegistry(BaseModel):
	__tablename__ = 'uuid_registry'

	id = Column(Integer, primary_key=True, autoincrement=True)
	uuid = Column(BINARY(16), unique=True, nullable=False, default=uuid.uuid4())
