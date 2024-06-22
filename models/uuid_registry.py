import uuid
from typing import Type, TypeVar

from sqlalchemy import Column, BINARY, Integer, String
from models import BaseModel
from storage import Storage

T = TypeVar('T', bound=BaseModel)


class UuidRegistry(BaseModel):
	__tablename__ = 'uuid_registry'

	_id = Column(Integer, name="id", primary_key=True, autoincrement=True)
	uuid = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes, unique=True, index=True)
	table_name = Column(String(16), nullable=False)

	@staticmethod
	def add_uuid_entry(table: Type[BaseModel]) -> 'UuidRegistry':
		UUID = UuidRegistry(table_name=table.__tablename__)
		Storage.new_object(UUID)
		return UUID

	@staticmethod
	def delete_uuid_entry(uuid_registry: bytes) -> None:
		UUID = Storage.find(UuidRegistry, {UuidRegistry.uuid: uuid_registry})
		Storage.remove_object(UUID)
